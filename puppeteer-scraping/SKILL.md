---
name: puppeteer-scraping
description: Puppeteer browser automation covering page navigation, element selection, form filling, screenshot capture, PDF generation, network interception, stealth mode, cookie management, and headless Chrome scripting. This skill should be used when automating Chrome/Chromium with Puppeteer for scraping, screenshot capture, PDF rendering, or any scripted browser interaction.
---

# Puppeteer Scraping & Browser Automation

This skill should be used when automating Chrome/Chromium with Puppeteer. It covers browser setup, navigation, interaction, screenshots, PDFs, network interception, stealth mode, and Docker deployment.

## When to Use This Skill

Use this skill when you need to:

- Scrape JavaScript-rendered pages
- Automate form filling and submission
- Capture full-page screenshots or generate PDFs
- Intercept and modify network requests
- Manage cookies and authenticated sessions
- Bypass basic bot detection with stealth mode

## Browser and Page Setup

```typescript
import puppeteer, { Browser, Page } from "puppeteer";

async function createBrowser(): Promise<Browser> {
  return puppeteer.launch({
    headless: "new",              // Use new headless mode
    args: [
      "--no-sandbox",             // Required in Docker/CI
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",  // Prevent /dev/shm OOM in containers
      "--disable-gpu",
    ],
  });
}

async function newPage(browser: Browser): Promise<Page> {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.setUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
  );
  return page;
}
```

## Navigation and Waiting Strategies

```typescript
// Navigate and wait for network to settle
await page.goto("https://example.com", { waitUntil: "networkidle2" });

// Wait for a selector before interacting
await page.waitForSelector(".product-list", { timeout: 10_000 });

// Wait for a function to return truthy in the browser context
await page.waitForFunction(() => document.querySelectorAll(".item").length > 5);

// Block images and fonts to speed up scraping
await page.setRequestInterception(true);
page.on("request", (req) => {
  if (["image", "font", "stylesheet"].includes(req.resourceType())) {
    req.abort();
  } else {
    req.continue();
  }
});
```

## Element Selection and Interaction

```typescript
await page.click('button[type="submit"]');
await page.type("#search", "laptops", { delay: 50 }); // realistic keystroke delay

// page.$$eval / page.$eval run a callback inside the browser context
const titles = await page.$$eval("h2.product-title", (els) =>
  els.map((el) => el.textContent?.trim() ?? "")
);
const price = await page.$eval(".price", (el) =>
  parseFloat(el.textContent!.replace(/[^0-9.]/g, ""))
);

// Scroll to trigger lazy loading
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
```

## Form Filling and Submission

```typescript
async function fillAndSubmit(page: Page, url: string) {
  await page.goto(url, { waitUntil: "networkidle2" });

  await page.type("#email", "user@example.com");
  await page.type("#password", "secret");

  // Select a dropdown option
  await page.select("#country", "US");

  // Check a checkbox
  await page.click('input[name="terms"]');

  // Submit and wait for navigation to complete
  await Promise.all([
    page.waitForNavigation({ waitUntil: "networkidle2" }),
    page.click('button[type="submit"]'),
  ]);
}
```

## Screenshots and PDF Generation

```typescript
// Full-page screenshot
await page.screenshot({ path: "page.png", fullPage: true, type: "png" });

// Clip a specific element
const el = await page.$(".hero-banner");
await page.screenshot({ path: "hero.png", clip: await el!.boundingBox()! });

// PDF (headless only)
await page.emulateMediaType("screen");
await page.pdf({
  path: "report.pdf",
  format: "A4",
  printBackground: true,
  margin: { top: "20mm", bottom: "20mm", left: "15mm", right: "15mm" },
});
```

## Network Request Interception

```typescript
// Modify request headers (e.g., inject auth token)
await page.setRequestInterception(true);
page.on("request", (req) => {
  req.continue({
    headers: { ...req.headers(), Authorization: "Bearer TOKEN" },
  });
});

// Capture API responses
page.on("response", async (res) => {
  if (res.url().includes("/api/products") && res.status() === 200) {
    const data = await res.json();
    console.log("Intercepted products:", data);
  }
});
```

## Cookie and Session Management

```typescript
import fs from "fs/promises";

async function saveSession(page: Page, file: string) {
  await fs.writeFile(file, JSON.stringify(await page.cookies(), null, 2));
}

async function loadSession(page: Page, file: string) {
  const cookies = JSON.parse(await fs.readFile(file, "utf-8"));
  await page.setCookie(...cookies);
}

// Restore session, navigate (already authenticated), then persist
await loadSession(page, "session.json");
await page.goto("https://example.com/dashboard");
await saveSession(page, "session.json");
```

## Stealth Mode with puppeteer-extra

```typescript
// npm install puppeteer-extra puppeteer-extra-plugin-stealth
import puppeteer from "puppeteer-extra";
import StealthPlugin from "puppeteer-extra-plugin-stealth";

puppeteer.use(StealthPlugin()); // patches dozens of bot-detection signals

const browser = await puppeteer.launch({ headless: "new" });
const page = await browser.newPage();
// Manually patch navigator.webdriver if not using the plugin
await page.evaluateOnNewDocument(() => {
  Object.defineProperty(navigator, "webdriver", { get: () => false });
});
```

## Error Handling and Retry Patterns

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  retries = 3,
  delayMs = 1500
): Promise<T> {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === retries) throw err;
      console.warn(`Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw new Error("Unreachable");
}

async function scrape(url: string) {
  const browser = await createBrowser();
  try {
    const page = await newPage(browser);
    return await withRetry(() => scrapePage(page, url));
  } finally {
    await browser.close(); // Always close, even on error
  }
}
```

## Running in Docker

```dockerfile
FROM node:20-slim

# Install Chromium and its dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["node", "dist/scraper.js"]
```

## Additional Resources

- Puppeteer API docs: https://pptr.dev/api
- puppeteer-extra stealth plugin: https://github.com/berstend/puppeteer-extra
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
