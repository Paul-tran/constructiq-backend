import os
import base64
import json
import re
import asyncio
from dataclasses import dataclass
from typing import List

import httpx
import fitz  # PyMuPDF
from anthropic import AsyncAnthropic
from fastapi import HTTPException

PROMPT = """You are analyzing an engineering drawing for a construction project management system.

Identify all equipment tags and assets visible in this drawing. For each asset:
1. Extract the tag number/ID (e.g. P-101, V-201, HV-301, FT-401)
2. Identify the asset type (pump, valve, vessel, heat exchanger, motor, instrument, etc.)
3. Estimate the x position as a percentage of the image WIDTH (0 = left edge, 100 = right edge)
4. Estimate the y position as a percentage of the image HEIGHT (0 = top edge, 100 = bottom edge)
5. Provide a brief description based on context in the drawing

Return ONLY a JSON array with this exact format — no other text:
[
  {
    "tag": "P-101",
    "asset_type": "Centrifugal Pump",
    "description": "Feed pump on process line 1",
    "x_percent": 45.2,
    "y_percent": 62.8
  }
]

If no equipment tags are found, return an empty array: []"""


@dataclass
class DetectedAsset:
    tag: str
    asset_type: str | None
    description: str | None
    x_percent: float
    y_percent: float


async def analyze_drawing_page(file_key: str, page_number: int, presigned_url: str) -> List[DetectedAsset]:
    """
    Download PDF from storage, convert the requested page to a PNG image,
    send to Claude Vision, and return detected assets with positions.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-anthropic-api-key":
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not configured")

    # Download PDF from presigned URL
    async with httpx.AsyncClient() as client:
        response = await client.get(presigned_url, timeout=30)
        response.raise_for_status()
        pdf_bytes = response.content

    # Convert the requested page to a PNG image using PyMuPDF
    def render_page(pdf_bytes: bytes, page_number: int) -> bytes:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if page_number < 1 or page_number > len(doc):
            raise HTTPException(status_code=400, detail=f"Page {page_number} does not exist in this document")
        page = doc[page_number - 1]
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better AI recognition
        pix = page.get_pixmap(matrix=mat)
        image_bytes = pix.tobytes("png")
        doc.close()
        return image_bytes

    image_bytes = await asyncio.to_thread(render_page, pdf_bytes, page_number)
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Call Claude Vision
    anthropic_client = AsyncAnthropic(api_key=api_key)

    message = await anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_b64,
                    },
                },
                {
                    "type": "text",
                    "text": PROMPT,
                },
            ],
        }],
    )

    raw = message.content[0].text.strip()

    # Parse JSON — handle cases where Claude adds surrounding text
    try:
        assets_data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        assets_data = json.loads(match.group()) if match else []

    return [
        DetectedAsset(
            tag=a.get("tag", "UNKNOWN"),
            asset_type=a.get("asset_type"),
            description=a.get("description"),
            x_percent=min(max(float(a.get("x_percent", 50.0)), 0), 100),
            y_percent=min(max(float(a.get("y_percent", 50.0)), 0), 100),
        )
        for a in assets_data
        if isinstance(a, dict) and a.get("tag")
    ]
