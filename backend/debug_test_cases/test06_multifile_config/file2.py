from file3 import DEFAULTS

def get_feature_flags():
    flags = DEFAULTS.copy()
    # Bug: Typo in flag key override
    flags['feature_X_enabled'] = True 
    return flags
