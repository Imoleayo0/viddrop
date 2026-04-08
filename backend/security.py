# ================================
# security.py - Request validation,
# rate limiting, and abuse prevention
# ================================

import ipaddress
from urllib.parse import urlparse

from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)


ALLOWED_DOMAINS: set[str] = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "m.youtube.com",
    "tiktok.com",
    "www.tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
    "instagram.com",
    "www.instagram.com",
    "twitter.com",
    "www.twitter.com",
    "x.com",
    "www.x.com",
    "t.co",
    "facebook.com",
    "www.facebook.com",
    "fb.watch",
}


BLOCKED_IP_RANGES = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


BLOCKED_URL_PATTERNS: list[str] = [
    "localhost",
    "metadata.google",
    "169.254.169.254",
    "file://",
    "ftp://",
    "../",
    "%2e%2e",
]


class SecurityError(Exception):
    """Raised when a request fails security validation."""


def validate_url(url: str) -> None:
    if not url or len(url) > 2048:
        raise SecurityError("Invalid URL length.")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SecurityError("Only http and https URLs are allowed.")

    hostname = parsed.hostname or ""

    url_lower = url.lower()
    for pattern in BLOCKED_URL_PATTERNS:
        if pattern in url_lower:
            raise SecurityError(f"URL contains blocked pattern: {pattern}")

    clean_host = hostname.lower().lstrip("www.")
    allowed_clean = {domain.lstrip("www.") for domain in ALLOWED_DOMAINS}

    if hostname.lower() not in ALLOWED_DOMAINS and clean_host not in allowed_clean:
        raise SecurityError(
            f"Domain '{hostname}' is not supported. "
            "Supported platforms: YouTube, TikTok, Instagram, X/Twitter, Facebook."
        )

    try:
        ip = ipaddress.ip_address(hostname)
        for blocked_range in BLOCKED_IP_RANGES:
            if ip in blocked_range:
                raise SecurityError("Requests to internal IP addresses are not allowed.")
    except ValueError:
        pass


def validate_quality(quality: str) -> None:
    allowed = {"2160p", "1080p", "720p", "480p", "audio"}
    if quality not in allowed:
        raise SecurityError(
            f"Invalid quality '{quality}'. Must be one of: {', '.join(sorted(allowed))}"
        )
