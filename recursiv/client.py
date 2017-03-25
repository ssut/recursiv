import asyncio

import aiohttp
import uvloop


class RecursivClient:

    def __init__(self):
        self._session = aiohttp.ClientSession()

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session.close:
            raise RuntimeError('Attempted to use a closed session')
        return self._session

    def _run(self):
        pass

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self._run())
        try:
            loop.run_until_complete(future)
        except KeyboardInterrupt:
            pass
        except:
            import traceback
            traceback.print_exc()
            raise SystemExit(1)
        finally:
            loop.close()
