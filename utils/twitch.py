import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

TWITCH_API_BASE = "https://api.twitch.tv/helix"
TWITCH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"
DEFAULT_CHANNEL = os.getenv("TWITCH_DEFAULT_CHANNEL", "guinhoshuto")


class TwitchConfigError(RuntimeError):
    pass


class TwitchChannelNotFoundError(ValueError):
    pass


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise TwitchConfigError(f"Missing required environment variable: {name}")


def _get_access_token() -> str:
    token = os.getenv("TWITCH_USER_ACCESS_TOKEN") or os.getenv("TWITCH_OAUTH")
    if token:
        return token.strip().strip('"')
    raise TwitchConfigError(
        "Missing required environment variable: TWITCH_USER_ACCESS_TOKEN or TWITCH_OAUTH"
    )


def _get_client_id() -> str:
    client_id = os.getenv("TWITCH_CLIENT_ID")
    if client_id:
        return client_id.strip().strip('"')
    return _validate_token()["client_id"]


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_access_token()}",
        "Client-Id": _get_client_id(),
        "Content-Type": "application/json",
    }


def _validate_token() -> dict[str, Any]:
    response = requests.get(
        TWITCH_VALIDATE_URL,
        headers={"Authorization": f"Bearer {_get_access_token()}"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _get_sender_id() -> str:
    sender_id = os.getenv("TWITCH_SENDER_ID")
    if sender_id:
        return sender_id
    return _validate_token()["user_id"]


def _get_broadcaster_id(channel_login: str) -> str:
    configured_channel = os.getenv("TWITCH_DEFAULT_CHANNEL", DEFAULT_CHANNEL).lower()
    broadcaster_id = os.getenv("TWITCH_BROADCASTER_ID")
    if broadcaster_id and channel_login.lower() == configured_channel:
        return broadcaster_id

    response = requests.get(
        f"{TWITCH_API_BASE}/users",
        headers=_get_headers(),
        params={"login": channel_login},
        timeout=15,
    )
    response.raise_for_status()

    data = response.json().get("data", [])
    if not data:
        raise TwitchChannelNotFoundError(f"Twitch channel not found: {channel_login}")

    return data[0]["id"]


def _split_text(text: str, max_length: int = 500) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        cut_off = text.rfind(" ", 0, max_length)
        if cut_off == -1:
            cut_off = max_length

        chunk = text[:cut_off].strip()
        text = text[cut_off:].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def send_chat_message(message: str, channel: str | None = None) -> dict[str, Any]:
    channel_login = (channel or DEFAULT_CHANNEL).strip()
    if not channel_login:
        raise ValueError("Twitch channel cannot be empty")

    chunks = _split_text(message.strip(), max_length=500)
    if not chunks:
        raise ValueError("Message cannot be empty")

    broadcaster_id = _get_broadcaster_id(channel_login)
    sender_id = _get_sender_id()
    responses: list[dict[str, Any]] = []

    for chunk in chunks:
        response = requests.post(
            f"{TWITCH_API_BASE}/chat/messages",
            headers=_get_headers(),
            json={
                "broadcaster_id": broadcaster_id,
                "sender_id": sender_id,
                "message": chunk,
            },
            timeout=15,
        )
        response.raise_for_status()
        responses.append(response.json())

    return {
        "channel": channel_login,
        "messages_sent": len(chunks),
        "responses": responses,
    }
