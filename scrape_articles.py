import os
import asyncio

# FORCE ALL SYSTEM ENGINES TO OPERATE OUT OF THE D: DRIVE
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"D:\f1-chatbot\.playwright-browsers"
os.environ["CRAWL4_AI_BASE_DIRECTORY"] = r"D:\f1-chatbot\.crawl4ai"

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def scrape_f1_pages():
    urls = [
        "https://en.wikipedia.org/wiki/2024_Monaco_Grand_Prix",
        "https://www.racefans.net/2024/05/26/leclerc-finally-breaks-his-home-race-jinx-with-monaco-grand-prix-victory/"
    ]
    
    os.makedirs(os.path.join("data", "raw"), exist_ok=True)

    browser_cfg = BrowserConfig(headless=True, verbose=True)
    # FIXED: Replaced old flag. Clean markdown is handled automatically in result.markdown
    crawl_cfg = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for i, url in enumerate(urls):
            print(f"Scraping textual data from: {url}...")
            result = await crawler.arun(url=url, config=crawl_cfg)
            
            if result.success:
                filename = os.path.join("data", "raw", f"text_source_{i+1}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                print(f"✓ Saved clean text to {filename}")
            else:
                print(f"✗ Failed to crawl {url}: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(scrape_f1_pages())