from library.minecraft.networking.packets import Packet

from library.minecraft.networking.types import (
    Long
)


# Formerly known as state_status_serverbound.
def get_packets(context):
    packets = {
        RequestPacket,
        PingPacket
    }
    return packets


class RequestPacket(Packet):
    id = 0x00
    packet_name = "request"
    definition = []


class PingPacket(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]
