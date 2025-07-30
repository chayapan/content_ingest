import asyncio
import argparse
import time
import nltk
import requests
from bs4 import BeautifulSoup
from pythainlp.tokenize import sent_tokenize, word_tokenize
from playwright.async_api import async_playwright

FIREFOX_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
)
COMMON_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1"
}

async def take_screenshot(url: str, output: str, full_page: bool = False,
                    width: int = 1280, height: int = 720, delay: float = 0):
    res = requests.get(url)
    print(res.status_code, res.headers)
    async with async_playwright() as p:
        # p.chromium, p.firefox, or p.webkit can be used
        # browser = await p.webkit.launch()
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context(viewport={"width": width, "height": height},
            user_agent=FIREFOX_USER_AGENT,
            extra_http_headers=COMMON_HEADERS,
            locale="en-US",
            geolocation={"longitude": 100.5018, "latitude": 13.7563},  # Bangkok example
            permissions=["geolocation"]
            )
        page = await context.new_page()
        response = await page.goto(url, timeout=20000, wait_until="load") 
        # Ref: https://playwright.dev/docs/api/class-page
        await page.wait_for_selector("body", timeout=20000)
        print(f"Navigating to {url}... :" + str(response.status) if response else "No response."
        )
        if response is None or not response.ok:
            print(f"Failed to navigate to {url}")
            await browser.close()
            return

        final_url = page.url
        if final_url != url:
            print(f"Redirected to {final_url}")

        if delay > 0:
            print(f"Waiting {delay} seconds before taking screenshot...")
            time.sleep(delay)
        
        await page.screenshot(path=output, full_page=full_page)
        content = await page.content()
        content = content.encode("utf-8")
        with open("output.html", "w") as f:
                  f.write(str(content))
        print(f"Screenshot saved to {output}")

        # Execute JavaScript to get all link hrefs
        hrefs = await page.evaluate("""
            () => {
                return Array.from(document.links).map(item => item.href);
            }
        """)
        print("Links found on the page:")
        for href in hrefs:
            print(href)

        # Extract text from HTML content
        soup = BeautifulSoup(content, features="html.parser")
        raw = soup.get_text()

        # https://pythainlp.org/docs/2.0/api/tokenize.html
        # pythainlp.tokenize.sent_tokenize(
        # 
        print("="*80)
        print(raw.replace("\n", " ").replace("\t","").replace("  ", " "))

        # depends on pycrfsuite
        # print("="*80)
        # sentences = sent_tokenize(raw)
        # print(f"Number of sentences: {len(sentences)}")
        # print("="*80)
        # words = word_tokenize(raw)
        # print(f"Number of words: {len(words)}")

        await browser.close()

def main():
    parser = argparse.ArgumentParser(description="Take a screenshot of a webpage using Playwright.")
    parser.add_argument("url", help="URL of the page to screenshot")
    parser.add_argument("output", help="Output image path, e.g., screenshot.png")
    parser.add_argument("--full", action="store_true", help="Capture full page")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width")
    parser.add_argument("--height", type=int, default=720, help="Viewport height")
    parser.add_argument("--delay", type=float, default=0, help="Delay in seconds before taking screenshot")

    args = parser.parse_args()
    asyncio.run(take_screenshot(args.url, args.output, args.full, args.width, args.height, args.delay))

if __name__ == "__main__":
    main()
