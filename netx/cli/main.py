import argparse
import sys
import json
from typing import List

from netx.core.engine import ExecutionEngine
from netx.core.models import (
    PhaseResult,
    URLParseResult,
    DNSResolutionResult,
    TCPConnectResult,
    TLSHandshakeResult,
    HTTPRequestResult,
)


def print_banner(url: str):
    print("▶ Network Explorer — v1.0 (Production Refactor)")
    print(f"▶ Target: {url}\n")


def print_result(result: PhaseResult):
    symbol = "✓" if result.success else "✗"
    print(f"{symbol} {result.name}  {result.duration_ms:.2f} ms")
    
    if not result.success:
        print(f"  Error: {result.error}")
        return

    data = result.data
    if isinstance(data, URLParseResult):
        print(f"  scheme: {data.scheme}")
        print(f"  host: {data.host}")
        print(f"  port: {data.port}")
        print(f"  path: {data.path}")
    
    elif isinstance(data, DNSResolutionResult):
        for addr in data.addresses:
            print(f"  {addr.family}: {addr.ip}")
            
    elif isinstance(data, TCPConnectResult):
        print(f"  Connected to: {data.ip}:{data.port} ({data.family})")
        
    elif isinstance(data, TLSHandshakeResult):
        if data.skipped:
            print(f"  Skipped: {data.reason}")
        else:
            print(f"  Version: {data.tls_version}")
            print(f"  Cipher: {data.cipher}")
            print(f"  SNI: {data.sni}")
            
    elif isinstance(data, HTTPRequestResult):
        print(f"  Status: {data.status_code} {data.reason}")
        print(f"  Protocol: {data.proto}")
        print(f"  Bytes Received: {data.bytes_received}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="netx",
        description="Network Explorer — production-grade network diagnostics"
    )

    subparsers = parser.add_subparsers(dest="command")

    explain_parser = subparsers.add_parser(
        "explain",
        help="Explain a network request step by step"
    )
    explain_parser.add_argument(
        "url",
        help="Target URL to analyze (e.g., https://google.com)"
    )
    explain_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    explain_parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout for each network phase (default: 5.0s)"
    )
    explain_parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for transient failures (default: 3)"
    )

    args = parser.parse_args()

    if args.command != "explain":
        parser.print_help()
        sys.exit(0)

    engine = ExecutionEngine(
        url=args.url,
        timeout=args.timeout,
        retries=args.retries
    )

    if not args.json:
        print_banner(args.url)

    results = engine.run()

    if args.json:
        # For JSON output, we still need to handle the dataclasses
        def default_serializer(o):
            if hasattr(o, '__dict__'):
                return o.__dict__
            return str(o)

        output = {
            "target": args.url,
            "success": engine.is_success,
            "total_duration_ms": engine.total_duration_ms,
            "phases": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "data": r.data,
                    "error": r.error
                } for r in results
            ]
        }
        print(json.dumps(output, indent=2, default=default_serializer))
    else:
        for r in results:
            print_result(r)
        
        if engine.is_success:
            print(f"✔ Completed successfully in {engine.total_duration_ms:.2f} ms")
        else:
            print(f"✘ Pipeline failed at {results[-1].name}")
            sys.exit(1)


if __name__ == "__main__":
    main()