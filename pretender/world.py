from attrs import define, field

from .events import EventListener

__all__ = ("World",)


@define
class World:
    listeners: list[EventListener] = field(init=False, repr=True, default=[])

    async def connect(self, client):
        listener = EventListener(client)
        self.listeners.append(listener)

        async with client:
            await listener.recv()
