import asyncio
from shared.config import HOST, PORT
from shared.logger import get_logger
from server.registry import Registry
from server.event_bus import EventBus
from server.client_handler import ClientHandler
from monitor.monitor import Monitor
from dashboard.ws_manager import WebSocketManager
from dashboard.ws_server import WebSocketServer
from dashboard.http_server import start as start_http   
from dashboard.client_controller import ClientController
from dashboard.anomaly_injector import AnomalyInjector
from client.psutil_client import PsutilClient

logger = get_logger(__name__)

registry = Registry()
event_bus = EventBus()

monitor = Monitor()
event_bus.subscribe("anomaly", monitor.on_anomaly)

ws_manager = WebSocketManager()
event_bus.subscribe("anomaly", ws_manager.on_anomaly)
event_bus.subscribe("reading", ws_manager.on_reading)
event_bus.subscribe("connection", ws_manager.on_connection)

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

    client_controller = ClientController()
    ws_server = WebSocketServer(ws_manager, client_controller)
    anomaly_injector = AnomalyInjector()

    cpu_client = PsutilClient(sensor_id="cpu_real", sensor_type="cpu", interval=2.0)
    ram_client = PsutilClient(sensor_id="ram_real", sensor_type="ram", interval=2.0)
    disk_client = PsutilClient(sensor_id="disk_real", sensor_type="disk", interval=2.0)
    network_client = PsutilClient(sensor_id="network_real", sensor_type="network", interval=2.0)

    server = await asyncio.start_server(handle_client, HOST, PORT)

    addr = server.sockets[0].getsockname()
    logger.info(f"sentinel server listening on {addr[0]}:{addr[1]}")

    async with server:
        await asyncio.gather(
            server.serve_forever(),
            ws_server.start(),
            start_http(),
            anomaly_injector.run(),
            cpu_client.run(),
            ram_client.run(),
            disk_client.run(),
            network_client.run()
        )


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("server stopped by user")