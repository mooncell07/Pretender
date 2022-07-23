__all__ = ("World",)
import logging
import gzip
import io
import struct
import asyncio
<<<<<<< HEAD
import random 
=======
import random

>>>>>>> 1c7966fdd128aea0bf54d679e85ef0cd4c91c73b
from packet import Packet
from tools import bold, cbold

logger = logging.getLogger(__name__)


class World:
    def __init__(self) -> None:
        self.chunks = None
        self.players = []

    def make(self):
        buffer = io.BytesIO()
        data = bytearray(256 * 256 * 64)

        with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=9) as f:
            f.write(struct.pack("!I", len(data)) + bytes(data))

        world = buffer.getvalue()
        self.chunks = [world[i : i + 1024] for i in range(0, len(world), 1024)]
        logger.debug("Completed building the world.")

    async def send_chunks(self, player):
        packet = Packet("BhAB")
        await self._init(player)

        logger.debug(f"{bold('0x03')}: Sending chunks to {cbold(player.name)}.")
        for num, chunk in enumerate(self.chunks):
            await player.send(
                packet.serialize(0x03, len(chunk), chunk, len(self.chunks) // (num + 1))
            )


        await self._spawn_player(player, 0, 0, 80, 35, 70)


        await self._finalize(player)

        spawn_player = Packet("BbChhhBB")
        spawn_player = spawn_player.serialize(
            0x07,
            random.randint(1, 128), # TODO: change the player id to dynamically allocate
            player.name,
            128 * 32, 33 * 32, 128 * 32,
            0, 0
        )

        for other_player in self.players:
            if other_player is not player:
                logger.debug(f"{bold('0x07')}: Sending {cbold(player.name)} to {cbold(other_player.name)}.")
                await other_player.send(spawn_player)

        self.players.append(player)
        
        asyncio.create_task(self._set_block_player(player))


    async def _finalize(self, player):
        packet = Packet("Bhhh")
        await player.send(packet.serialize(0x04, 256, 64, 256))
        logger.debug(
            f"{bold('0x04')}: Finalization complete; {cbold(player.name)} joined the game."
        )

    async def _init(self, player):
        packet = Packet("B")
        payload = packet.serialize(0x02)

        await player.send(payload)
        logger.debug(
            f"{bold('0x02')}: Notification sent for level chunking startup to {cbold(player.name)}."
        )

    async def _set_block_player(self, player):
        while not player.is_closing:
            payload = await player.reader.read(255)
            packet = Packet("BhhhBB")
            packetview = packet.deserialize(payload)
            cords = [c[0] for c in packetview["h"]]

            await self._set_block_server(
                player,
                cords[0],
                cords[1],
                cords[2],
                int.from_bytes(packetview["B"][2], "big"),
            )

    async def _set_block_server(self, player, x, y, z, btype):
        packet = Packet("BhhhB")
        await player.send(
            packet.serialize(0x06, x, y, z, btype)
        )  # TODO: implement physics check

    async def _spawn_player(self, player, yaw, pitch, *cords):
        packet = Packet("BbChhhBB")

        for p in self.players[:-1]:
            data = packet.serialize(0x07, -1, player.name, cords[0], cords[1], cords[2], yaw, pitch)
            await p.send(data)
            print(p.name, " --> ", player.name)

