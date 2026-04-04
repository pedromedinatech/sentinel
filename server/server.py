import asyncio
from shared.config import HOST, PORT
from shared.logger import get_logger
from server.registry import Registry
from server.event_bus import EventBus
from server.client_handler import ClientHandler
from monitor.monitor import Monitor

logger = get_logger(__name__)

registry = Registry()
event_bus = EventBus()

monitor = Monitor()
event_bus.subscribe("anomaly", monitor.on_anomaly)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Callback invoked by asyncio for each new incoming connection.
    Creates a ClientHandler and delegates the full client lifecycle to it.
    """

    handler = ClientHandler(reader, writer, registry, event_bus)

    await handler.handle()

async def main() -> None: 
    """
    Start the server and run the event loop indefinitely.
    """

    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    logger.info(f"sentinel server listening on {addr[0]}:{addr[1]}")

    async with server:

        await server.serve_forever()


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("server stopped by user")