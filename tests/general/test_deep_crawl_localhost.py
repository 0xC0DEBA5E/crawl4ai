import pytest
from aiohttp import web

from crawl4ai import CrawlerRunConfig, CacheMode, AsyncWebCrawler, BFSDeepCrawlStrategy

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Index Page</title>
</head>
<body>
    <a href="/path/second-page.html">Link to second page.</a>
</body>
</html>
"""

SECOND_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Second Page</title></head>
<body>
    <p>This is the second page</p>
    <a href="third-page.html#fragment">Link to third page with fragment.</a>
    <a href="http://example.com">External link</a>
</body>
</html>
"""

THIRD_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Third Page</title></head>
<body>
</body>
</html>
"""


async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type="text/html")


async def handle_second_page(request):
    return web.Response(text=SECOND_PAGE_HTML, content_type="text/html")


async def handle_third_page(request):
    return web.Response(text=THIRD_PAGE_HTML, content_type="text/html")


async def start_server(port=8000, host="localhost"):
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/index.html", handle_index)
    app.router.add_get("/path/second-page.html", handle_second_page)
    app.router.add_get("/path/third-page.html", handle_third_page)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    return runner


@pytest.mark.asyncio
async def test_deep_crawl_localhost():
    host = "localhost"
    port = 8000
    runner = await start_server(port=port, host=host)

    try:
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,
            delay_before_return_html=0.1,
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=2, include_external=False
            ),
        )
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(
                url=f"http://{host}:{port}/index.html", config=run_config
            )
            assert len(results) == 3, "should have crawled three pages"
            assert [result.url for result in results] == [
                f"http://{host}:{port}/index.html",
                f"http://{host}:{port}/path/second-page.html",
                f"http://{host}:{port}/path/third-page.html",
            ], "should have crawled the expected URLs"
            assert [result.status_code for result in results] == [200, 200, 200], "should have returned 200 status codes for all pages"
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    # Use pytest for async tests
    pytest.main(["-xvs", __file__])
