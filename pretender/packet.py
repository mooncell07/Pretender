import struct
from abc import ABC

from attrs import define, field

from .enums import DownstreamOperations, UpstreamOperations

__all__ = ("PlayerIdentificationPacket", "ServerIdentificationPacket")


class AbstractBasePacket(ABC):
    data: bytearray
    fmt: str
    purpose: DownstreamOperations


@define
class PlayerIdentificationPacket(AbstractBasePacket):
    fmt: str = field(init=False, repr=True, default="!BB64s64sB")
    data: str = field(init=True, repr=False)

    purpose: DownstreamOperations = field(init=False, converter=DownstreamOperations)
    protocol_version: int = field(init=False)
    username: str = field(init=False)
    verification_key: str = field(init=False, repr=False)

    def __attrs_post_init__(self):
        (
            self.purpose,
            self.protocol_version,
            self.username,
            self.verification_key,
            _,
        ) = struct.unpack(self.fmt, self.data)


@define
class ServerIdentificationPacket(AbstractBasePacket):
    fmt: str = field(init=False, repr=True, default="!BB64s64sB")

    server_name: bytes
    server_motd: bytes
    user_type: int

    purpose: int = field(
        init=False, repr=True, default=UpstreamOperations.SERVER_IDENTIFICATION
    )
    protocol_version: int = field(init=False, repr=True, default=0x07)

    def serialize(self):
        return struct.pack(
            self.fmt,
            self.purpose.value,
            self.protocol_version,
            self.server_name,
            self.server_motd,
            self.user_type,
        )
