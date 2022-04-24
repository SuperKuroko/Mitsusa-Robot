import base64
import shutil
import urllib3
import config
import os
import json
from pathlib import Path
from typing import Optional
from appdirs import AppDirs
from playwright.async_api import Browser, async_playwright
from PIL import Image
from io import BytesIO


_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    browser = await async_playwright().start()
    _browser = await browser.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)


async def get_dynamic_screenshot(url):
    browser = await get_browser()
    page = None
    try:
        page = await browser.new_page(device_scale_factor=2,
                                      viewport={"width": 2160, "height": 1080})
        await page.goto(url, wait_until='networkidle', timeout=10000)
        card = await page.query_selector(".card")
        assert card
        clip = await card.bounding_box()
        assert clip
        bar = await page.query_selector(".text-bar")
        assert bar
        bar_bound = await bar.bounding_box()
        assert bar_bound
        clip['height'] = bar_bound['y'] - clip['y']
        image = await page.screenshot(clip=clip, full_page=True, type="png")
        await page.close()
        return image
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


async def get_weibo_screenshot(url):
    browser = await get_browser()
    page = None
    try:
        print(1)
        page = await browser.new_page(device_scale_factor=2,
                                      user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
                                      viewport={"width": 2160, "height": 1080})
        print(2)
        await page.goto(url, wait_until='networkidle', timeout=30000)
        print(3)
        card = await page.query_selector("article")
        print(4)
        assert card
        print(5)
        clip = await card.bounding_box()
        print(6)
        assert clip
        print(7)
        image = await page.screenshot(clip=clip, full_page=True, type="png")
        print(8)
        await page.close()
        print(9)
        return image
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise



