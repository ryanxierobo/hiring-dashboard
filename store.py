import json
import os
from models import Candidate

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "candidates.json")


def load_candidates() -> list[Candidate]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return [Candidate.from_dict(d) for d in json.load(f)]


def save_candidates(candidates: list[Candidate]) -> None:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump([c.to_dict() for c in candidates], f, indent=2)


def add_candidate(candidates: list[Candidate], name: str, role: str) -> Candidate:
    from models import Stage
    c = Candidate(name=name, role=role, stage=Stage.APPLIED)
    candidates.append(c)
    save_candidates(candidates)
    return c


def update_candidate_stage(candidates: list[Candidate], candidate_id: str, stage) -> None:
    for c in candidates:
        if c.id == candidate_id:
            c.stage = stage
            break
    save_candidates(candidates)


def delete_candidate(candidates: list[Candidate], candidate_id: str) -> None:
    candidates[:] = [c for c in candidates if c.id != candidate_id]
    save_candidates(candidates)
