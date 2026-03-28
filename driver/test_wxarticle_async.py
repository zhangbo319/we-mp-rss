import asyncio
import time
import unittest

from driver.wxarticle import WXArticleFetcher


class WXArticleFetcherAsyncTest(unittest.IsolatedAsyncioTestCase):
    async def test_async_get_article_content_does_not_block_event_loop(self):
        fetcher = object.__new__(WXArticleFetcher)

        def fake_get_article_content(url):
            time.sleep(0.05)
            return {"url": url, "ok": True}

        fetcher.get_article_content = fake_get_article_content

        marker = {"triggered": False}

        async def tick():
            await asyncio.sleep(0.01)
            marker["triggered"] = True

        tick_task = asyncio.create_task(tick())

        result = await asyncio.wait_for(
            fetcher.async_get_article_content("https://example.com/article"),
            timeout=0.5,
        )

        self.assertEqual(result["url"], "https://example.com/article")
        self.assertTrue(
            marker["triggered"],
            "异步抓取不应阻塞事件循环，否则会导致整个服务请求假死",
        )

        await tick_task


if __name__ == "__main__":
    unittest.main()
