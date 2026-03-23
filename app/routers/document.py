from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from app.core.limiter import limiter

from app.models.document import Document, DocumentRevision, DocumentApproval, DocumentComment, DrawingAsset
from app.models.asset import Asset
from app.models.geography import Site, Location, Unit, Partition
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentOut,
    DocumentRevisionCreate, DocumentRevisionOut,
    DocumentApprovalCreate, DocumentApprovalOut,
    DocumentCommentCreate, DocumentCommentOut,
    DrawingAssetCreate, DrawingAssetUpdate, DrawingAssetOut,
)
from app.core.auth import get_current_user
from app.models.user import User
from app.services.storage import get_presigned_url
from app.services.ai import analyze_drawing_page

router = APIRouter(tags=["Documents"])


async def _build_document_out(doc: Document) -> DocumentOut:
    out = DocumentOut.model_validate(doc, from_attributes=True)
    if doc.site_id:
        site = await Site.get_or_none(id=doc.site_id)
        out.site_name = site.name if site else None
    if doc.location_id:
        loc = await Location.get_or_none(id=doc.location_id)
        out.location_name = loc.name if loc else None
    if doc.unit_id:
        unit = await Unit.get_or_none(id=doc.unit_id)
        out.unit_name = unit.name if unit else None
    if doc.partition_id:
        part = await Partition.get_or_none(id=doc.partition_id)
        out.partition_name = part.name if part else None
    return out


# --- Documents ---

@router.get("/projects/{project_id}/documents", response_model=List[DocumentOut])
async def list_documents(project_id: int):
    docs = await Document.filter(project_id=project_id)
    return [await _build_document_out(d) for d in docs]


@router.post("/projects/{project_id}/documents", response_model=DocumentOut, status_code=201)
async def create_document(project_id: int, data: DocumentCreate):
    doc = await Document.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return await _build_document_out(doc)


@router.get("/documents/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: int):
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return await _build_document_out(doc)


@router.patch("/documents/{doc_id}", response_model=DocumentOut)
async def update_document(doc_id: int, data: DocumentUpdate):
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.update_from_dict(data.model_dump(exclude_none=True)).save()
    return await _build_document_out(doc)


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: int):
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.delete()


# --- Document Revisions ---

@router.get("/documents/{doc_id}/revisions", response_model=List[DocumentRevisionOut])
async def list_revisions(doc_id: int):
    return await DocumentRevision.filter(document_id=doc_id)


@router.post("/documents/{doc_id}/revisions", response_model=DocumentRevisionOut, status_code=201)
async def create_revision(doc_id: int, data: DocumentRevisionCreate):
    revision = await DocumentRevision.create(document_id=doc_id, **data.model_dump(exclude={"document_id"}))
    return revision


@router.get("/revisions/{revision_id}", response_model=DocumentRevisionOut)
async def get_revision(revision_id: int):
    revision = await DocumentRevision.get_or_none(id=revision_id)
    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")
    return revision


# --- Document Approvals ---

@router.get("/documents/{doc_id}/approvals", response_model=List[DocumentApprovalOut])
async def list_approvals(doc_id: int):
    return await DocumentApproval.filter(document_id=doc_id)


@router.post("/documents/{doc_id}/approvals", response_model=DocumentApprovalOut, status_code=201)
async def create_approval(doc_id: int, data: DocumentApprovalCreate):
    approval = await DocumentApproval.create(document_id=doc_id, **data.model_dump(exclude={"document_id"}))
    return approval


# --- Document Comments ---

@router.get("/documents/{doc_id}/comments", response_model=List[DocumentCommentOut])
async def list_comments(doc_id: int):
    return await DocumentComment.filter(document_id=doc_id)


@router.post("/documents/{doc_id}/comments", response_model=DocumentCommentOut, status_code=201)
async def create_comment(doc_id: int, data: DocumentCommentCreate):
    comment = await DocumentComment.create(document_id=doc_id, **data.model_dump(exclude={"document_id"}))
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    comment = await DocumentComment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    await comment.delete()


# --- Drawing Asset Pins ---

async def _enrich_pin(pin: DrawingAsset) -> DrawingAssetOut:
    out = DrawingAssetOut.model_validate(pin, from_attributes=True)
    if pin.asset_id:
        asset = await Asset.get_or_none(id=pin.asset_id)
        if asset:
            out.location_id = asset.location_id
            out.unit_id = asset.unit_id
            if asset.location_id:
                loc = await Location.get_or_none(id=asset.location_id)
                out.location_name = loc.name if loc else None
            if asset.unit_id:
                unit = await Unit.get_or_none(id=asset.unit_id)
                out.unit_name = unit.name if unit else None
    return out


@router.get("/documents/{doc_id}/pins", response_model=List[DrawingAssetOut])
async def list_pins(doc_id: int):
    pins = await DrawingAsset.filter(document_id=doc_id)
    return [await _enrich_pin(p) for p in pins]


@router.post("/documents/{doc_id}/pins", response_model=DrawingAssetOut, status_code=201)
async def create_pin(doc_id: int, data: DrawingAssetCreate):
    pin = await DrawingAsset.create(document_id=doc_id, **data.model_dump(exclude={"document_id"}))
    return pin


@router.get("/pins/{pin_id}", response_model=DrawingAssetOut)
async def get_pin(pin_id: int):
    pin = await DrawingAsset.get_or_none(id=pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    return pin


@router.patch("/pins/{pin_id}", response_model=DrawingAssetOut)
async def update_pin(pin_id: int, data: DrawingAssetUpdate):
    pin = await DrawingAsset.get_or_none(id=pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    await pin.update_from_dict(data.model_dump(exclude_none=True)).save()
    return pin


@router.delete("/pins/{pin_id}", status_code=204)
async def delete_pin(pin_id: int):
    pin = await DrawingAsset.get_or_none(id=pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    await pin.delete()


# --- Drawing Intelligence ---

@router.post("/documents/{doc_id}/analyze", response_model=List[DrawingAssetOut])
@limiter.limit("10/minute")
async def analyze_document(
    request: Request,
    doc_id: int,
    page: int = 1,
    current_user: User = Depends(get_current_user),
):
    """
    Run Claude Vision on a specific page of a document.
    Clears any existing pending pins for that page first, then saves new ones.
    Document must have status 'approved'.
    """
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "approved":
        raise HTTPException(status_code=400, detail="Document must be approved before AI analysis")

    revision = await DocumentRevision.filter(document_id=doc_id).order_by("-created_at").first()
    if not revision:
        raise HTTPException(status_code=400, detail="No file revision found for this document")

    # Clear existing pending pins for this page so re-analysis doesn't duplicate
    await DrawingAsset.filter(document_id=doc_id, page_number=page, status="pending").delete()

    presigned_url = get_presigned_url(revision.file_key)
    detected = await analyze_drawing_page(revision.file_key, page, presigned_url)

    pins = []
    for asset in detected:
        pin = await DrawingAsset.create(
            document_id=doc_id,
            revision_id=revision.id,
            tag=asset.tag,
            asset_type=asset.asset_type,
            description=asset.description,
            x_percent=asset.x_percent,
            y_percent=asset.y_percent,
            page_number=page,
            status="pending",
        )
        pins.append(pin)

    return pins


@router.post("/pins/{pin_id}/confirm", response_model=DrawingAssetOut)
async def confirm_pin(
    pin_id: int,
    project_id: int,
    site_id: int,
    location_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    partition_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    subgroup_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Confirm a detected pin: creates an Asset record and links it to the pin.
    If an asset with the same tag already exists in the project, links to that instead.
    """
    pin = await DrawingAsset.get_or_none(id=pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    # Re-use existing asset if tag already exists in this project at this location
    existing = await Asset.get_or_none(
        project_id=project_id, tag=pin.tag, site_id=site_id,
        location_id=location_id, unit_id=unit_id, partition_id=partition_id,
    )
    if existing:
        asset = existing
    else:
        asset = await Asset.create(
            project_id=project_id,
            tag=pin.tag,
            name=pin.tag,
            type=pin.asset_type,
            description=pin.description,
            site_id=site_id,
            location_id=location_id,
            unit_id=unit_id,
            partition_id=partition_id,
            parent_id=parent_id,
            subgroup_id=subgroup_id,
        )

    pin.asset_id = asset.id
    pin.status = "confirmed"
    await pin.save()
    return pin
