import argparse
import sys

from netx.core.url_parse import parse_url
from netx.core.phase_result import PhaseResult
from netx.core.dns import run_dns_phase
from netx.core.tcp import run_tcp_phase
from netx.core.tls import run_tls_phase
from netx.core.http import run_http_phase
import time


def run_url_parsing_phase(url: str) -> PhaseResult:
    start = time.perf_counter()

    try:
        data = parse_url(url)
    except ValueError as e:
        end = time.perf_counter()
        return PhaseResult(
            name="URL parsing",
            duration_ms=(end - start) * 1000,
            success=False,
            error=str(e),
        )

    end = time.perf_counter()
    return PhaseResult(
        name="URL parsing",
        duration_ms=(end - start) * 1000,
        success=True,
        data=data,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="netx",
        description="Network Explorer — explain what happens during a network request"
    )

    subparsers = parser.add_subparsers(dest="command")

    explain_parser = subparsers.add_parser(
        "explain",
        help="Explain a network request step by step"
    )
    explain_parser.add_argument(
        "url",
        help="Target URL to analyze"
    )

    args = parser.parse_args()

    if args.command != "explain":
        parser.print_help()
        sys.exit(1)

    # Header
    print("▶ Network Explorer — v0.1")
    print(f"▶ Target: {args.url}\n")

    # ---- URL Parsing Phase ----
    url_result = run_url_parsing_phase(args.url)

    if not url_result.success:
        print(f"✗ {url_result.name}  {url_result.duration_ms:.2f} ms")
        print(f"  Reason: {url_result.error}")
        sys.exit(1)

    print(f"✓ {url_result.name}  {url_result.duration_ms:.2f} ms")
    for key, value in url_result.data.items():
        print(f"  {key}: {value}")
    print()

    # ---- DNS Resolution Phase ----
    dns_result = run_dns_phase(url_result.data["host"])

    if not dns_result.success:
        print(f"✗ {dns_result.name}  {dns_result.duration_ms:.2f} ms")
        print(f"  Reason: {dns_result.error}")
        sys.exit(1)

    print(f"✓ {dns_result.name}  {dns_result.duration_ms:.2f} ms")
    for addr in dns_result.data["addresses"]:
        print(f"  {addr['family']}: {addr['ip']}")
    print()

    # ---- TCP Connection Phase ----
    addr = dns_result.data["addresses"][0]

    tcp_result = run_tcp_phase(
        addr["ip"],
        url_result.data["port"],
        addr["family"]
    )

    if not tcp_result.success:
        print(f"✗ {tcp_result.name}  {tcp_result.duration_ms:.2f} ms")
        print(f"  Reason: {tcp_result.error}")
        sys.exit(1)

    print(f"✓ {tcp_result.name}  {tcp_result.duration_ms:.2f} ms")
    print(f"  ip: {tcp_result.data['ip']}")
    print(f"  port: {tcp_result.data['port']}")
    print()

    # ---- TLS Handshake Phase ----
    tls_result = run_tls_phase(
    tcp_ip=tcp_result.data["ip"],
    tcp_port=tcp_result.data["port"],
    family=tcp_result.data["family"],
    hostname=url_result.data["host"],
    )

    if not tls_result.success:
        print(f"✗ {tls_result.name}  {tls_result.duration_ms:.2f} ms")
        print(f"  Reason: {tls_result.error}")
        sys.exit(1)

    print(f"✓ {tls_result.name}  {tls_result.duration_ms:.2f} ms")
    print(f"  TLS version: {tls_result.data['tls_version']}")
    print(f"  Cipher: {tls_result.data['cipher']}")
    print()

    # ---- HTTP Request Phase ----
    http_result = run_http_phase(
        scheme=url_result.data["scheme"],
        hostname=url_result.data["host"],
        port=url_result.data["port"],
        path=url_result.data["path"],
    )

    if not http_result.success:
        print(f"✗ {http_result.name}  {http_result.duration_ms:.2f} ms")
        print(f"  Reason: {http_result.error}")
        sys.exit(1)

    print(f"✓ {http_result.name}  {http_result.duration_ms:.2f} ms")
    print(f"  Status: {http_result.data['status']} {http_result.data['reason']}")
    print(f"  TTFB: {http_result.data['ttfb_ms']:.2f} ms")
    print(f"  Response size: {http_result.data['response_bytes']} bytes")
    print()

if __name__ == "__main__":
    main()
