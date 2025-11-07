const express = require('express');
const bodyParser = require('body-parser');
const puppeteer = require('puppeteer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '50mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'md2pdf-renderer',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'md2pdf Renderer Service',
        endpoints: {
            'GET /health': 'Health check',
            'POST /render/pdf': 'Render HTML to PDF',
            'POST /render/html': 'Save HTML file'
        }
    });
});

// PDF rendering endpoint
app.post('/render/pdf', async (req, res) => {
    const { html, options = {} } = req.body;

    if (!html) {
        return res.status(400).json({
            error: 'Missing required field: html'
        });
    }

    let browser = null;

    try {
        // Launch Puppeteer
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        // Set HTML content
        await page.setContent(html, {
            waitUntil: ['networkidle0', 'domcontentloaded']
        });

        // Wait for rendering (Mermaid, KaTeX)
        const waitTime = options.waitForRendering || 1000;
        await new Promise(resolve => setTimeout(resolve, waitTime));

        // PDF options
        const pdfOptions = {
            format: options.pageSize || 'Letter',
            printBackground: options.printBackground !== false,
            margin: options.margins || {
                top: '1in',
                bottom: '1in',
                left: '1in',
                right: '1in'
            }
        };

        // Generate PDF
        const pdfBuffer = await page.pdf(pdfOptions);

        // Close browser
        await browser.close();

        // Send PDF as response
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Length', pdfBuffer.length);
        res.end(pdfBuffer, 'binary');

    } catch (error) {
        console.error('PDF rendering error:', error);

        if (browser) {
            await browser.close();
        }

        res.status(500).json({
            error: 'PDF rendering failed',
            message: error.message
        });
    }
});

// HTML rendering endpoint (saves HTML)
app.post('/render/html', async (req, res) => {
    const { html } = req.body;

    if (!html) {
        return res.status(400).json({
            error: 'Missing required field: html'
        });
    }

    try {
        // For HTML output, just return the HTML
        // Python client will save it to file
        res.contentType('text/html');
        res.send(html);

    } catch (error) {
        console.error('HTML rendering error:', error);

        res.status(500).json({
            error: 'HTML rendering failed',
            message: error.message
        });
    }
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Endpoint ${req.method} ${req.path} not found`
    });
});

// Error handler middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);

    res.status(500).json({
        error: 'Internal Server Error',
        message: err.message
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`✓ md2pdf renderer service listening on port ${PORT}`);
    console.log(`  Health check: http://localhost:${PORT}/health`);
});

module.exports = app;  // For testing
