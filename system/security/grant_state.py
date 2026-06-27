CURRENT_GRANT = None


def set_current_grant(grant: dict):
    global CURRENT_GRANT
    CURRENT_GRANT = grant


def get_current_grant():
    return CURRENT_GRANT


def clear_current_grant():
    global CURRENT_GRANT
    CURRENT_GRANT = None
