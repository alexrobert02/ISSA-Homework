import socket
from threading import Thread

from Car import Car


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_commands = ["register_Renter", "register_Owner", "post_Car", "request_Car",
                               "end_Rental", "pay_Rental", "start_Engine", "unlock_Car", "lock_Car", "owner_Id", "change_Price"]
        self.cars = [Car("Audi", "A4", 2019, 100, 11, 1),
                     Car("BMW", "X5", 2020, 150, 12, 2),
                     Car("Mercedes", "E200", 2018, 120, 13, 3)]
        self.clients_type = [None] * 1000
        self.client_id_counter = 0

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        print(f"[*] Listening as {self.host}: {self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"[*] {client_address[0]}:{client_address[1]} connected.")
            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        client_id = self.client_id_counter + 1
        self.client_id_counter += 1
        self.clients_type[client_id] = None

        if True:
            try:
                client_id = self.client_id_counter
                self.clients_type[client_id] = None
                while True:
                    client_message = client_socket.recv(1024).decode()
                    print(f"[Client]: {client_message}")
                    print(f"[Client]: {client_id}")
                    if client_message == "end_Rental":
                        print("test")
                        for car in self.cars:
                            if car.user_id == client_id and car.paid == 1:
                                confirmation_message = car.send_confirmation_message()
                                if confirmation_message == "rental_success":
                                    print("test2")
                                    print(car.id)
                                    print(car.paid)
                                    car.user_id = None
                                    car.availability = 1
                                    car.paid = 0
                                    print("[Server]: Confirmation successful.")
                                    print("[Server]: Rental ended.")
                                    server_message = "Rental ended."
                                    client_socket.send(server_message.encode())
                                    break
                                else:
                                    print("[Server]: Confirmation error.")
                            else:
                                server_message = "You have to pay the rental first."

                    elif client_message == "register_Renter":
                        server_message = "You are registered as a renter."
                        self.clients_type[client_id] = "renter"

                    elif client_message == "register_Owner":
                        server_message = "Enter the Owner Id like this: 'owner_Id: id' "

                    elif client_message.startswith("owner_Id"):
                        owner_id = int(client_message.split(":")[1])
                        server_message = "You are registered as an owner. Your cars are: \n"
                        for car in self.cars:
                            if car.owner_id == owner_id:
                                server_message += f"{car.to_dict()}\n"
                        if server_message == "You are registered as an owner. Your cars are: \n":
                            server_message = "No cars found."
                        else:
                            self.clients_type[client_id] = "owner"

                    elif client_message == "change_Price" and self.clients_type[client_id] == "owner":
                        server_message = "Enter the Id of the car and the new price like this: 'owner_Id: car_Id: new_price'"

                    elif client_message[0].isdigit() and self.clients_type[client_id] == "owner":
                        owner_id, car_id, new_price = client_message.split(":")
                        car_id = int(car_id)
                        new_price = int(new_price)
                        ok=0
                        for car in self.cars:
                            if car.id == car_id and car.owner_id == int(owner_id):
                                car.price = new_price
                                server_message = "Price changed."
                                ok=1
                        if ok == 0:
                            server_message = "Car not found."

                    elif client_message == "post_Car" and self.clients_type[client_id] is not None:
                        server_message = ""
                        for car in self.cars:
                            if car.availability == 1:
                                server_message += f"{car.to_dict()}\n"

                    elif client_message == "request_Car" and self.clients_type[client_id] is not None :
                        server_message = "Enter the Id of requested car like this: 'car_Id: id'"

                    elif client_message == "start_Engine" and self.clients_type[client_id] is not None:
                        for car in self.cars:
                            if car.user_id == client_id:
                                car.start_engine = 1
                        server_message = "Engine started."

                    elif client_message == "unlock_Car" and self.clients_type[client_id] is not None:
                        for car in self.cars:
                            if car.user_id == client_id:
                                car.lock = 0
                        server_message = "Car unlocked."

                    elif client_message == "lock_Car" and self.clients_type[client_id] is not None:
                        for car in self.cars:
                            if car.user_id == client_id:
                                car.lock = 1
                        server_message = "Car locked."

                    elif client_message == "pay_Rental" and self.clients_type[client_id] is not None:
                        for car in self.cars:
                            if car.user_id == client_id:
                                car.paid = 1
                        server_message = "Rental paid."

                    elif client_message.startswith("car_Id") and self.clients_type[client_id] is not None:
                        car_id = int(client_message.split(":")[1])
                        ok = 0
                        for Car in self.cars:
                            if Car.id == car_id:
                                if Car.availability == 1:
                                    Car.availability = 0
                                    Car.user_id = client_id
                                    ok = 1
                                    server_message = "Rental started."
                        if ok == 0:
                            server_message = "Car not found or not available."
                    elif self.clients_type[client_id] is None:
                        server_message = "You have to register first."
                    else:
                        server_message = "Invalid command."

                    client_socket.send(server_message.encode())

            except Exception as e:
                print(f"Error: {e}")

            finally:
                client_socket.close()

    def stop(self):
        self.server_socket.close()


if __name__ == "__main__":
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12345
    server = Server(SERVER_HOST, SERVER_PORT)
    server.start()
    server.stop()