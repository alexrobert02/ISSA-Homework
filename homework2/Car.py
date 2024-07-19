import requests


class Car:
    def __init__(self, brand, model, year, price, owner_id, id):
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price
        self.availability = 1
        self.paid = 0
        self.owner_id = owner_id
        self.id = id
        self.lock = 1
        self.start_engine = 0
        self.user_id = None


    def get_location(self):
        response = requests.get('https://ipinfo.io%27')
        data = response.json()
        location = data.get('loc')
        return location

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "price": self.price,
            "location": self.get_location()
        }

    def send_confirmation_message(self):
        if self.paid == 1:
            return "rental_success"
        else:
            return "rental_failure"


def main():
    car = Car("Audi", "A3", 2019, 100, "Owner1")
    print(car.to_dict())
