import os
import asyncio

# FORCE ALL SYSTEM ENGINES TO OPERATE OUT OF THE D: DRIVE
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"D:\f1-chatbot\.playwright-browsers"
os.environ["CRAWL4_AI_BASE_DIRECTORY"] = r"D:\f1-chatbot\.crawl4ai"

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def scrape_tech_specs():
    print("====================================================")
    print("STARTING TECHNICAL SPECIFICATIONS & HISTORIC SCRAIPING")
    print("====================================================")
    
    # Targeting engine history regulations and the Indian GP track history
    targets = {
        "engine_history": "https://en.wikipedia.org/wiki/Formula_One_engines",
        "indian_gp_history": "https://en.wikipedia.org/wiki/Indian_Grand_Prix"
    }
    
    RAW_DIR = r"D:\f1-chatbot\data\raw"
    os.makedirs(RAW_DIR, exist_ok=True)

    browser_cfg = BrowserConfig(headless=True, verbose=True)
    crawl_cfg = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for name, url in targets.items():
            print(f"Scraping detailed narrative from: {url}...")
            result = await crawler.arun(url=url, config=crawl_cfg)
            
            if result.success:
                filename = os.path.join(RAW_DIR, f"tech_info_{name}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                print(f"  ✓ Saved technical context to {filename}")
            else:
                print(f"  ✗ Failed to crawl {name}: {result.error_message}")
                
    print("\n====================================================")
    print("EXTRA TECH DATA GATHERING COMPLETE!")
    print("====================================================")

if __name__ == "__main__":
    asyncio.run(scrape_tech_specs())