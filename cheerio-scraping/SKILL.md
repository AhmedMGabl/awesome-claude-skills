---
name: cheerio-scraping
description: Cheerio web scraping patterns covering HTML parsing, jQuery-style selectors, DOM traversal, data extraction, form parsing, table scraping, and Node.js integration.
---

# Cheerio Scraping

This skill should be used when scraping static HTML with Cheerio. It covers selectors, DOM traversal, data extraction, form parsing, and table scraping.

## When to Use This Skill

Use this skill when you need to:

- Parse and extract data from static HTML pages
- Use jQuery-style selectors for DOM querying
- Scrape tables, lists, and structured data
- Build fast, lightweight scraping pipelines
- Process HTML without a browser engine

## Setup

```bash
npm install cheerio
```

## Basic Scraping

```ts
import * as cheerio from "cheerio";

async function scrapeProducts(url: string) {
  const response = await fetch(url);
  const html = await response.text();
  const $ = cheerio.load(html);

  const products: { title: string; price: string; link: string }[] = [];

  $(".product-card").each((_, element) => {
    products.push({
      title: $(element).find("h3").text().trim(),
      price: $(element).find(".price").text().trim(),
      link: $(element).find("a").attr("href") || "",
    });
  });

  return products;
}
```

## Selector Patterns

```ts
const $ = cheerio.load(html);

// Basic selectors
const title = $("h1").text();
const links = $("a").toArray().map((el) => $(el).attr("href"));
const classes = $(".container .item").length;
const ids = $("#main-content").html();

// Attribute selectors
const images = $("img[src]").toArray().map((el) => $(el).attr("src"));
const externalLinks = $('a[href^="https://"]').toArray().map((el) => ({
  text: $(el).text().trim(),
  href: $(el).attr("href"),
}));

// Pseudo selectors
const firstItem = $("li:first-child").text();
const lastItem = $("li:last-child").text();
const nthItem = $("li:nth-child(3)").text();
const hasChild = $("div:has(> img)").length;

// Traversal
const parent = $(".child").parent();
const siblings = $(".active").siblings();
const nextEl = $(".current").next();
const prevEl = $(".current").prev();
const closest = $(".deep-child").closest(".wrapper");
```

## Table Scraping

```ts
function scrapeTable($: cheerio.CheerioAPI, selector: string) {
  const headers: string[] = [];
  const rows: Record<string, string>[] = [];

  // Extract headers
  $(`${selector} thead th`).each((_, th) => {
    headers.push($(th).text().trim());
  });

  // Extract rows
  $(`${selector} tbody tr`).each((_, tr) => {
    const row: Record<string, string> = {};
    $(tr).find("td").each((i, td) => {
      row[headers[i] || `col_${i}`] = $(td).text().trim();
    });
    rows.push(row);
  });

  return { headers, rows };
}
```

## Paginated Scraping

```ts
async function scrapeAllPages(baseUrl: string) {
  const allItems: any[] = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await fetch(`${baseUrl}?page=${page}`);
    const html = await response.text();
    const $ = cheerio.load(html);

    $(".item").each((_, el) => {
      allItems.push({
        title: $(el).find("h3").text().trim(),
        description: $(el).find("p").text().trim(),
      });
    });

    hasMore = $("a.next-page").length > 0;
    page++;

    // Rate limiting
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  return allItems;
}
```

## Content Manipulation

```ts
const $ = cheerio.load(html);

// Remove unwanted elements
$("script, style, nav, footer, .ads").remove();

// Get clean text
const cleanText = $("article").text().replace(/\s+/g, " ").trim();

// Modify attributes
$("img").each((_, img) => {
  const src = $(img).attr("src");
  if (src && !src.startsWith("http")) {
    $(img).attr("src", `https://example.com${src}`);
  }
});

// Get modified HTML
const modifiedHtml = $.html();
```

## Additional Resources

- Cheerio: https://cheerio.js.org/
- API: https://cheerio.js.org/docs/api
- Selectors: https://cheerio.js.org/docs/basics/selecting
