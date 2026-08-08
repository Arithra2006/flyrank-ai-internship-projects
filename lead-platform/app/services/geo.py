"""
Geo enrichment service.

Resolves an IP address to country/region/city using a primary API
(ip-api.com) with a fallback to a secondary API (ipapi.co) if the
primary fails, times out, or is rate-limited.

Both are free-tier third-party APIs. Response formats and rate limits
can change without notice on the provider's side — verify current
behavior against their live docs before relying on this in production.
"""
import httpx

PRIMARY_URL = "http://ip-api.com/json/{ip}"
FALLBACK_URL = "https://ipapi.co/{ip}/json/"

TIMEOUT = 3.0


def _is_private_ip(ip: str) -> bool:
    return (
        ip.startswith("127.")
        or ip.startswith("192.168.")
        or ip.startswith("10.")
        or ip == "localhost"
        or ip == "testclient"
        or ip.startswith("172.16.")
    )


async def resolve_geo(ip: str) -> dict:
    """
    Returns a dict: {country, region, city, source}
    All fields may be None if resolution fails or IP is private/local.
    """
    result = {"country": None, "region": None, "city": None, "source": None}

    if not ip or _is_private_ip(ip):
        result["source"] = "skipped_private_ip"
        return result

    # Try primary: ip-api.com
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(PRIMARY_URL.format(ip=ip))
            if resp.status_code == 200:
                payload = resp.json()
                if payload.get("status") == "success":
                    result["country"] = payload.get("country")
                    result["region"] = payload.get("regionName")
                    result["city"] = payload.get("city")
                    result["source"] = "ip-api.com"
                    return result
    except (httpx.HTTPError, ValueError):
        pass

    # Fallback: ipapi.co
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(FALLBACK_URL.format(ip=ip))
            if resp.status_code == 200:
                payload = resp.json()
                if not payload.get("error"):
                    result["country"] = payload.get("country_name")
                    result["region"] = payload.get("region")
                    result["city"] = payload.get("city")
                    result["source"] = "ipapi.co"
                    return result
    except (httpx.HTTPError, ValueError):
        pass

    result["source"] = "unresolved"
    return result
