import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 8080))
s.listen(1)

conn, addr = s.accept()
print(conn)
print(addr)

while 1:
    # struct.unpack('')
    data = conn.recv(1024)
    print(data)
    if not data:
        break
    conn.send(data.upper())

conn.close()
