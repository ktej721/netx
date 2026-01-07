import ssl
import time
import socket

from netx.core.phase_result import PhaseResult


def run_tls_phase(
    tcp_ip: str,
    tcp_port: int,
    family: str,
    hostname: str,
    timeout: float = 5.0
) -> PhaseResult:
    start = time.perf_counter()

    # Select socket family
    if family == "IPv6":
        sock_family = socket.AF_INET6
        address = (tcp_ip, tcp_port, 0, 0)
    else:
        sock_family = socket.AF_INET
        address = (tcp_ip, tcp_port)

    raw_sock = socket.socket(sock_family, socket.SOCK_STREAM)
    raw_sock.settimeout(timeout)

    try:
        raw_sock.connect(address)
    except Exception as e:
        end = time.perf_counter()
        return PhaseResult(
            name="TLS handshake",
            duration_ms=(end - start) * 1000,
            success=False,
            error=f"TCP reconnect failed for TLS: {e}",
        )

    # Create SSL context (secure defaults)
    context = ssl.create_default_context()

    try:
        tls_sock = context.wrap_socket(
            raw_sock,
            server_hostname=hostname  # CRITICAL
        )
    except ssl.SSLError as e:
        end = time.perf_counter()
        raw_sock.close()
        return PhaseResult(
            name="TLS handshake",
            duration_ms=(end - start) * 1000,
            success=False,
            error=f"TLS error: {e}",
        )

    end = time.perf_counter()

    # Extract TLS metadata
    tls_version = tls_sock.version()
    cipher = tls_sock.cipher()

    tls_sock.close()

    return PhaseResult(
        name="TLS handshake",
        duration_ms=(end - start) * 1000,
        success=True,
        data={
            "tls_version": tls_version,
            "cipher": cipher[0] if cipher else None,
        },
    )
