#!/bin/bash
# Test script for renderer service

echo "=== md2pdf Renderer Service Tests ==="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
curl -s http://localhost:3000/health | jq
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
curl -s http://localhost:3000/ | jq
echo ""

# Test 3: PDF Rendering (simple HTML)
echo "Test 3: PDF Rendering"
curl -X POST http://localhost:3000/render/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Test PDF</h1><p>This is a test.</p></body></html>",
    "options": {}
  }' \
  --output /tmp/test_output.pdf

if [ -f /tmp/test_output.pdf ]; then
    echo "✓ PDF generated: /tmp/test_output.pdf"
    file /tmp/test_output.pdf
else
    echo "✗ PDF generation failed"
fi
echo ""

# Test 4: HTML Rendering
echo "Test 4: HTML Rendering"
curl -X POST http://localhost:3000/render/html \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Test HTML</h1><p>This is a test.</p></body></html>"
  }' \
  --output /tmp/test_output.html

if [ -f /tmp/test_output.html ]; then
    echo "✓ HTML saved: /tmp/test_output.html"
else
    echo "✗ HTML save failed"
fi
echo ""

# Test 5: Error Handling (missing HTML)
echo "Test 5: Error Handling (missing HTML)"
curl -s -X POST http://localhost:3000/render/pdf \
  -H "Content-Type: application/json" \
  -d '{}' | jq
echo ""

echo "=== Tests Complete ==="
