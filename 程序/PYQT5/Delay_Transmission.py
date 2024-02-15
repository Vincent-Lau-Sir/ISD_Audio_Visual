import socket
import selectors
import types
from Mic_function import *

HOST = "192.168.1.10"
PORT = 5001


def start_connections(host, port):
    server_addr = (host, port)
    print("starting connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(outb=b"")
    sel = selectors.DefaultSelector()  # Vincent added from main
    sel.register(sock, events, data=data)
    return sel


def service_connection(key, mask, sel, host, port):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # shd be ready to read
        if recv_data:
            print("received", repr(recv_data))
            print("closing connection")
            sel.unregister(sock)
            sock.close()
        elif not recv_data:
            print("closing connection")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        global sendFlag
        # TODO change to #if sendFlag == True?
        if sendFlag:
            data.outb = sendBuf
            print("sending", repr(data.outb), "to connection", host, port)
            sent = sock.send(data.outb)  # shd be ready to write
            sendFlag = False


def create_and_send_packet(host, port, message):
    while True:
        try:
            while (input("Please input 'start' to send:") != 'start'):
                pass
            sel = start_connections(host, port)
            global sendBuf, sendFlag
            sendBuf = message
            sendFlag = True
            while True:
                events = sel.select(timeout=None)
                if events:
                    for key, mask in events:
                        service_connection(key, mask, sel, host, port)
        # WX: Check for a socket being monitored to continue
                if not sel.get_map():
                    print("exit 2")
                break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
            sys.exit(1)
        finally:
            print("exit 3")
            sel.close()






