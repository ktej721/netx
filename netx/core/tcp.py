import socket
import time

from netx.core.phase_result import PhaseResult


def run_tcp_phase(ip: str, port: int, family: str, timeout: float = 5.0) -> PhaseResult:
    start = time.perf_counter()

    if family == "IPv6":
        sock_family = socket.AF_INET6
        address = (ip, port, 0, 0)
    else:
        sock_family = socket.AF_INET
        address = (ip, port)

    sock = socket.socket(sock_family, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect(address)
    except socket.timeout:
        end = time.perf_counter()
        return PhaseResult(
            name="TCP connect",
            duration_ms=(end - start) * 1000,
            success=False,
            error=f"Connection timed out after {timeout}s",
        )
    except ConnectionRefusedError:
        end = time.perf_counter()
        return PhaseResult(
            name="TCP connect",
            duration_ms=(end - start) * 1000,
            success=False,
            error="Connection refused (port closed)",
        )
    except OSError as e:
        end = time.perf_counter()
        return PhaseResult(
            name="TCP connect",
            duration_ms=(end - start) * 1000,
            success=False,
            error=str(e),
        )

    end = time.perf_counter()
    sock.close()

    return PhaseResult(
        name="TCP connect",
        duration_ms=(end - start) * 1000,
        success=True,
        data={
            "ip": ip,
            "port": port,
            "family": family,
        },
    )
