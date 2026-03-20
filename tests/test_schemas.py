"""
Schema unit tests — no database required.
"""
import pytest
from pydantic import ValidationError

from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.document import DocumentUpdate
from app.schemas.commissioning import CommissioningRecordUpdate, PunchItemCreate


# ── Asset ─────────────────────────────────────────────────────────────────────

def test_asset_tag_is_uppercased():
    a = AssetCreate(project_id=1, tag="pump-001", site_id=1)
    assert a.tag == "PUMP-001"


def test_asset_tag_cannot_be_empty():
    with pytest.raises(ValidationError):
        AssetCreate(project_id=1, tag="   ", site_id=1)


def test_asset_status_defaults_to_active():
    a = AssetCreate(project_id=1, tag="V-100", site_id=1)
    assert a.status == "active"


def test_asset_rejects_invalid_status():
    with pytest.raises(ValidationError):
        AssetUpdate(status="broken")


def test_asset_accepts_valid_statuses():
    for status in ("active", "inactive", "maintenance"):
        a = AssetUpdate(status=status)
        assert a.status == status


# ── Document ──────────────────────────────────────────────────────────────────

def test_document_rejects_invalid_status():
    with pytest.raises(ValidationError):
        DocumentUpdate(status="pending")


def test_document_accepts_valid_statuses():
    for status in ("draft", "under_review", "approved", "superseded"):
        d = DocumentUpdate(status=status)
        assert d.status == status


# ── Commissioning ─────────────────────────────────────────────────────────────

def test_commissioning_rejects_invalid_status():
    with pytest.raises(ValidationError):
        CommissioningRecordUpdate(overall_status="unknown")


def test_punch_item_rejects_invalid_severity():
    with pytest.raises(ValidationError):
        PunchItemCreate(
            commissioning_record_id=1,
            description="Something is wrong",
            severity="blocker",  # not valid
            raised_by="user_abc",
        )


def test_punch_item_accepts_valid_severities():
    for sev in ("critical", "major", "minor"):
        p = PunchItemCreate(
            commissioning_record_id=1,
            description="Issue",
            severity=sev,
            raised_by="user_abc",
        )
        assert p.severity == sev
