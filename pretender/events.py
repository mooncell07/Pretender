from anyio.abc import SocketStream
from attrs import define, field

from .enums import DownstreamOperations
from .packet import PlayerIdentificationPacket, ServerIdentificationPacket

__all__ = ("EventListener",)


@define
class EventListener:
    client: SocketStream = field(repr=True, init=True)

    def __getitem__(self, name):
        return getattr(self, f"on_{name}")

    async def recv(self):
        data = await self.client.receive(1024)
        await self._selector(DownstreamOperations(int(data[0])), data)

    async def _selector(self, op, data):
        event = self[op.name.lower()]
        await event(data)

    async def on_player_identification(self, data):
        _ = PlayerIdentificationPacket(data=data)
        packet = ServerIdentificationPacket(
            server_name=b"TestServer", server_motd=b"Test", user_type=0x64
        )
        await self.client.send(packet.serialize())

    async def on_set_block(self):
        ...

    async def on_position_and_orientation(self):
        ...

    async def on_message(self):
        ...
