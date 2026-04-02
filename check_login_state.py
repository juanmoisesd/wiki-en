import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    async with async_playwright() as p:
        # Try launching with the default user data dir if possible, or just check cookies
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto("https://juanmoisesdelaserna.es/wp-admin/")
            await page.wait_for_timeout(3000)
            cookies = await context.cookies()
            print(f"Cookies: {json.dumps(cookies, indent=2)}")

            # Check for admin bar or specific admin elements
            admin_bar = await page.query_selector("#wpadminbar")
            if admin_bar:
                print("Logged in! Admin bar found.")
            else:
                print("Not logged in. Admin bar not found.")

            await page.screenshot(path="wp_check.png")
        except Exception as e:
            print(f"Error: {e}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
