import os
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CACARECO_API_BASE_URL = (
    "https://cacareco-backend-production.up.railway.app"
)


class CacarecoConfigError(RuntimeError):
    pass


def _get_base_url() -> str:
    base_url = os.getenv(
        "CACARECO_API_BASE_URL",
        DEFAULT_CACARECO_API_BASE_URL,
    ).strip()
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"
    return base_url.rstrip("/")


def _get_admin_api_key() -> str:
    api_key = os.getenv("CACARECO_ADMIN_API_KEY")
    if api_key:
        return api_key.strip().strip('"')
    raise CacarecoConfigError(
        "Missing required environment variable: CACARECO_ADMIN_API_KEY"
    )


def _request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> Any:
    response = requests.request(
        method,
        f"{_get_base_url()}{path}",
        headers={
            "Authorization": f"Bearer {_get_admin_api_key()}",
            "Accept": "application/json",
        },
        params=params,
        json=json,
        timeout=30,
    )
    response.raise_for_status()

    if not response.content:
        return {}
    if "application/json" in response.headers.get("content-type", ""):
        return response.json()
    return {"text": response.text}


def get_etsy_listing(
    listing_id: str,
    includes: str = "Images,Shop,Inventory",
) -> Any:
    return _request(
        "GET",
        f"/api/v1/admin/integrations/etsy/listings/{quote(listing_id, safe='')}",
        params={"includes": includes},
    )


def get_etsy_shop_listings(
    shop_id: str,
    *,
    state: str = "active",
    limit: int = 25,
    offset: int = 0,
    includes: str = "Images,Shop",
) -> Any:
    return _request(
        "GET",
        f"/api/v1/admin/integrations/etsy/shops/{quote(shop_id, safe='')}/listings",
        params={
            "state": state,
            "limit": limit,
            "offset": offset,
            "includes": includes,
        },
    )


def send_twitch_test_messages(
    *,
    channel_username: str = "guinhoshuto",
    quantity: int = 8,
    interval_seconds: float = 1.5,
    messages: list[str] | None = None,
) -> Any:
    payload: dict[str, Any] = {
        "channelUsername": channel_username,
        "quantity": quantity,
        "intervalSeconds": interval_seconds,
    }
    if messages:
        payload["messages"] = messages

    return _request(
        "POST",
        "/api/v1/admin/integrations/twitch/chat/test-messages",
        json=payload,
    )
