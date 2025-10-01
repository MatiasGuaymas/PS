# Esqueleto para probar Flags -> Cambiar cuanto antes :)
def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        pass

    return decorated_function

def system_admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        pass

    return decorated_function