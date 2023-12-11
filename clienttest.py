import tkinter as tk
from tkinter import ttk
import socket

host = '192.168.1.144'
port = 4444

root = tk.Tk()
root.title("LED Color Control")

def send_colors():
    red = int(round(red_slider.get()))
    green = int(round(green_slider.get()))
    blue = int(round(blue_slider.get()))

    color_data = f"{red},{green},{blue}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(color_data.encode())

red_label = ttk.Label(root, text="Red:")
red_label.grid(column=0, row=0, padx=10, pady=10)
red_slider = ttk.Scale(root, from_=0, to=255, orient="horizontal")
red_slider.grid(column=1, row=0, padx=10, pady=10)

green_label = ttk.Label(root, text="Green:")
green_label.grid(column=0, row=1, padx=10, pady=10)
green_slider = ttk.Scale(root, from_=0, to=255, orient="horizontal")
green_slider.grid(column=1, row=1, padx=10, pady=10)

blue_label = ttk.Label(root, text="Blue:")
blue_label.grid(column=0, row=2, padx=10, pady=10)
blue_slider = ttk.Scale(root, from_=0, to=255, orient="horizontal")
blue_slider.grid(column=1, row=2, padx=10, pady=10)

send_button = ttk.Button(root, text="Send Colors", command=send_colors)
send_button.grid(column=0, row=3, columnspan=2, pady=10)

root.mainloop()
