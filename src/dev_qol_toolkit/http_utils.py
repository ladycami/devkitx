from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Iterable, Mapping, MutableMapping

import httpx


RETRY_STATUSES = {429, 500, 502, 503, 504}


def _sleep_backoff(attempt: int, base: float = 0.25, cap: float = 4.0) -> None:
    delay = min(cap, base * (2 ** (attempt - 1)))
    time.sleep(delay)


def _merge_headers(
    base: Mapping[str, str] | None, extra: Mapping[str, str] | None
) -> MutableMapping[str, str]:
    out: dict[str, str] = {}
    if base:
        out.update(base)
    if extra:
        out.update(extra)
    return out


def api_request(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    json_body: Any | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 15.0,
    retries: int = 3,
) -> Any:
    """
    Sync HTTP request with retries/jitter on common transient failures.
    Returns parsed JSON when possible else text.
    """
    hdrs = _merge_headers({"accept": "application/json"}, headers)
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(http2=True, timeout=timeout, follow_redirects=True) as client:
                resp = client.request(method.upper(), url, headers=hdrs, json=json_body, params=params)
            if resp.status_code in RETRY_STATUSES and attempt < retries:
                _sleep_backoff(attempt)
                continue
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "")
            if "application/json" in ctype:
                return resp.json()
            return resp.text
        except Exception as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            _sleep_backoff(attempt)
    if last_exc:
        raise last_exc


class BaseAPIClient:
    def __init__(self, base_url: str, headers: Mapping[str, str] | None = None, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs: Any) -> Any:
        return api_request("GET", self._url(path), headers=self.headers, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return api_request("POST", self._url(path), headers=self.headers, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return api_request("PUT", self._url(path), headers=self.headers, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return api_request("DELETE", self._url(path), headers=self.headers, **kwargs)


# Async helpers (optional)
async def async_api_request(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    json_body: Any | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 15.0,
    retries: int = 3,
) -> Any:
    hdrs = _merge_headers({"accept": "application/json"}, headers)
    last_exc: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(http2=True, timeout=timeout, follow_redirects=True) as client:
                resp = await client.request(method.upper(), url, headers=hdrs, json=json_body, params=params)
            if resp.status_code in RETRY_STATUSES and attempt < retries:
                await asyncio.sleep(min(4.0, 0.25 * (2 ** (attempt - 1))))
                continue
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "")
            if "application/json" in ctype:
                return resp.json()
            return resp.text
        except Exception as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            await asyncio.sleep(min(4.0, 0.25 * (2 ** (attempt - 1))))
    if last_exc:
        raise last_exc