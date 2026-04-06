from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class Stage(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


STAGE_ORDER = [Stage.APPLIED, Stage.INTERVIEW, Stage.OFFER, Stage.HIRED]

STAGE_LABELS = {
    Stage.APPLIED: "Applied",
    Stage.INTERVIEW: "Interview",
    Stage.OFFER: "Offer",
    Stage.HIRED: "Hired",
    Stage.REJECTED: "Rejected",
}

STAGE_COLORS = {
    Stage.APPLIED: "#6B7280",
    Stage.INTERVIEW: "#F59E0B",
    Stage.OFFER: "#3B82F6",
    Stage.HIRED: "#10B981",
    Stage.REJECTED: "#EF4444",
}


@dataclass
class Candidate:
    name: str
    role: str
    stage: Stage
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "role": self.role, "stage": self.stage.value}

    @classmethod
    def from_dict(cls, d: dict) -> "Candidate":
        return cls(id=d["id"], name=d["name"], role=d["role"], stage=Stage(d["stage"]))

    def next_stage(self) -> "Stage | None":
        try:
            idx = STAGE_ORDER.index(self.stage)
            if idx + 1 < len(STAGE_ORDER):
                return STAGE_ORDER[idx + 1]
        except ValueError:
            pass
        return None
