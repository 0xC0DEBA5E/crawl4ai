import asyncio

from aiohttp import web

from crawl4ai import CrawlerRunConfig, CacheMode, AsyncWebCrawler

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head><title>Index Page</title></head>
<body>
    <a href="second-page.html">Link to second page</a>
</body>
</html>
"""

SECOND_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Second Page</title></head>
<body>
    <p>This is the second page</p>
</body>
</html>
"""


async def handle_index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')


async def handle_second_page(request):
    return web.Response(text=SECOND_PAGE_HTML, content_type='text/html')


async def start_server(port=8000, host='localhost'):
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/index.html', handle_index)
    app.router.add_get('/second-page.html', handle_second_page)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    return runner


async def extract_links():
    host = 'localhost'
    port = 8000
    runner = await start_server(port=port, host=host)

    try:
        run_config = CrawlerRunConfig(cache_mode=CacheMode.DISABLED)
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url=f"http://{host}:{port}/index.html", config=run_config)
            result = results[0]
            assert result.status_code == 200, "should have returned a 200 status code"
            internal_links = result.links.get('internal', [])
            assert len(internal_links) == 1, "should have exactly one internal link"
            assert internal_links[0]['href'] == f"http://{host}:{port}/second-page.html", \
                "the internal link should be the second page link"
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(extract_links())
