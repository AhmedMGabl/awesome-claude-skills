---
name: playwright-scraping
description: Playwright web scraping patterns covering multi-browser automation, locator strategies, network interception, stealth mode, pagination handling, and data extraction workflows.
---

# Playwright Scraping

This skill should be used when building web scrapers with Playwright. It covers locators, network interception, stealth mode, pagination, and data extraction.

## When to Use This Skill

Use this skill when you need to:

- Scrape JavaScript-rendered dynamic pages
- Automate multi-browser data extraction
- Handle pagination and infinite scroll
- Intercept API responses for data capture
- Build resilient scraping pipelines

## Setup

```bash
npm install playwright
npx playwright install
```

## Basic Scraping

```ts
import { chromium } from "playwright";

async function scrapeProducts(url: string) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    viewport: { width: 1280, height: 720 },
  });

  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });

  // Wait for content to load
  await page.waitForSelector(".product-card");

  const products = await page.locator(".product-card").evaluateAll((cards) =>
    cards.map((card) => ({
      title: card.querySelector("h3")?.textContent?.trim() || "",
      price: card.querySelector(".price")?.textContent?.trim() || "",
      image: card.querySelector("img")?.getAttribute("src") || "",
    }))
  );

  await browser.close();
  return products;
}
```

## Locator-Based Extraction

```ts
async function extractWithLocators(page: any) {
  // Text content
  const title = await page.locator("h1").textContent();

  // Attribute
  const imgSrc = await page.locator(".hero img").getAttribute("src");

  // Multiple elements
  const links = await page.locator("nav a").all();
  const navItems = await Promise.all(
    links.map(async (link: any) => ({
      text: await link.textContent(),
      href: await link.getAttribute("href"),
    }))
  );

  // Inner HTML
  const html = await page.locator(".content").innerHTML();

  // Input value
  const value = await page.locator("input#search").inputValue();

  return { title, imgSrc, navItems, html, value };
}
```

## Pagination Handling

```ts
async function scrapeAllPages(baseUrl: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const allItems: any[] = [];

  let currentPage = 1;
  let hasNext = true;

  while (hasNext) {
    await page.goto(`${baseUrl}?page=${currentPage}`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".item");

    const items = await page.locator(".item").evaluateAll((nodes) =>
      nodes.map((n) => ({
        title: n.querySelector("h3")?.textContent?.trim() || "",
        description: n.querySelector("p")?.textContent?.trim() || "",
      }))
    );

    allItems.push(...items);

    // Check for next page
    hasNext = (await page.locator("a.next-page").count()) > 0;
    currentPage++;
  }

  await browser.close();
  return allItems;
}
```

## Infinite Scroll

```ts
async function scrapeInfiniteScroll(url: string, maxScrolls = 10) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });

  let previousHeight = 0;
  let scrollCount = 0;

  while (scrollCount < maxScrolls) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000);

    const newHeight = await page.evaluate(() => document.body.scrollHeight);
    if (newHeight === previousHeight) break;
    previousHeight = newHeight;
    scrollCount++;
  }

  const items = await page.locator(".feed-item").evaluateAll((nodes) =>
    nodes.map((n) => n.textContent?.trim() || "")
  );

  await browser.close();
  return items;
}
```

## Network Response Capture

```ts
async function captureAPIData(url: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const apiData: any[] = [];

  // Listen for API responses
  page.on("response", async (response) => {
    if (response.url().includes("/api/products") && response.status() === 200) {
      try {
        const json = await response.json();
        apiData.push(...(json.data || []));
      } catch {}
    }
  });

  await page.goto(url, { waitUntil: "networkidle" });
  await browser.close();
  return apiData;
}
```

## Additional Resources

- Playwright: https://playwright.dev/
- Locators: https://playwright.dev/docs/locators
- API: https://playwright.dev/docs/api/class-page
