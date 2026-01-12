from urllib.parse import urlparse
from netx.phases.base import Phase
from netx.core.models import RequestContext, URLParseResult # Added URLParseResult
from netx.core.exceptions import URLParseError


class URLParsePhase(Phase):
    name = "URL Parsing"

    def run(self, context: RequestContext) -> URLParseResult: # Changed return type
        try:
            parsed = urlparse(context.url)
            
            # Default scheme
            if not parsed.scheme:
                 # If user didn't provide scheme, maybe we can assume https or throw? 
                 # Let's enforce scheme presence or default to https if missing but that might be ambiguous.
                 # The prompt says "malformed URL handling".
                 pass

            if parsed.scheme not in ("http", "https"):
                raise URLParseError(f"Unsupported scheme: '{parsed.scheme}'. Only 'http' and 'https' are supported.")

            if not parsed.hostname:
                raise URLParseError("Invalid URL: Hostname is missing.")

            context.scheme = parsed.scheme
            context.host = parsed.hostname
            context.path = parsed.path if parsed.path else "/"
            context.query = parsed.query

            # Port determination
            if parsed.port:
                context.port = parsed.port
            else:
                context.port = 443 if context.scheme == "https" else 80

            return URLParseResult( # Changed to return URLParseResult
                scheme=context.scheme,
                host=context.host,
                port=context.port,
                path=context.path,
                query=context.query
            )

        except ValueError as e:
            raise URLParseError(f"Malformed URL: {str(e)}")
