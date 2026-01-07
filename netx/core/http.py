import time
import http.client

from netx.core.phase_result import PhaseResult


def run_http_phase(
    scheme: str,
    hostname: str,
    port: int,
    path: str,
    timeout: float = 5.0
) -> PhaseResult:
    start = time.perf_counter()

    try:
        if scheme == "https":
            conn = http.client.HTTPSConnection(
                hostname,
                port=port,
                timeout=timeout
            )
        else:
            conn = http.client.HTTPConnection(
                hostname,
                port=port,
                timeout=timeout
            )

        # Send request
        conn.request("GET", path or "/")

        # Measure TTFB
        response = conn.getresponse()
        ttfb = (time.perf_counter() - start) * 1000

        # Read response body fully
        body = response.read()
        end = time.perf_counter()

    except Exception as e:
        end = time.perf_counter()
        return PhaseResult(
            name="HTTP request",
            duration_ms=(end - start) * 1000,
            success=False,
            error=str(e),
        )
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return PhaseResult(
        name="HTTP request",
        duration_ms=(end - start) * 1000,
        success=True,
        data={
            "status": response.status,
            "reason": response.reason,
            "ttfb_ms": ttfb,
            "response_bytes": len(body),
        },
    )
