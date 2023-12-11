import socket
import board
import neopixel

num_pixels = 500

pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False)


host = '192.168.1.144'
port = 4444

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print(f"Server listening on {host}:{port}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            red, green, blue = map(int, data.decode().split(','))

            pixels.fill((red, green, blue))
            pixels.show()

    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed")
