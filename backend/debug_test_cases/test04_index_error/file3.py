def get_raw_lines():
    return [
        "1,Alice,Admin",
        "2,Bob" # Missing role, causes IndexError
    ]
