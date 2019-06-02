'''
1. Продолжая задачу логирования, реализовать декоратор @log, фиксирующий обращение к декорируемой функции. Он сохраняет ее имя и аргументы.
2. В декораторе @log реализовать фиксацию функции, из которой была вызвана декорированная. Если имеется такой код:
@log
def func_z():
    pass

def main():
    func_z()
...в логе должна быть отражена информация:
"<дата-время> Функция func_z() вызвана из функции main"
'''
import time
from functools import wraps
from functools import wraps
from logs.config.client_config_log import *
from logs.config.server_config_log import *

def log(func):
    @wraps(func)
    def deco_log_call(*args,**kwargs):
        if func.__name__ == 'create_presence_meassage' or func.__name__ == 'start_client':
            client_log.info(f'{time.asctime()} Вызван декоратор {log.__name__} для {func.__name__} с параметрами ({args} {kwargs})')
        elif func.__name__ == 'check_correct_presence_and_response' or func.__name__ == 'start_server':
            server_log.info(f'{time.asctime()} Вызван декоратор {log.__name__} для {func.__name__} с параметрами ({args} {kwargs})')

        print(f'{time.asctime()} Вызван декоратор {log.__name__} для {func.__name__} с параметрами ({args} {kwargs})')
        res = func(*args,**kwargs)
        return res
    return deco_log_call
