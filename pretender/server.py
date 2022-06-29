import asyncio


class MockPacket:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def id(self):
        return self.data[0]

    @property
    def protocol_version(self):
        return self.data[1]

    @property
    def _username(self):
        return self.data


class Client(MockPacket):
    def __init__(self, writer, data):
        super().__init__(data)
        self.username = self._username
        self.writer = writer
        self.is_closing = False

    @classmethod
    async def login(cls, reader, writer):
        data = await reader.read(255)
        return cls(writer, data)

    async def disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()
        self.is_closing = self.writer.is_closing()

    def __repr__(self):
        return f"<Client is_closing={self.is_closing}>"


class Server:
    def __init__(self, host="127.0.0.1", port=25565) -> None:
        self.clients = []
        self.server = None
        self.loop = asyncio.new_event_loop()

        self.host = host
        self.port = port

        asyncio.set_event_loop(self.loop)

    async def __call__(self, reader, writer):
        client = await Client.login(reader, writer)
        self.clients.append(client)

    async def close_all_clients(self):
        for client in self.clients:
            await client.disconnect()

    async def start(self):
        self.server = await asyncio.start_server(self, self.host, self.port)
        addrs = ", ".join(str(sock.getsockname()) for sock in self.server.sockets)

        print(f"Serving on {addrs}")

        async with self.server:
            await self.server.wait_closed()

    def serve(self):
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.close_all_clients())
            self.server.close()
            self.loop.close()

        print(self.clients, self.loop, self.server)


server = Server()
server.serve()
