def tkinter_is_installed() -> bool:
    try:
        import tkinter
        return True
    except ModuleNotFoundError:
        return False
