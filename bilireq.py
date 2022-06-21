# -*- coding: utf-8 -*-

import aiohttp

from typing import Dict


class BiliReq:

    def __init__(self):
        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88'
                          'Safari/537.36 Edg/87.0.664.60',
            'Referer': 'https://www.bilibili.com/'
        }
        self.proxies = None

    async def request(self, method, url, **kwargs) -> Dict:
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.request(method=method, url=url, proxy=self.proxies, **kwargs) as response:
                data = await response.json(encoding="utf-8")
                return data["data"]

    async def get_user_dynamics(self, uid):
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0'
        return await self.request('GET', url)

    async def get_live_list(self, uids):
        """根据 UID 获取直播间信息列表"""
        url = 'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
        params = {'uids': uids}
        return await self.request("POST", url, params=params)
