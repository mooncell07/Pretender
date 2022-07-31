import enum

__all__ = ("DownstreamOperations", "UpstreamOperations")


@enum.unique
class DownstreamOperations(enum.IntEnum):
    PLAYER_IDENTIFICATION = 0x00
    SET_BLOCK = 0x05
    POSITION_AND_ORIENTATION = 0x08
    MESSAGE = 0x0D


@enum.unique
class UpstreamOperations(enum.IntEnum):
    SERVER_IDENTIFICATION = 0x00
    PING = 0x01
    LEVEL_INITIALIZE = 0x02
    LEVEL_DATA_CHUNK = 0x03
    LEVEL_FINALIZE = 0x04
    SET_BLOCK = 0x06
    SPAWN_PLAYER = 0x07
    POSITION_AND_ORIENTATION = 0x08
    POSITION_AND_ORIENTATION_UPDATE = 0x09
    POSITION_UPDATE = 0x0A
    ORIENTATION_UPDATE = 0x0B
    DESPAWN_PLAYER = 0x0C
    MESSAGE = 0x0D
    DISCONNECT_PLAYER = 0x0E
    UPDATE_USER_TYPE = 0x0F
