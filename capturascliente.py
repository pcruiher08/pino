import socket
import cv2
import numpy as np

server_ip = "192.168.1.144" 
server_port = 5555  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))


cap = cv2.VideoCapture(0)

def capture_and_process_image():
    ret, frame = cap.read()

    cv2.imshow("Captura", frame)
    cv2.waitKey(0)  # Wait for key

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresholded_frame = cv2.threshold(gray_frame, 128, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(largest_contour)
        if moments["m00"] != 0:
            centroid_x = int(moments["m10"] / moments["m00"])
            centroid_y = int(moments["m01"] / moments["m00"])

            print("Centroide:", (centroid_x, centroid_y))

            return centroid_x, centroid_y

capture_and_process_image()

cap.release()


def send_acknowledgment():
    client_socket.send("ACK".encode())

try:
    while True:
        led_number = int(client_socket.recv(1024).decode())
        print("LED ID:", led_number)
        capture_and_process_image()

        send_acknowledgment()

finally:
    cap.release()
    client_socket.close()
