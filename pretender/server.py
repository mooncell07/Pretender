import anyio

from .world import World

__all__ = ("serve",)


async def serve():
    listener = await anyio.create_tcp_listener(local_host="127.0.0.1", local_port=25565)
    world = World()
    await listener.serve(world.connect)


anyio.run(serve)
