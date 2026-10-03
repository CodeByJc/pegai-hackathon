DEFAULTS = {
    'feature_x_enabled': False
}

def process_data(flags):
    # KeyError because 'feature_x_enabled' is accessed but file2 updated 'feature_X_enabled'
    # Wait, the KeyError actually happens if someone pops or accesses strictly. 
    # Let's make it more direct.
    if flags.pop('feature_x_enabled'):
        print("X enabled")
    # This will fail on something else.
    # Let's make process_data strictly require all keys in a strict list
    strict_keys = ['feature_x_enabled']
    for k in flags.keys():
        if k not in strict_keys:
            raise KeyError(f"Invalid flag {k}")
