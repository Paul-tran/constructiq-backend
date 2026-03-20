from fastapi import APIRouter, HTTPException
from typing import List

from app.models.document import Document, DocumentRevision, DocumentApproval, DocumentComment, DrawingAsset
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentOut,
    DocumentRevisionCreate, DocumentRevisionOut,
    DocumentApprovalCreate, DocumentApprovalOut,
    DocumentCommentCreate, DocumentCommentOut,
    DrawingAssetCreate, DrawingAssetUpdate, DrawingAssetOut,
)

router = APIRouter(tags=["Documents"])


# --- Documents ---

@router.get("/projects/{project_id}/documents", response_model=List[DocumentOut])
async def list_documents(project_id: int):
    return await Document.filter(project_id=project_id)


@router.post("/projects/{project_id}/documents", response_model=DocumentOut, status_code=201)
async def create_document(project_id: int, data: DocumentCreate):
    doc = await Document.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return doc


@router.get("/documents/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: int):
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/documents/{doc_id}", response_model=DocumentOut)
async def update_document(doc_id: int, data: DocumentUpdate):
    doc = await Document.get_or_none(id=doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.update_from_dict(data.model_dump(exclude_none=True)).save()
    return doc


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

@router.get("/documents/{doc_id}/pins", response_model=List[DrawingAssetOut])
async def list_pins(doc_id: int):
    return await DrawingAsset.filter(document_id=doc_id)


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
