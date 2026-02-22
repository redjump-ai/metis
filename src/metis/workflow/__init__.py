"""Workflow state machine for content lifecycle."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class ContentStatus(str, Enum):
    PENDING = "pending"
    EXTRACTED = "extracted"
    READ = "read"
    VALUABLE = "valuable"
    ARCHIVED = "archived"
    CREATING = "creating"
    KNOWLEDGE_BASE = "knowledge_base"


@dataclass
class ContentRecord:
    url: str
    title: str
    platform: str
    status: ContentStatus
    created_at: datetime
    extracted_at: datetime | None = None
    read_at: datetime | None = None
    file_path: Path | None = None
    is_english: bool = False
    has_translation: bool = False


VALID_TRANSITIONS = {
    ContentStatus.PENDING: [ContentStatus.EXTRACTED],
    ContentStatus.EXTRACTED: [ContentStatus.READ],
    ContentStatus.READ: [ContentStatus.VALUABLE, ContentStatus.ARCHIVED],
    ContentStatus.VALUABLE: [ContentStatus.CREATING, ContentStatus.KNOWLEDGE_BASE],
    ContentStatus.ARCHIVED: [],
    ContentStatus.CREATING: [],
    ContentStatus.KNOWLEDGE_BASE: [],
}


def can_transition(current: ContentStatus, target: ContentStatus) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])


def transition_record(record: ContentRecord, new_status: ContentStatus) -> ContentRecord:
    if not can_transition(record.status, new_status):
        raise ValueError(f"Invalid transition from {record.status} to {new_status}")

    now = datetime.now()
    if new_status == ContentStatus.EXTRACTED:
        record.extracted_at = now
    elif new_status == ContentStatus.READ:
        record.read_at = now

    record.status = new_status
    return record
