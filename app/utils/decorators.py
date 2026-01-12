# app/utils/decorators.py
def static_all_methods(cls):
    for name, attr in cls.__dict__.items():
        if callable(attr) and not name.startswith("__"):
            setattr(cls, name, staticmethod(attr))
    return cls
