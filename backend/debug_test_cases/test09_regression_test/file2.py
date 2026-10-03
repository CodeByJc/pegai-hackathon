def calculate_total(items):
    # Functional bug: multiplies instead of adds
    total = 1
    for item in items:
        total *= item['price']
    return total
