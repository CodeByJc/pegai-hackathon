def init_db(config):
    # KeyError: 'db_port'
    return f"Connecting to {config['db_host']}:{config['db_port']}"
