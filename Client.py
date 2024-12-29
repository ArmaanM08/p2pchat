# client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import ssl
from config import CLIENT_HOST as HOST, PORT, PASSWORD

class ChatClient:
    def __init__(self):
        # Create socket and SSL context
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.sock = context.wrap_socket(self.sock)
        
        # Create GUI
        self.win = tk.Tk()
        self.win.title("Secure Chat")
        self.win.geometry("400x500")
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.win)
        self.chat_area.pack(padx=20, pady=5)
        
        # Message input
        self.msg_entry = tk.Entry(self.win)
        self.msg_entry.pack(padx=20, pady=5)
        
        # Send button
        self.send_button = tk.Button(self.win, text="Send", command=self.send_message)
        self.send_button.pack(padx=20, pady=5)
        
        # Connect to server
        self.connect_to_server()
        
        # Start receiving thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Handle window closing
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.win.mainloop()
    
    def connect_to_server(self):
        try:
            self.sock.connect((HOST, PORT))
            self.sock.send(PASSWORD.encode('utf-8'))  # Send password first
            # Wait for authentication response
            response = self.sock.recv(1024).decode('utf-8')
            if response == "Invalid password":
                messagebox.showerror("Authentication Error", "Invalid password")
                self.win.destroy()
                return
            self.chat_area.insert(tk.END, "Connected to server!\n")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.win.destroy()
    
    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                self.chat_area.insert(tk.END, message + '\n')
                self.chat_area.see(tk.END)
            except:
                messagebox.showerror("Connection Error", "Lost connection to server")
                self.sock.close()
                self.win.destroy()
                break
    
    def send_message(self):
        message = self.msg_entry.get()
        if message:
            try:
                self.sock.send(message.encode('utf-8'))
                self.msg_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Connection Error", "Could not send message")
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.sock.close()
            self.win.destroy()

if __name__ == "__main__":
    ChatClient()
