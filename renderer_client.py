"""
HTTP client for md2pdf renderer service.

Manages Node.js server lifecycle and sends rendering requests.
"""

import os
import subprocess
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class RendererServerError(Exception):
    """Raised when renderer server fails"""
    pass

class RendererTimeoutError(Exception):
    """Raised when renderer request times out"""
    pass

class RendererClient:
    """
    HTTP client for md2pdf renderer service.

    Manages Node.js server lifecycle and sends rendering requests.

    Examples:
        # Manual lifecycle management
        client = RendererClient()
        client.start_server()
        pdf = client.render_pdf("<html>...</html>")
        client.stop_server()

        # Context manager (recommended)
        with RendererClient() as client:
            pdf = client.render_pdf("<html>...</html>")
    """

    def __init__(self, port: int = 3000, timeout: int = 60):
        """
        Initialize renderer client.

        Args:
            port: Port for Node.js server (default: 3000)
            timeout: Request timeout in seconds (default: 60)
        """
        self.port = port
        self.timeout = timeout
        self.server_process = None
        self.base_url = f"http://localhost:{port}"

    def start_server(self, max_retries: int = 10, retry_delay: float = 0.5):
        """
        Start Node.js renderer server.

        Args:
            max_retries: Maximum health check retries (default: 10)
            retry_delay: Delay between retries in seconds (default: 0.5)

        Raises:
            RendererServerError: If server fails to start
        """
        if self.server_process is not None:
            return  # Server already running

        # Find server.js
        server_path = Path(__file__).parent / "renderer" / "server.js"
        if not server_path.exists():
            raise RendererServerError(f"Server not found: {server_path}")

        # Prepare environment (inherit current env + set PORT)
        env = os.environ.copy()
        env['PORT'] = str(self.port)

        # Start Node.js process
        self.server_process = subprocess.Popen(
            ['node', str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        # Wait for server to be ready
        for i in range(max_retries):
            try:
                health = self.health_check()
                if health.get('status') == 'healthy':
                    return  # Server ready
            except (requests.ConnectionError, requests.RequestException):
                pass

            time.sleep(retry_delay)

        # Failed to start
        self.stop_server()
        raise RendererServerError("Server failed to start after retries")

    def stop_server(self):
        """Stop Node.js renderer server."""
        if self.server_process is not None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

            self.server_process = None

    def is_server_running(self) -> bool:
        """
        Check if server is running.

        Returns:
            True if server is running, False otherwise
        """
        if self.server_process is None:
            return False

        # Check if process is alive
        return self.server_process.poll() is None

    def health_check(self) -> Dict[str, Any]:
        """
        Check server health.

        Returns:
            Health check response JSON

        Raises:
            RendererServerError: If health check fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RendererServerError(f"Health check failed: {e}")

    def render_pdf(self, html: str, options: Optional[Dict[str, Any]] = None) -> bytes:
        """
        Render HTML to PDF.

        Args:
            html: HTML content to render
            options: PDF rendering options (optional)

        Returns:
            PDF bytes

        Raises:
            RendererServerError: If rendering fails
            RendererTimeoutError: If request times out
        """
        payload = {
            'html': html,
            'options': options or {}
        }

        try:
            response = requests.post(
                f"{self.base_url}/render/pdf",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.Timeout:
            raise RendererTimeoutError(f"PDF rendering timed out after {self.timeout}s")
        except requests.RequestException as e:
            raise RendererServerError(f"PDF rendering failed: {e}")

    def render_html(self, html: str) -> str:
        """
        Render HTML (passthrough).

        Args:
            html: HTML content

        Returns:
            HTML string

        Raises:
            RendererServerError: If rendering fails
        """
        payload = {'html': html}

        try:
            response = requests.post(
                f"{self.base_url}/render/html",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.Timeout:
            raise RendererTimeoutError(f"HTML rendering timed out after {self.timeout}s")
        except requests.RequestException as e:
            raise RendererServerError(f"HTML rendering failed: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()
        return False
