from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PhaseResult:
    name: str
    duration_ms: float
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

