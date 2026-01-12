from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import socket


@dataclass
class URLParseResult:
    scheme: str
    host: str
    port: int
    path: str
    query: str


@dataclass
class DNSAddress:
    ip: str
    family: str


@dataclass
class DNSResolutionResult:
    addresses: List[DNSAddress]
    count: int


@dataclass
class TCPConnectResult:
    ip: str
    port: int
    family: str


@dataclass
class TLSHandshakeResult:
    tls_version: Optional[str] = None
    cipher: Optional[str] = None
    sni: Optional[str] = None
    skipped: bool = False
    reason: Optional[str] = None


@dataclass
class HTTPRequestResult:
    status_code: int
    reason: str
    proto: str
    bytes_received: int


PhaseData = Union[
    URLParseResult,
    DNSResolutionResult,
    TCPConnectResult,
    TLSHandshakeResult,
    HTTPRequestResult,
    Dict[str, Any]
]


@dataclass
class PhaseResult:
    """Result of a single execution phase."""
    name: str
    duration_ms: float
    success: bool
    data: PhaseData = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class HostAddress:
    """Represents a resolved IP address."""
    ip: str
    family: socket.AddressFamily

    @property
    def family_str(self) -> str:
        return "IPv6" if self.family == socket.AF_INET6 else "IPv4"


@dataclass
class RequestContext:
    """
    Shared context passed through the pipeline.
    Holds state, accumulated results, and shared resources (socket).
    """
    url: str
    scheme: str = ""
    host: str = ""
    port: int = 0
    path: str = ""
    query: str = ""

    # DNS State
    resolved_addresses: List[HostAddress] = field(default_factory=list)
    selected_address: Optional[HostAddress] = None

    # Connection State
    sock: Optional[socket.socket] = None
    cipher: Optional[str] = None
    tls_version: Optional[str] = None

    # HTTP State
    http_version: str = "HTTP/1.1"

    # Configuration
    timeout: float = 5.0
    retries: int = 3
    user_agent: str = "netx/1.0"

    def cleanup(self):
        """Safely close the socket if it exists."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
