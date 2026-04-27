import asyncio
from fastapi import APIRouter, HTTPException
from fastapi import Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import requests

import utils

router = APIRouter()
route = "/twitch/"


class ChatMessage(BaseModel):
    message: str = Field(min_length=1)
    channel: str | None = None


@router.get(route)
async def hello():
    return "oi"


@router.post(route + "chat")
async def send_twitch_chat_message(payload: ChatMessage):
    try:
        return await run_in_threadpool(
            utils.send_chat_message,
            payload.message,
            payload.channel,
        )
    except utils.TwitchConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except utils.TwitchChannelNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except requests.RequestException as exc:
        response = getattr(exc, "response", None)
        detail = response.text if response is not None else str(exc)
        raise HTTPException(status_code=502, detail=detail) from exc


@router.get(route + "mock-chat")
async def mock_twitch_chat(
    count: int = Query(default=20, ge=1, le=250),
    interval_ms: int = Query(default=1200, ge=0, le=60000),
    interval_jitter_ms: int = Query(default=250, ge=0, le=10000),
    size_profile: utils.SizeProfile = Query(default="mixed"),
    include_emotes: bool = Query(default=True),
    stream: bool = Query(default=False),
    seed: int | None = Query(default=None),
    channel: str = Query(default="guinhoshuto", min_length=1),
):
    options = utils.MockChatOptions(
        channel=channel,
        count=count,
        interval_ms=interval_ms,
        interval_jitter_ms=interval_jitter_ms,
        size_profile=size_profile,
        include_emotes=include_emotes,
        seed=seed,
    )
    feed = utils.build_mock_chat_feed(options)

    if not stream:
        return feed

    async def event_stream():
        meta = {key: value for key, value in feed.items() if key != "messages"}
        yield utils.format_sse("meta", meta)
        for message in feed["messages"]:
            wait_ms = message["waitMs"]
            if wait_ms > 0:
                await asyncio.sleep(wait_ms / 1000)
            yield utils.format_sse("message", message)
        yield utils.format_sse(
            "done",
            {
                "channel": feed["channel"],
                "count": feed["count"],
            },
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
