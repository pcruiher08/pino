import socket
import cv2
import json
import numpy as np

server_ip = "192.168.1.144" 
server_port = 5555  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap.set(cv2.CAP_PROP_FRAME_WIDTH,width)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 


def capture_and_process_image(frame):

    #cv2.imshow("Captura", frame)
    
    #cv2.waitKey(0)  # Wait for key

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
            cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

            
            return centroid_x, centroid_y




def send_acknowledgment():
    client_socket.send("ACK".encode())


led_points = []

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error")
            break
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        led_number = int(client_socket.recv(1024).decode())
        print("LED ID:", led_number)
        centroid = capture_and_process_image(rotated_frame)

        if(centroid is not None):
            led_points.append({"id": len(led_points), "x": centroid[0], "y": centroid[1]})


            cv2.line(rotated_frame, (centroid[0], 0), (centroid[0], rotated_frame.shape[0]), (255, 0, 255), 8)  
            cv2.line(rotated_frame, (0, centroid[1]), (rotated_frame.shape[1], centroid[1]), (255, 0, 255), 8)  

            cv2.putText(rotated_frame, f'Coordinates: ({centroid[0]}, {centroid[1]})', (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.imshow('Video Feed', rotated_frame)
        print(centroid)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        send_acknowledgment()
    

finally:
    if led_points:
        average_x = sum(point["x"] for point in led_points) / len(led_points)
        average_y = sum(point["y"] for point in led_points) / len(led_points)
    else:
        print("No hay leds")
        average_x, average_y = 0, 0

        
    for point in led_points:
        point["x_corrected"] = point["x"] - average_x
        point["y_corrected"] = point["y"] - average_y

    output_filename = "led_coordinates.json"
    print(len(led_points))
    if(len(led_points) > 258):
        with open(output_filename, "w") as json_file:
            json.dump(led_points, json_file, indent=2)

        print(f"Guardado en {output_filename}")


    cap.release()
    cv2.destroyAllWindows()

    client_socket.close()
