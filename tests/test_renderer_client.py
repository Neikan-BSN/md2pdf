import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from renderer_client import RendererClient, RendererServerError, RendererTimeoutError

def test_renderer_client_init():
    """Test RendererClient initialization"""
    client = RendererClient()
    assert client.port == 3000
    assert client.timeout == 60
    assert client.server_process is None

def test_start_server():
    """Test starting the Node.js server"""
    client = RendererClient()

    # Start server
    client.start_server()

    # Verify server is running
    assert client.server_process is not None
    assert client.is_server_running()

    # Cleanup
    client.stop_server()

def test_health_check():
    """Test health check endpoint"""
    client = RendererClient()
    client.start_server()

    # Should return healthy status
    health = client.health_check()
    assert health['status'] == 'healthy'
    assert health['service'] == 'md2pdf-renderer'

    client.stop_server()

def test_render_pdf():
    """Test PDF rendering"""
    client = RendererClient()
    client.start_server()

    html = "<html><body><h1>Test</h1></body></html>"
    pdf_bytes = client.render_pdf(html)

    # Verify PDF header
    assert pdf_bytes.startswith(b'%PDF-')
    assert len(pdf_bytes) > 0

    client.stop_server()

def test_render_html():
    """Test HTML rendering"""
    client = RendererClient()
    client.start_server()

    html = "<html><body><h1>Test</h1></body></html>"
    html_output = client.render_html(html)

    assert '<h1>Test</h1>' in html_output
    assert isinstance(html_output, str)

    client.stop_server()

def test_stop_server():
    """Test stopping the server"""
    client = RendererClient()
    client.start_server()

    assert client.is_server_running()

    client.stop_server()

    assert not client.is_server_running()
    assert client.server_process is None

def test_context_manager():
    """Test using client as context manager"""
    with RendererClient() as client:
        assert client.is_server_running()

        html = "<html><body><h1>Test</h1></body></html>"
        pdf = client.render_pdf(html)
        assert pdf.startswith(b'%PDF-')

    # Server should be stopped after exiting context
    assert not client.is_server_running()

def test_render_pdf_with_options():
    """Test PDF rendering with custom options"""
    client = RendererClient()
    client.start_server()

    html = "<html><body><h1>Test</h1></body></html>"
    options = {
        'pageSize': 'A4',
        'margins': {'top': '2cm', 'bottom': '2cm', 'left': '2cm', 'right': '2cm'},
        'printBackground': True
    }

    pdf_bytes = client.render_pdf(html, options)
    assert pdf_bytes.startswith(b'%PDF-')

    client.stop_server()
