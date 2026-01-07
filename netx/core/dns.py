import socket
import time

from netx.core.phase_result import PhaseResult


def run_dns_phase(hostname: str) -> PhaseResult:
    start = time.perf_counter()

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM
        )
    except socket.gaierror as e:
        end = time.perf_counter()
        return PhaseResult(
            name="DNS resolution",
            duration_ms=(end - start) * 1000,
            success=False,
            error=str(e),
        )

    end = time.perf_counter()

    addresses = []
    for family, _, _, _, sockaddr in results:
        ip = sockaddr[0]
        family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
        addresses.append({
            "ip": ip,
            "family": family_name
        })

    return PhaseResult(
        name="DNS resolution",
        duration_ms=(end - start) * 1000,
        success=True,
        data={
            "hostname": hostname,
            "addresses": addresses,
        },
    )

