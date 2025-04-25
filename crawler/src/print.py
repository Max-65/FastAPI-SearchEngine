import datetime

def log(message: str) -> None: # Log messages are printed with current date
    print(f'[{datetime.datetime.now().isoformat()}] {message}')

__all__ = ['log']