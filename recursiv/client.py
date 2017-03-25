import os
import os.path
import asyncio
import logging
from urllib.parse import urlparse

import aiohttp
import uvloop

from .parser import extract_links


class RecursivClient:

    def __init__(self, index_url: str, output_dir: str, num_connections: int):
        self._session = None
        self._loop = None

        if index_url[-1] != '/':
            index_url += '/'
        self.index_url = index_url
        self.num_connections = num_connections
        self.output_dir = output_dir
        self.logger = logging.getLogger('recursiv')

        self.directories = []
        self.files = []

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError('Attempted to use a closed session')
        return self._session

    async def _collect_urls(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url) as resp:
            body = await resp.text()
            path = urlparse(url).path[1:]
            dirs, files = extract_links(body)
            self.directories.extend([os.path.join(path, dir) for dir in dirs])
            self.files.extend([os.path.join(path, file) for file in files])
            for path in dirs:
                suburl = url + path
                await self._collect_urls(session, suburl)

    async def collect_urls(self, url: str):
        async with self.session as session:
            await self._collect_urls(session, url)

    async def collect_urls_from_index(self):
        task = asyncio.Task(self.collect_urls(self.index_url))
        while not task.done():
            self.logger.debug('Collected files: {}'.format(
                len(self.files)))
            await asyncio.sleep(1)
        self.logger.info('Total directories found: {}'.format(
            len(self.directories)))
        self.logger.info('Total files found: {}'.format(len(self.files)))

    def create_directories(self):
        root = urlparse(self.index_url).path[1:]
        cwd = os.getcwd()
        if self.output_dir.startswith('.'):
            self.output_dir = os.path.abspath(
                os.path.join(cwd, self.output_dir))
        # create a root directory
        os.makedirs(os.path.join(self.output_dir, root), exist_ok=True)
        for path in self.directories:
            target = os.path.join(self.output_dir, path)
            os.makedirs(target, exist_ok=True)

    async def _run(self):
        async with aiohttp.ClientSession() as session:
            self._session = session
            self.logger.info('Starting collecting URLs..')
            await self.collect_urls_from_index()
            self.logger.info('Creating the same dictory structure..')
            self.create_directories()

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
