import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto("https://juanmoisesdelaserna.es/wp-admin/post-new.php")
            await page.wait_for_timeout(5000) # Wait to see what loads
            await page.screenshot(path="wp_admin_test.png")
            print(f"Page title: {await page.title()}")
        except Exception as e:
            print(f"Error: {e}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
