// Renders HTML files to PDF with the pre-installed Chromium.
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const files = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();
  for (const f of files) {
    const abs = path.resolve(f);
    await page.goto('file://' + abs, { waitUntil: 'networkidle' });
    await page.emulateMedia({ media: 'print' });
    const out = abs.replace(/\.html$/, '.pdf');
    await page.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' },
      displayHeaderFooter: true, headerTemplate: '<div></div>',
      footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;font-family:Arial">Infinity Story · <span class="title"></span> · page <span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
    console.log('ok', out);
  }
  await browser.close();
})();
