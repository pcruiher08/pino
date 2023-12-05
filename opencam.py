import cv2

mouse_x, mouse_y = -1, -1
rotated_frame = None

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_x, mouse_y = x, y
        cv2.circle(rotated_frame, (mouse_x, mouse_y), 5, (0, 255, 0), -1)  


cap = cv2.VideoCapture(0)  

if not cap.isOpened():
    print("Error")
    exit()


cv2.namedWindow('Video ')
cv2.setMouseCallback('Video', mouse_callback)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error")
        break


    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)


    cv2.line(rotated_frame, (mouse_x, 0), (mouse_x, rotated_frame.shape[0]), (255, 0, 255), 8)  
    cv2.line(rotated_frame, (0, mouse_y), (rotated_frame.shape[1], mouse_y), (255, 0, 255), 8)  

    cv2.putText(rotated_frame, f'Coordenadas: ({mouse_x}, {mouse_y})', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow('Video', rotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()