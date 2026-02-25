---
name: web-scraping
description: Web scraping and data extraction covering Cheerio, Puppeteer, Playwright, Beautiful Soup, Scrapy, rate limiting, proxy rotation, anti-bot detection handling, structured data extraction, pagination, and ethical scraping best practices.
---

# Web Scraping & Data Extraction

This skill should be used when building web scrapers, extracting data from websites, or automating web data collection. It covers both static and dynamic page scraping patterns.

## When to Use This Skill

Use this skill when you need to:

- Scrape data from websites
- Extract structured data from HTML
- Handle JavaScript-rendered pages
- Build resilient scraping pipelines
- Respect rate limits and robots.txt
- Parse and transform scraped data

## Cheerio (Static HTML — Fast)

```typescript
import * as cheerio from "cheerio";

async function scrapeProducts(url: string) {
  const response = await fetch(url);
  const html = await response.text();
  const $ = cheerio.load(html);

  const products = $(".product-card").map((_, el) => ({
    name: $(el).find("h2.title").text().trim(),
    price: parseFloat($(el).find(".price").text().replace(/[^0-9.]/g, "")),
    rating: parseFloat($(el).find("[data-rating]").attr("data-rating") ?? "0"),
    url: $(el).find("a").attr("href"),
    image: $(el).find("img").attr("src"),
  })).get();

  return products;
}

// Extract table data
function extractTable($: cheerio.CheerioAPI, selector: string) {
  const headers = $(`${selector} thead th`).map((_, el) => $(el).text().trim()).get();
  const rows = $(`${selector} tbody tr`).map((_, row) => {
    const cells = $(row).find("td").map((_, cell) => $(cell).text().trim()).get();
    return Object.fromEntries(headers.map((h, i) => [h, cells[i]]));
  }).get();
  return rows;
}
```

## Playwright (Dynamic Pages — JavaScript Rendered)

```typescript
import { chromium } from "playwright";

async function scrapeSPA(url: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Block unnecessary resources for speed
  await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,css}", (route) => route.abort());

  await page.goto(url, { waitUntil: "networkidle" });

  // Wait for specific content to load
  await page.waitForSelector(".product-list", { timeout: 10000 });

  // Handle infinite scroll using locators
  for (let i = 0; i < 10; i++) {
    const count = await page.locator(".product-card").count();
    await page.keyboard.press("End");
    await page.waitForTimeout(1000);
    const newCount = await page.locator(".product-card").count();
    if (newCount === count) break;
  }

  // Extract data with $$eval (safe DOM extraction)
  const products = await page.$$eval(".product-card", (cards) =>
    cards.map((card) => ({
      name: card.querySelector("h2")?.textContent?.trim() ?? "",
      price: card.querySelector(".price")?.textContent?.trim() ?? "",
    })),
  );

  await browser.close();
  return products;
}
```

## Python with Beautiful Soup

```python
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from time import sleep

@dataclass
class Article:
    title: str
    url: str
    date: str
    summary: str

def scrape_articles(base_url: str, pages: int = 5) -> list[Article]:
    articles = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0; +https://example.com/bot)"
    })

    for page in range(1, pages + 1):
        response = session.get(f"{base_url}?page={page}", timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for card in soup.select("article.post"):
            articles.append(Article(
                title=card.select_one("h2").get_text(strip=True),
                url=card.select_one("a")["href"],
                date=card.select_one("time")["datetime"],
                summary=card.select_one("p.excerpt").get_text(strip=True),
            ))

        sleep(1)  # Be polite — 1 second between requests
    return articles
```

## Rate Limiting and Politeness

```typescript
// Respectful scraper with rate limiting
class RateLimitedScraper {
  private lastRequest = 0;

  constructor(
    private minDelay: number = 1000,  // 1 second between requests
    private userAgent: string = "MyBot/1.0 (+https://example.com/bot)",
  ) {}

  async fetch(url: string): Promise<string> {
    // Respect rate limit
    const elapsed = Date.now() - this.lastRequest;
    if (elapsed < this.minDelay) {
      await new Promise((r) => setTimeout(r, this.minDelay - elapsed));
    }

    const response = await fetch(url, {
      headers: { "User-Agent": this.userAgent },
    });

    this.lastRequest = Date.now();

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get("retry-after") ?? "60");
      await new Promise((r) => setTimeout(r, retryAfter * 1000));
      return this.fetch(url); // Retry
    }

    if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
    return response.text();
  }
}
```

## Ethical Scraping Checklist

```
BEFORE SCRAPING:
  [ ] Check robots.txt (https://example.com/robots.txt)
  [ ] Review Terms of Service
  [ ] Check if an API exists (prefer API over scraping)
  [ ] Identify yourself with a descriptive User-Agent
  [ ] Include contact info in User-Agent string

WHILE SCRAPING:
  [ ] Rate limit requests (minimum 1 second between)
  [ ] Respect Crawl-delay in robots.txt
  [ ] Handle 429 (Too Many Requests) gracefully
  [ ] Don't scrape behind authentication without permission
  [ ] Cache responses to avoid redundant requests
  [ ] Scrape during off-peak hours when possible

DATA HANDLING:
  [ ] Don't republish copyrighted content
  [ ] Handle personal data per GDPR/CCPA
  [ ] Store only what you need
```

## Additional Resources

- Cheerio: https://cheerio.js.org/
- Playwright: https://playwright.dev/
- Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
- Scrapy: https://scrapy.org/
- robots.txt spec: https://www.robotstxt.org/
