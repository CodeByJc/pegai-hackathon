def render_profile(user):
    # AttributeError: 'NoneType' object has no attribute 'get'
    # Multiple causes: fetch_user returned None OR render_profile doesn't handle None
    name = user.get('name', 'Unknown')
    return f"Profile: {name}"
