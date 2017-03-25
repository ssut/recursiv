import asyncio
import logging

import aiohttp
import uvloop

from .parser import extract_links


class RecursivClient:

    def __init__(self, index_url: str, num_connections: int):
        self._session = None
        self._loop = None

        if index_url[-1] != '/':
            index_url += '/'
        self.index_url = index_url
        self.num_connections = num_connections
        self.logger = logging.getLogger('recursiv')
        self.collected = []

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError('Attempted to use a closed session')
        return self._session

    async def _collect_urls(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url) as resp:
            body = await resp.text()
            dirs, files = extract_links(body)
            self.collected.extend(files)
            for path in dirs:
                suburl = url + path
                await self._collect_urls(session, suburl)

    async def collect_urls(self, url: str):
        async with self.session as session:
            await self._collect_urls(session, url)

    async def collect_urls_from_index(self):
        task = asyncio.Task(self.collect_urls(self.index_url))
        while not task.done():
            self.logger.debug('Collected items: {}'.format(
                len(self.collected)))
            await asyncio.sleep(1)
        self.logger.info('Total items: {}'.format(len(self.collected)))

    async def _run(self):
        async with aiohttp.ClientSession() as session:
            self._session = session
            self.logger.info('Prepared for collecting URLs..')
            await self.collect_urls_from_index()

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self._loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self._run())
        try:
            self._loop.run_until_complete(future)
        except KeyboardInterrupt:
            pass
        except:
            import traceback
            traceback.print_exc()
            raise SystemExit(1)
        finally:
            self._loop.close()
