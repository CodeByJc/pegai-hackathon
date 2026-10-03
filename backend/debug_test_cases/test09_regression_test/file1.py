from file2 import calculate_total
from file3 import get_cart

def checkout():
    cart = get_cart()
    total = calculate_total(cart)
    # The bug is functional: calculate_total doesn't sum correctly
    # So we'll force an assertion error or just an exception to mimic a failure
    if total != 150:
        raise ValueError(f"Total is wrong! Expected 150, got {total}")

if __name__ == '__main__':
    checkout()
