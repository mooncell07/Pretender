import asyncio
from packet import Packet
import logging
from tools import bold, cbold

logger = logging.getLogger(__name__)

__all__ = ("Player",)


class Player:
    def __init__(self, reader, writer, packetview, world):
        self.view = packetview
        self.reader = reader
        self.writer = writer
        self.is_closing = self.writer.is_closing()
        self.spawn_data = None
        self.world = world
        self.id = 1
        self.vacant = []

    @property
    def name(self):
        return self.view["C"][0]

    @property
    def protocol_version(self):
        return self.view["B"][1]

    @property
    def verification_key(self):
        return self.view["C"][1]


    @classmethod
    async def login(cls, reader, writer, world):
        packet = Packet("BBCCB")
        identify = await reader.read(255)
        packetview = packet.deserialize(identify)
        logger.debug(
            f"{bold('upstream(0x00)')}: Received request from {cbold(packetview['C'][0])} to join the server."
        )
        # TODO: MD5 checksum here

        packet.reset()

        payload = packet.serialize(0x00, 0x07, "mock_server", "motd", 0x64)
        writer.write(payload)
        logger.debug(
            f"{bold('downstream(0x00)')}: {cbold(packetview['C'][0])}'s Request Accepted; moving ahead."
        )

        return cls(reader, writer, packetview, world)

    async def loop(self):
        packet = Packet("B")
        payload = packet.serialize(0x01)

        logger.debug(f"{bold('0x01')}: Starting pinging {cbold(self.name)}.")
        while not self.writer.is_closing():
            await self.send(payload)
            await asyncio.sleep(1)

    async def disconnect(self, message="Server Closed!"):
        if not self.is_closing:
            packet = Packet("BC")
            payload = packet.serialize(0x0E, message)

            await self.send(payload)

            self.writer.close()
            await self.writer.wait_closed()

        self.is_closing = self.writer.is_closing()
        logger.debug(f"{bold('0x0E')}: Disconnected player {cbold(self.name)}.")

    async def send(self, payload):
        if not self.is_closing:
            self.writer.write(payload)
            await self.writer.drain()
        else:
            raise NotImplementedError

    def __repr__(self):
        return f"<Player is_closing={self.is_closing}>"
