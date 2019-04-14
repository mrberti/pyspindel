"""
Simple script to receive multicast messages.
Based on: https://stackoverflow.com/questions/15197569/any-small-program-to-receive-multicast-packets-on-specified-udp-port

ATTENTION: When on Windows and using VirtualBox, you maybe need to
disable the "VirtualBox Host-Only Network" Adapter. The Adapter is a
black hole for multicast packages.
See: https://serverfault.com/questions/348156/troubleshooting-udp-multicast-on-windows
Also: https://www.virtualbox.org/ticket/8698
"""
import socket

MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT = 6265

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", MULTICAST_PORT))
# sock.bind((MULTICAST_GROUP, MULTICAST_PORT))

# Tell the kernel that we want to add ourselves to a multicast group
# The address for the multicast group is the third param
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0"))

while 1:
    try:
        data, addr = sock.recvfrom(1024)
    except socket.error as exc:
        print("Exception: {}".format(exc))
    else:
        print("From: {}".format(addr))
        print("Data: {}".format(data))
