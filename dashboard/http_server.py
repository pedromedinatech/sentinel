import asyncio
from pathlib import Path
from shared.logger import get_logger

logger = get_logger(__name__)

DASHBOARD_PATH = Path(__file__).parent / "dashboard.html"
HOST = "localhost"
PORT = 8080

async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Serve dashboard.html for any incoming HTTP request."""

    await reader.read(4096)

    try:
        html = DASHBOARD_PATH.read_bytes()
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        ) + html
    except FileNotFoundError:
        response = (
            b"HTTP/1.1 404 Not Found\r\n"
            b"Content-Type: text/plain\r\n"
            b"\r\n"
            b"dashboard.html not found"
        )

    writer.write(response)
    await writer.drain()
    writer.close()

async def start() -> None:
    """Start the HTTP server."""
    
    server = await asyncio.start_server(_handle, HOST, PORT)
    logger.info(f"Dashboard available at http://{HOST}:{PORT}")
    async with server:
        await server.serve_forever()