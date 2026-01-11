"""turntable_client.py

Simple HTTP client for the ESP32 turntable.
"""
from __future__ import annotations

import requests
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class TurntableClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, path: str, params: dict = None) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("HTTP error to %s: %s", url, e)
            return None

    def rotate_to(self, angle_deg: float) -> Optional[dict]:
        logger.info("Request rotate_to(%s deg)", angle_deg)
        return self._request('/rotate', params={'deg': angle_deg})

    def step(self, deg: float) -> Optional[dict]:
        logger.info("Request step(%s deg)", deg)
        return self._request('/step', params={'deg': deg})

    def home(self) -> Optional[dict]:
        logger.info("Request home")
        return self._request('/home')

    def status(self) -> Optional[dict]:
        return self._request('/status')

    def wait_until_idle(self, poll_interval: float = 0.2, timeout: float = 30.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            st = self.status()
            if st is None:
                time.sleep(poll_interval)
                continue
            if st.get('state') == 'idle':
                logger.debug("Turntable idle")
                return True
            time.sleep(poll_interval)
        logger.warning("Timeout waiting for turntable to be idle")
        return False
