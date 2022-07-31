import asyncio
import os

os.environ["PYTHONASYNCIODEBUG"] = "1"

import sys
import logging

from player import Player
from world import World
from tools import bold

logger = logging.getLogger(__name__)
__all__ = ("Server",)


class Server:
    def __init__(self, host="127.0.0.1", port=25565) -> None:
        self.server = None
        self.world = World()
        self.loop = asyncio.new_event_loop()

        self.host = host
        self.port = port

        asyncio.set_event_loop(self.loop)
        self.world.make()

    async def __call__(self, reader, writer):
        player = await Player.login(reader, writer, self.world)
        self.world.players.append(player)

        asyncio.create_task(player.loop())
        await self.world.send_chunks(player)

    def assign_id(self):
        return len(self.world.players) + 1

    async def global_disconnect(self):
        for player in self.world.players:
            await player.disconnect()

    async def start(self):
        self.server = await asyncio.start_server(self, self.host, self.port)
        addrs = ", ".join(str(sock.getsockname()) for sock in self.server.sockets)
        logger.debug(f"STARTED SERVING ON {bold(addrs)}")

        async with self.server:
            await self.server.wait_closed()

    def shutdown(self):
        sh_items = [self.global_disconnect, self.loop.shutdown_asyncgens]

        if sys.version_info.minor > 8:
            sh_items.append(self.loop.shutdown_default_executor)

        for task in asyncio.all_tasks(loop=self.loop):
            task.cancel()

            try:
                self.loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass

        for item in sh_items:
            self.loop.run_until_complete(item())

        self.server.close()
        self.loop.close()

        logger.debug("SHUTDOWN COMPLETE.")
        logger.debug(
            f"RESOURCE STATUS: \n{bold('CLIENTS')}: {self.world.players} \n{bold('LOOP')}: {self.loop} \n{bold('SERVER')}: {self.server}"
        )

    def serve(self):
        self.loop.run_until_complete(self.start())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    server = Server()
    server.loop.set_debug(True)

    try:
        server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
