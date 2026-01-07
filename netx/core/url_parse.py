from urllib.parse import urlparse

#yeah had to use a lib for this one
def parse_url(url: str):
    parsed_url = urlparse(url)
    # basic validation
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
    # validating hostname
    if not parsed_url.hostname:
        raise ValueError("URL must include a hostname")

    port = parsed_url.port
    if port is None:
        port = 443 if parsed_url.scheme == "https" else 80
    #dict return for easy access
    return {
        "scheme": parsed_url.scheme,
        "host": parsed_url.hostname,
        "port": port,
        "path": parsed_url.path or "/",
        "query": parsed_url.query,
    }