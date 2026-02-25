---
name: pdf-generation
description: PDF generation and manipulation covering Puppeteer/Playwright HTML-to-PDF, pdf-lib for programmatic creation, React-PDF for templating, invoice and report layouts, headers/footers, watermarks, table of contents, and Python ReportLab patterns for server-side document generation.
---

# PDF Generation

This skill should be used when generating, manipulating, or processing PDF documents programmatically. It covers HTML-to-PDF conversion, programmatic creation, and document templating.

## When to Use This Skill

Use this skill when you need to:

- Generate invoices, reports, or certificates as PDF
- Convert HTML pages to PDF
- Programmatically create PDFs with text, images, and tables
- Add watermarks, headers, and footers
- Merge, split, or modify existing PDFs

## HTML to PDF with Playwright

```typescript
import { chromium } from "playwright";

async function htmlToPdf(html: string, options?: { landscape?: boolean }) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.setContent(html, { waitUntil: "networkidle" });

  const pdf = await page.pdf({
    format: "A4",
    landscape: options?.landscape ?? false,
    printBackground: true,
    margin: { top: "1cm", bottom: "1.5cm", left: "1cm", right: "1cm" },
    displayHeaderFooter: true,
    headerTemplate: `
      <div style="font-size:9px;color:#666;width:100%;text-align:center;padding:5px;">
        <span>Company Name — Confidential</span>
      </div>`,
    footerTemplate: `
      <div style="font-size:9px;color:#666;width:100%;padding:5px 20px;display:flex;justify-content:space-between;">
        <span>Generated <span class="date"></span></span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
      </div>`,
  });

  await browser.close();
  return pdf; // Buffer
}

// Invoice HTML template
function invoiceTemplate(data: InvoiceData): string {
  return `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Helvetica Neue', sans-serif; color: #333; margin: 0; padding: 40px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #f8f9fa; text-align: left; padding: 10px; border-bottom: 2px solid #dee2e6; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .total-row td { font-weight: bold; border-top: 2px solid #333; }
    .header { display: flex; justify-content: space-between; margin-bottom: 40px; }
    .amount { text-align: right; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1 style="margin:0;color:#2563eb;">INVOICE</h1>
      <p>#${data.invoiceNumber}</p>
    </div>
    <div style="text-align:right;">
      <strong>${data.company.name}</strong><br/>
      ${data.company.address}<br/>
      ${data.company.email}
    </div>
  </div>

  <div style="margin-bottom:30px;">
    <strong>Bill To:</strong><br/>
    ${data.customer.name}<br/>
    ${data.customer.address}
  </div>

  <table>
    <thead>
      <tr><th>Item</th><th>Qty</th><th class="amount">Price</th><th class="amount">Total</th></tr>
    </thead>
    <tbody>
      ${data.items.map((item) => `
        <tr>
          <td>${item.description}</td>
          <td>${item.quantity}</td>
          <td class="amount">$${item.unitPrice.toFixed(2)}</td>
          <td class="amount">$${(item.quantity * item.unitPrice).toFixed(2)}</td>
        </tr>`).join("")}
      <tr class="total-row">
        <td colspan="3">Total</td>
        <td class="amount">$${data.total.toFixed(2)}</td>
      </tr>
    </tbody>
  </table>

  <p style="color:#666;font-size:12px;margin-top:40px;">
    Payment due within ${data.paymentTerms} days. Thank you for your business.
  </p>
</body>
</html>`;
}
```

## Programmatic PDF with pdf-lib

```typescript
import { PDFDocument, rgb, StandardFonts } from "pdf-lib";

async function createReport(data: ReportData): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const boldFont = await doc.embedFont(StandardFonts.HelveticaBold);

  // Title page
  const titlePage = doc.addPage([595, 842]); // A4
  titlePage.drawText(data.title, {
    x: 50, y: 742, size: 28, font: boldFont, color: rgb(0.15, 0.15, 0.15),
  });
  titlePage.drawText(`Generated: ${new Date().toLocaleDateString()}`, {
    x: 50, y: 710, size: 12, font, color: rgb(0.5, 0.5, 0.5),
  });

  // Content pages
  let yPos = 750;
  let page = doc.addPage([595, 842]);

  for (const section of data.sections) {
    if (yPos < 100) {
      page = doc.addPage([595, 842]);
      yPos = 750;
    }

    // Section header
    page.drawText(section.title, { x: 50, y: yPos, size: 16, font: boldFont });
    yPos -= 25;

    // Section content (simple line wrapping)
    const lines = wrapText(section.content, font, 12, 495);
    for (const line of lines) {
      if (yPos < 60) {
        page = doc.addPage([595, 842]);
        yPos = 750;
      }
      page.drawText(line, { x: 50, y: yPos, size: 12, font });
      yPos -= 18;
    }
    yPos -= 20;
  }

  return doc.save();
}

// Add watermark to existing PDF
async function addWatermark(pdfBytes: Uint8Array, text: string): Promise<Uint8Array> {
  const doc = await PDFDocument.load(pdfBytes);
  const font = await doc.embedFont(StandardFonts.HelveticaBold);

  for (const page of doc.getPages()) {
    const { width, height } = page.getSize();
    page.drawText(text, {
      x: width / 4, y: height / 2,
      size: 60, font, color: rgb(0.9, 0.9, 0.9),
      rotate: { type: "degrees" as any, angle: 45 },
      opacity: 0.3,
    });
  }

  return doc.save();
}
```

## Python ReportLab

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_invoice(data: dict, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Invoice #{data['number']}", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Items table
    table_data = [["Item", "Qty", "Price", "Total"]]
    for item in data["items"]:
        total = item["qty"] * item["price"]
        table_data.append([item["desc"], str(item["qty"]), f"${item['price']:.2f}", f"${total:.2f}"])

    table_data.append(["", "", "Total:", f"${data['total']:.2f}"])

    table = Table(table_data, colWidths=[250, 60, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    elements.append(table)
    doc.build(elements)
```

## Additional Resources

- pdf-lib: https://pdf-lib.js.org/
- Playwright PDF: https://playwright.dev/docs/api/class-page#page-pdf
- React-PDF: https://react-pdf.org/
- ReportLab: https://www.reportlab.com/docs/reportlab-userguide.pdf
