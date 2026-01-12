from typing import List
from netx.core.models import RequestContext, PhaseResult
from netx.phases.base import Phase
from netx.phases.url_parse import URLParsePhase
from netx.phases.dns import DNSResolutionPhase
from netx.phases.tcp import TCPConnectPhase
from netx.phases.tls import TLSHandshakePhase
from netx.phases.http import HTTPRequestPhase


class ExecutionEngine:
    """
    Orchestrates the execution of network phases in a pipeline.
    """

    def __init__(self, url: str, timeout: float = 5.0, retries: int = 3, pipeline: List[Phase] = None):
        self.context = RequestContext(url=url, timeout=timeout, retries=retries)
        self.pipeline: List[Phase] = pipeline or [
            URLParsePhase(),
            DNSResolutionPhase(),
            TCPConnectPhase(),
            TLSHandshakePhase(),
            HTTPRequestPhase()
        ]
        self.results: List[PhaseResult] = []

    def run(self) -> List[PhaseResult]:
        """
        Executes the pipeline sequentially.
        Stops on the first failure.
        """
        try:
            for phase in self.pipeline:
                result = phase.execute(self.context)
                self.results.append(result)
                
                if not result.success:
                    break
                    
            return self.results
        finally:
            self.context.cleanup()

    @property
    def total_duration_ms(self) -> float:
        return sum(r.duration_ms for r in self.results)

    @property
    def is_success(self) -> bool:
        return all(r.success for r in self.results) if self.results else False
