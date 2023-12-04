import socket
import board
import neopixel

num_pixels = 500
pixel_pin = board.D18  

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("192.168.1.144", 5555))  
server_socket.listen(1)

print("Listening.")

while True:
    client_socket, client_address = server_socket.accept()
    print("Conectado", client_address)

    try:
        for led_number in range(num_pixels):
            client_socket.send(str(led_number).encode())

            ack = client_socket.recv(1024).decode()
            if ack != "ACK":
                break

            pixels.fill((0, 0, 0))  
            pixels[led_number] = (255, 255, 255)  
            pixels.show()
            print("LED:", led_number)

    finally:
        client_socket.close()
