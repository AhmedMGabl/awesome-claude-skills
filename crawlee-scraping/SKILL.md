---
name: crawlee-scraping
description: Crawlee web scraping framework patterns covering request queues, browser crawlers, Cheerio/Playwright/Puppeteer crawlers, proxy rotation, storage, and anti-blocking strategies.
---

# Crawlee Scraping

This skill should be used when building production web scrapers with Crawlee. It covers crawlers, request queues, proxy rotation, storage, and anti-blocking.

## When to Use This Skill

Use this skill when you need to:

- Build production-grade web scraping pipelines
- Handle request queues and automatic retries
- Rotate proxies and manage anti-blocking
- Store scraped data with built-in storage
- Choose between Cheerio, Playwright, or Puppeteer crawlers

## Setup

```bash
npm install crawlee playwright
npx playwright install
```

## Cheerio Crawler (Static HTML)

```ts
import { CheerioCrawler, Dataset } from "crawlee";

const crawler = new CheerioCrawler({
  maxConcurrency: 5,
  maxRequestRetries: 3,
  requestHandlerTimeoutSecs: 60,

  async requestHandler({ request, $, enqueueLinks, log }) {
    log.info(`Scraping ${request.url}`);

    const products = $(".product-card")
      .toArray()
      .map((el) => ({
        url: request.url,
        title: $(el).find("h3").text().trim(),
        price: $(el).find(".price").text().trim(),
        image: $(el).find("img").attr("src") || "",
      }));

    await Dataset.pushData(products);

    // Follow pagination links
    await enqueueLinks({
      selector: "a.next-page",
      label: "LIST",
    });
  },

  async failedRequestHandler({ request, log }) {
    log.error(`Failed: ${request.url}`);
  },
});

await crawler.run(["https://example.com/products"]);

// Export data
const dataset = await Dataset.open();
await dataset.exportToCSV("products");
```

## Playwright Crawler (Dynamic Pages)

```ts
import { PlaywrightCrawler, Dataset } from "crawlee";

const crawler = new PlaywrightCrawler({
  maxConcurrency: 3,
  headless: true,
  launchContext: {
    launchOptions: {
      args: ["--no-sandbox"],
    },
  },

  async requestHandler({ page, request, enqueueLinks, log }) {
    log.info(`Scraping ${request.url}`);

    // Wait for dynamic content
    await page.waitForSelector(".product-card");

    const products = await page.locator(".product-card").evaluateAll((cards) =>
      cards.map((card) => ({
        title: card.querySelector("h3")?.textContent?.trim() || "",
        price: card.querySelector(".price")?.textContent?.trim() || "",
      }))
    );

    await Dataset.pushData(
      products.map((p) => ({ ...p, url: request.url }))
    );

    await enqueueLinks({ selector: "a.next-page" });
  },
});

await crawler.run(["https://example.com/products"]);
```

## Request Queue Management

```ts
import { CheerioCrawler, RequestQueue } from "crawlee";

const requestQueue = await RequestQueue.open();

// Add requests with metadata
await requestQueue.addRequests([
  {
    url: "https://example.com/page/1",
    userData: { category: "electronics", page: 1 },
    label: "LIST",
  },
  {
    url: "https://example.com/page/2",
    userData: { category: "electronics", page: 2 },
    label: "LIST",
  },
]);

const crawler = new CheerioCrawler({
  requestQueue,
  async requestHandler({ request, $ }) {
    const { category, page } = request.userData;

    if (request.label === "LIST") {
      // Process list page
      $(".product a").each((_, el) => {
        const href = $(el).attr("href");
        if (href) {
          requestQueue.addRequest({
            url: new URL(href, request.url).toString(),
            label: "DETAIL",
            userData: { category },
          });
        }
      });
    }

    if (request.label === "DETAIL") {
      // Process detail page
      const product = {
        title: $("h1").text().trim(),
        description: $(".description").text().trim(),
        category,
      };
      await Dataset.pushData(product);
    }
  },
});

await crawler.run();
```

## Proxy Rotation

```ts
import { CheerioCrawler, ProxyConfiguration } from "crawlee";

const proxyConfiguration = new ProxyConfiguration({
  proxyUrls: [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
  ],
});

const crawler = new CheerioCrawler({
  proxyConfiguration,
  sessionPoolOptions: {
    maxPoolSize: 20,
    sessionOptions: {
      maxUsageCount: 50,
    },
  },
  async requestHandler({ request, $, session }) {
    // Session is automatically rotated on errors
    const data = $("h1").text();
    await Dataset.pushData({ url: request.url, data });
  },
});
```

## Additional Resources

- Crawlee: https://crawlee.dev/
- API: https://crawlee.dev/api/core
- Examples: https://crawlee.dev/docs/examples
