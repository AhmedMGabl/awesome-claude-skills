---
name: puppeteer-automation
description: Puppeteer browser automation patterns covering page navigation, element interaction, screenshots, PDF generation, network interception, web scraping, and testing workflows.
---

# Puppeteer Automation

This skill should be used when automating browser tasks with Puppeteer. It covers navigation, interaction, screenshots, PDFs, network interception, and scraping.

## When to Use This Skill

Use this skill when you need to:

- Automate browser interactions and form submissions
- Take screenshots and generate PDFs
- Scrape dynamic JavaScript-rendered pages
- Intercept and modify network requests
- Build end-to-end testing workflows

## Setup

```bash
npm install puppeteer
# Or for lighter install without bundled Chromium:
npm install puppeteer-core
```

## Basic Navigation and Interaction

```ts
import puppeteer from "puppeteer";

async function automateLogin() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 720 });

  await page.goto("https://example.com/login", { waitUntil: "networkidle0" });

  // Fill form
  await page.type("#username", "user@example.com", { delay: 50 });
  await page.type("#password", "password123", { delay: 50 });

  // Click and wait for navigation
  await Promise.all([
    page.waitForNavigation({ waitUntil: "networkidle0" }),
    page.click('button[type="submit"]'),
  ]);

  console.log("Current URL:", page.url());
  await browser.close();
}
```

## Screenshots and PDFs

```ts
async function captureContent(url: string) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "networkidle0" });

  // Full page screenshot
  await page.screenshot({
    path: "screenshot.png",
    fullPage: true,
  });

  // Element screenshot
  const element = await page.$(".main-content");
  if (element) {
    await element.screenshot({ path: "element.png" });
  }

  // PDF generation
  await page.pdf({
    path: "output.pdf",
    format: "A4",
    margin: { top: "1cm", right: "1cm", bottom: "1cm", left: "1cm" },
    printBackground: true,
  });

  await browser.close();
}
```

## Web Scraping

```ts
async function scrapeProducts(url: string) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });

  // Wait for dynamic content
  await page.waitForSelector(".product-card");

  const products = await page.evaluate(() => {
    return Array.from(document.querySelectorAll(".product-card")).map((card) => ({
      title: card.querySelector("h3")?.textContent?.trim() || "",
      price: card.querySelector(".price")?.textContent?.trim() || "",
      image: card.querySelector("img")?.getAttribute("src") || "",
      link: card.querySelector("a")?.getAttribute("href") || "",
    }));
  });

  await browser.close();
  return products;
}
```

## Network Interception

```ts
async function interceptRequests(url: string) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Enable request interception
  await page.setRequestInterception(true);

  page.on("request", (request) => {
    // Block images and stylesheets for faster scraping
    if (["image", "stylesheet", "font"].includes(request.resourceType())) {
      request.abort();
    } else {
      request.continue();
    }
  });

  // Capture API responses
  page.on("response", async (response) => {
    if (response.url().includes("/api/")) {
      try {
        const data = await response.json();
        console.log("API response:", response.url(), data);
      } catch {}
    }
  });

  await page.goto(url, { waitUntil: "networkidle0" });
  await browser.close();
}
```

## Waiting Strategies

```ts
// Wait for selector
await page.waitForSelector(".loaded", { timeout: 10000 });

// Wait for function
await page.waitForFunction(
  () => document.querySelectorAll(".item").length > 5,
  { timeout: 10000 }
);

// Wait for navigation
await page.waitForNavigation({ waitUntil: "networkidle0" });

// Wait for network response
const response = await page.waitForResponse(
  (res) => res.url().includes("/api/data") && res.status() === 200
);
```

## Additional Resources

- Puppeteer: https://pptr.dev/
- API: https://pptr.dev/api
- Guides: https://pptr.dev/guides
