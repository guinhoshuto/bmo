from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import uuid4, uuid5, NAMESPACE_DNS


SizeProfile = Literal["short", "mixed", "long"]


@dataclass(slots=True)
class MockChatOptions:
    channel: str = "guinhoshuto"
    count: int = 20
    interval_ms: int = 1_200
    interval_jitter_ms: int = 250
    size_profile: SizeProfile = "mixed"
    include_emotes: bool = True
    seed: int | None = None


VIEWERS = [
    {
        "login": "akira_dev",
        "display_name": "AkiraDev",
        "color": "#1E90FF",
        "badges": [{"type": "moderator", "version": "1"}],
    },
    {
        "login": "chat_da_lua",
        "display_name": "ChatDaLua",
        "color": "#FF69B4",
        "badges": [{"type": "subscriber", "version": "12"}],
    },
    {
        "login": "cafecomjs",
        "display_name": "CafeComJS",
        "color": "#8A2BE2",
        "badges": [],
    },
    {
        "login": "pixelpuff",
        "display_name": "PixelPuff",
        "color": "#00B894",
        "badges": [{"type": "vip", "version": "1"}],
    },
    {
        "login": "senhorclip",
        "display_name": "SenhorClip",
        "color": "#F39C12",
        "badges": [],
    },
    {
        "login": "gui_testa_overlay",
        "display_name": "GuiTestaOverlay",
        "color": "#E74C3C",
        "badges": [{"type": "subscriber", "version": "3"}],
    },
]

EMOTES = [
    {"id": "25", "name": "Kappa"},
    {"id": "1902", "name": "Keepo"},
    {"id": "305954156", "name": "PogChamp"},
    {"id": "425618", "name": "HeyGuys"},
    {"id": "30259", "name": "SwiftRage"},
    {"id": "81274", "name": "LUL"},
]
EMOTE_BY_NAME = {emote["name"]: emote for emote in EMOTES}

SHORT_TEMPLATES = [
    "salve chat",
    "boa",
    "{emote}",
    "{emote} {emote}",
    "teste 123",
    "overlay linda {emote}",
    "chegou liso aqui",
    "gg",
]

MEDIUM_TEMPLATES = [
    "essa entrada ficou limpa demais {emote}",
    "testando uma mensagem media para validar quebra de linha no widget",
    "o nome do usuario e a cor renderizaram certinho por aqui {emote}",
    "curti o ritmo dessa fila de mensagens no preview",
    "mandando texto com algumas palavras extras para simular chat normal",
    "o balao encaixou bem mesmo quando entra uma mensagem mais comprida {emote}",
]

LONG_TEMPLATES = [
    "mandando uma mensagem grande para testar largura, quebra de linha, empilhamento e tempo de permanencia do item dentro do chat sem estourar o layout do widget {emote}",
    "essa aqui e uma mensagem mais longa com cara de conversa real para ajudar a validar padding, alinhamento, avatar opcional e como os emotes ficam misturados no meio do texto {emote}",
    "quero conferir se o widget continua legivel quando chega uma frase bem maior, com varias palavras, alguns detalhes de contexto e tambem um emote no final para fechar o teste {emote}",
]


def build_mock_chat_feed(options: MockChatOptions) -> dict[str, Any]:
    rng = random.Random(options.seed)
    started_at = datetime.now(timezone.utc)
    room_id = _get_room_id(options.channel)
    messages: list[dict[str, Any]] = []
    elapsed_ms = 0

    for index in range(options.count):
        wait_ms = 0 if index == 0 else _get_wait_ms(rng, options)
        elapsed_ms += wait_ms
        scheduled_at = started_at + timedelta(milliseconds=elapsed_ms)
        messages.append(
            _build_message_envelope(
                rng=rng,
                channel=options.channel,
                room_id=room_id,
                sequence=index + 1,
                wait_ms=wait_ms,
                elapsed_ms=elapsed_ms,
                scheduled_at=scheduled_at,
                size_profile=options.size_profile,
                include_emotes=options.include_emotes,
            )
        )

    return {
        "channel": options.channel,
        "count": options.count,
        "intervalMs": options.interval_ms,
        "intervalJitterMs": options.interval_jitter_ms,
        "sizeProfile": options.size_profile,
        "includeEmotes": options.include_emotes,
        "seed": options.seed,
        "startedAt": started_at.isoformat(),
        "messages": messages,
    }


def format_sse(event_name: str, payload: dict[str, Any]) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _build_message_envelope(
    *,
    rng: random.Random,
    channel: str,
    room_id: str,
    sequence: int,
    wait_ms: int,
    elapsed_ms: int,
    scheduled_at: datetime,
    size_profile: SizeProfile,
    include_emotes: bool,
) -> dict[str, Any]:
    viewer = rng.choice(VIEWERS)
    text = _build_message_text(rng, size_profile, include_emotes)
    msg_id = str(uuid4())
    user_id = str(100_000 + rng.randint(1, 899_999))
    emotes = _extract_emotes(text)
    badges = viewer["badges"]

    event_data = {
        "channel": channel,
        "time": scheduled_at.isoformat(),
        "msgId": msg_id,
        "userId": user_id,
        "nick": viewer["login"],
        "displayName": viewer["display_name"],
        "displayColor": viewer["color"],
        "text": text,
        "isAction": False,
        "badges": badges,
        "emotes": emotes,
        "tags": {
            "badges": _stringify_badges(badges),
            "color": viewer["color"],
            "display-name": viewer["display_name"],
            "emotes": _stringify_emotes(emotes),
            "id": msg_id,
            "mod": _has_badge(badges, "moderator"),
            "room-id": room_id,
            "subscriber": _has_any_sub_badge(badges),
            "turbo": "0",
            "user-id": user_id,
            "vip": _has_badge(badges, "vip"),
        },
    }

    return {
        "sequence": sequence,
        "waitMs": wait_ms,
        "elapsedMs": elapsed_ms,
        "scheduledAt": scheduled_at.isoformat(),
        "detail": {
            "listener": "message",
            "event": {
                "service": "twitch",
                "data": event_data,
            },
        },
    }


def _build_message_text(
    rng: random.Random,
    size_profile: SizeProfile,
    include_emotes: bool,
) -> str:
    template_pool = _get_template_pool(size_profile, include_emotes)
    template = rng.choice(template_pool)

    if include_emotes:
        emote = rng.choice(EMOTES)["name"]
        second_emote = rng.choice(EMOTES)["name"]
    else:
        emote = ""
        second_emote = ""

    text = template.format(emote=emote, emote2=second_emote).strip()
    text = " ".join(part for part in text.split(" ") if part)

    if include_emotes and "{emote}" not in template and rng.random() < 0.45:
        text = f"{text} {rng.choice(EMOTES)['name']}".strip()

    return text or "mensagem de teste"


def _get_template_pool(size_profile: SizeProfile, include_emotes: bool) -> list[str]:
    short_templates = SHORT_TEMPLATES
    if not include_emotes:
        short_templates = [template for template in SHORT_TEMPLATES if template != "{emote}"]
        short_templates = [
            template for template in short_templates if template != "{emote} {emote}"
        ]

    if size_profile == "short":
        return short_templates
    if size_profile == "long":
        return LONG_TEMPLATES
    return short_templates + MEDIUM_TEMPLATES + LONG_TEMPLATES


def _extract_emotes(text: str) -> list[dict[str, Any]]:
    emotes = []
    search_from = 0
    for token in text.split():
        start = text.find(token, search_from)
        end = start + len(token) - 1
        search_from = end + 1

        emote = EMOTE_BY_NAME.get(token)
        if not emote:
            continue

        emotes.append(
            {
                "id": emote["id"],
                "name": emote["name"],
                "start": start,
                "end": end,
            }
        )
    return emotes


def _stringify_emotes(emotes: list[dict[str, Any]]) -> str:
    if not emotes:
        return ""

    grouped: dict[str, list[str]] = {}
    for emote in emotes:
        grouped.setdefault(emote["id"], []).append(f"{emote['start']}-{emote['end']}")

    return "/".join(
        f"{emote_id}:{','.join(positions)}" for emote_id, positions in grouped.items()
    )


def _stringify_badges(badges: list[dict[str, str]]) -> str:
    if not badges:
        return ""
    return ",".join(f"{badge['type']}/{badge['version']}" for badge in badges)


def _get_room_id(channel: str) -> str:
    if channel.lower() == "guinhoshuto":
        return "271736706"
    return str((uuid5(NAMESPACE_DNS, channel).int % 900_000_000) + 100_000_000)


def _get_wait_ms(rng: random.Random, options: MockChatOptions) -> int:
    if options.interval_ms == 0 and options.interval_jitter_ms == 0:
        return 0

    min_wait = max(0, options.interval_ms - options.interval_jitter_ms)
    max_wait = max(min_wait, options.interval_ms + options.interval_jitter_ms)
    return rng.randint(min_wait, max_wait)


def _has_badge(badges: list[dict[str, str]], badge_type: str) -> str:
    return "1" if any(badge["type"] == badge_type for badge in badges) else "0"


def _has_any_sub_badge(badges: list[dict[str, str]]) -> str:
    return "1" if any(badge["type"] == "subscriber" for badge in badges) else "0"
