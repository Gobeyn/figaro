def figarotag(name: str | None = None, ext: str | None = None):
    def decorator(func):
        func._figaroname = name or func.__name__
        func._figaroext = ext or "pdf"
        return func

    return decorator
