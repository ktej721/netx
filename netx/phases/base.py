from abc import ABC, abstractmethod
import time
from typing import Optional

from netx.core.models import RequestContext, PhaseResult
from netx.core.exceptions import PhaseError


class Phase(ABC):
    """Abstract base class for all network phases."""

    name: str = "Base Phase"

    def execute(self, context: RequestContext) -> PhaseResult:
        """
        Wraps the abstract run method with timing and error handling.
        """
        start_time = time.perf_counter()
        last_error: Optional[Exception] = None

        for attempt in range(context.retries + 1):
            try:
                data = self.run(context)
                duration_ms = (time.perf_counter() - start_time) * 1000
                return PhaseResult(
                    name=self.name,
                    duration_ms=duration_ms,
                    success=True,
                    data=data if data else {}
                )
            except PhaseError as e:
                last_error = e
                if attempt < context.retries:
                    time.sleep(0.5)  # Backoff delay
                continue
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                return PhaseResult(
                    name=self.name,
                    duration_ms=duration_ms,
                    success=False,
                    error=f"Unexpected error: {str(e)}"
                )

        duration_ms = (time.perf_counter() - start_time) * 1000
        return PhaseResult(
            name=self.name,
            duration_ms=duration_ms,
            success=False,
            error=str(last_error)
        )

    @abstractmethod
    def run(self, context: RequestContext) -> dict:
        """
        Core logic for the phase.
        Must return a dictionary of data to include in the result.
        Must raise PhaseError on failure.
        """
        pass
