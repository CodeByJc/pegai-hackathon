def get_user(user_id):
    return None  # simulating a failed DB lookup

def get_username(user_id):
    user = get_user(user_id)
    return user.name
