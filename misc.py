from datetime import datetime


def timestamp():
    current_time = datetime.now()
    return current_time.strftime('%d/%m/%Y %H:%M')

def print_message(message:str):
    print('\n'+'-'*(len(message)+ 4))
    print(f'| {message} |')
    print('-'*(len(message)+ 4))

def on_start():
    msg=f'Bot started at {timestamp()}'
    print_message(msg)

def on_stop():
    msg=f'Bot stopped at {timestamp()}'
    print_message(msg)