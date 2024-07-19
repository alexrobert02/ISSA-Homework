import socket


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.type = None
        self.valid_commands = ["register_Renter", "register_Owner", "post_Car", "request_Car",
                               "end_Rental", "pay_Rental", "start_Engine", "unlock_Car", "lock_Car", "owner_Id", "change_Price"]

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"[+] Conectat la {self.host}: {self.port}")

    def send_message(self, message):
        self.client_socket.send(message.encode())
        server_message = self.client_socket.recv(1024).decode()
        print(f"[Server]: {server_message}")
        if server_message == "You are registered as a renter.":
            self.type = "renter"
        elif server_message.startswith("You are registered as an owner. Your cars are:"):
            self.type = "owner"
        elif server_message.startswith("Rental ended."):
            print("[Client]: Rental ended.")
            return
    def disconnect(self):
        self.client_socket.close()


if __name__ == "__main__":
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12345
    client = Client(SERVER_HOST, SERVER_PORT)
    client.connect()

    while True:
        message = input("Enter your command:")
        client.send_message(message)
        if message == "end_Rental":
            break

    client.disconnect()