import struct

__all__ = ("DataBuffer", "Packet")


class DataBuffer:
    def __init__(self):
        self._data = bytes()
        self.cursor = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def read(self, length: int = 1):
        data = self._data[self.cursor :][:length]
        self.cursor += length
        return data

    def read_byte(self):
        return self.read()

    def read_sbyte(self):
        pass

    def read_short(self):
        self.cursor += struct.calcsize("!h")
        return struct.unpack_from("!h", self._data, self.cursor)

    def read_string(self, length: int = 64):
        return self.read(length).decode("ascii").rstrip()

    def read_array(self, length: int = 1024):
        return bytes(self.read(length))

    def write(self, data: bytes):
        if type(data) is int:
            data = data.to_bytes(1, byteorder="big")

        self._data += data

    def write_byte(self, data: bytes):
        self.write(struct.pack("!B", data))

    def write_sbyte(self, sbyte):
        self.write(struct.pack(">b", sbyte))

    def write_short(self, short):
        self.write(struct.pack("!h", short))

    def write_string(self, string: str, length: int = 64):
        self.write(
            string.encode("ascii") + ("\x20" * (length - len(string))).encode("ascii")
        )

    def write_array(self, array, length: int = 1024):
        self.write(array + (b"\x00" * (length - len(array))))

    def reset(self):
        self._data = bytes()
        self.cursor = 0


class Packet(DataBuffer):
    def __init__(self, fmt) -> None:
        super().__init__()
        self.fmt = fmt

    @property
    def wfmtspec(self):
        return {
            "B": self.write_byte,
            "b": self.write_sbyte,
            "h": self.write_short,
            "C": self.write_string,
            "A": self.write_array,
        }

    @property
    def rfmtspec(self):
        return {
            "B": self.read_byte,
            "b": self.read_sbyte,
            "h": self.read_short,
            "C": self.read_string,
            "A": self.read_array,
        }

    def serialize(self, *data):
        for f, d in zip(self.fmt, data):
            self.wfmtspec[f](d)
        return self._data

    def deserialize(self, data):
        self.data = data

        packet_dict = {}

        for f in self.fmt:
            if f not in packet_dict:
                packet_dict[f] = [self.rfmtspec[f]()]
            else:
                packet_dict[f].append(self.rfmtspec[f]())

        return packet_dict
