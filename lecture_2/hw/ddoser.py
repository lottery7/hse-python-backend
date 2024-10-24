import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def create_carts():
    for _ in range(500):
        response = requests.post("http://localhost:8000/cart")
        print(response)

        if random.random() > 0.5:
            time.sleep(5)


def get_cart(cart_id):
    for _ in range(500):
        response = requests.get(f"http://localhost:8000/cart/{cart_id}")
        print(response)

        if random.random() > 0.5:
            time.sleep(5)


with ThreadPoolExecutor() as executor:
    futures = {}

    # Создаем корзины
    for i in range(30):
        futures[executor.submit(create_carts)] = f"create-cart-{i}"

    # Получаем корзины
    for i in range(30):
        cart_id = random.randint(0, 100)
        futures[executor.submit(get_cart, cart_id)] = f"get-cart-{i}"

    for future in as_completed(futures):
        print(f"completed {futures[future]}")
