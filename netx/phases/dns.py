import socket
from typing import List, Dict

from netx.phases.base import Phase
from netx.core.models import RequestContext, HostAddress, DNSResolutionResult, DNSAddress # Added DNSResolutionResult, DNSAddress
from netx.core.exceptions import DNSResolutionError


class DNSResolutionPhase(Phase):
    name = "DNS Resolution"

    def run(self, context: RequestContext) -> DNSResolutionResult: # Changed return type
        if not context.host:
             raise DNSResolutionError("Cannot resolve DNS: Hostname not found in context.")

        try:
            # We request both IPv4 and IPv6
            # socket.AI_ADDRCONFIG might be useful but sometimes filters too aggressively on some systems
            # We want to see what's available.
            addr_infos = socket.getaddrinfo(
                context.host,
                context.port,
                family=socket.AF_UNSPEC,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )
        except socket.gaierror as e:
            raise DNSResolutionError(f"DNS lookup failed for {context.host}", original_error=e)
        except Exception as e:
             raise DNSResolutionError(f"Unexpected DNS error: {e}", original_error=e)

        unique_addresses = []
        seen_ips = set()

        # Prioritize IPv6 if available, or just list them all
        # The prompt mentions "Retry and fallback logic (IPv6 -> IPv4)"
        # We will collect all, and the TCP phase can try them in order.
        # For display, we show them.

        for family, socktype, proto, canonname, sockaddr in addr_infos:
            ip = sockaddr[0]
            if ip in seen_ips:
                continue
            seen_ips.add(ip)
            
            # Filter for IPv4/IPv6 only
            if family == socket.AF_INET6:
                 unique_addresses.append(HostAddress(ip=ip, family=family))
            elif family == socket.AF_INET:
                 unique_addresses.append(HostAddress(ip=ip, family=family))

        if not unique_addresses:
            raise DNSResolutionError(f"No A or AAAA records found for {context.host}")

        # Sort: IPv6 first by default (Happy Eyeballs-ish preparation)
        # In a real impl we might race them, but here we just prepare the list.
        unique_addresses.sort(key=lambda x: x.family == socket.AF_INET, reverse=False) # False means IPv6 (23/10/30) vs IPv4 (2) - actually AF_INET is 2, AF_INET6 is 10/23/30. 
        # Actually AF_INET=2, AF_INET6=30 (on mac) or 10.
        # Let's just explicit sort.
        unique_addresses.sort(key=lambda x: 0 if x.family == socket.AF_INET6 else 1)

        context.resolved_addresses = unique_addresses
        
        # Serialization for result
        display_addresses = [
            DNSAddress(ip=addr.ip, family=addr.family_str) # Changed to DNSAddress
            for addr in unique_addresses
        ]

        return DNSResolutionResult( # Changed to return DNSResolutionResult
            addresses=display_addresses,
            count=len(display_addresses)
        )
