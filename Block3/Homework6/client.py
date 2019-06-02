'''
Урок 3. Основы сетевого программирования
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):
a. клиент отправляет запрос серверу;
b. сервер отвечает соответствующим кодом результата.
Клиент и сервер должны быть реализованы в виде отдельных скриптов, содержащих соответствующие функции.
Функции клиента:
1. Сформировать presence-сообщение;
2. Отправить сообщение серверу;
3. Получить ответ сервера;
4. Разобрать сообщение сервера;
5. Параметры командной строки скрипта client.py <addr> [<port>]:
6. Addr — ip-адрес сервера;
7. Port — tcp-порт на сервере, по умолчанию 7777.
Функции сервера:
1. Принимает сообщение клиента;
2. Формирует ответ клиенту;
3. Отправляет ответ клиенту.
Имеет параметры командной строки:
-p <port> — TCP-порт для работы (по умолчанию использует 7777);
-a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
'''

import sys, json, time, logging, logs.config.client_config_log, decorators
from socket import *
from config import *

log = logging.getLogger('Client_log')

@decorators.log
def create_presence_meassage(account_name='Guest', Action=PRESENCE):
    log.info('Формирование сообщения')
    if len(account_name)> 25:
        log.error('Имя пользователя более 25 символов!')
        raise ValueError

    if not isinstance(account_name, str):
        log.error('Полученное имя пользователя не является строкой символов')
        raise TypeError

    message = {
        ACTION: Action,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return message


@decorators.log
def start_client(serv_addr=server_address, serv_port=server_port,action=PRESENCE):
    log.info('Запуск клиента')

    s = socket(AF_INET,SOCK_STREAM)

    if not isinstance(serv_addr,str) or not isinstance(serv_port,int):
        log.error('Полученный адрес сервера или порт не является строкой или числом!')
        s.close()
        raise ValueError

    try:
        if server_address != '0.0.0.0':
            s.connect((serv_addr,serv_port))
        else:
            s.connect(('localhost', serv_port))
    except Exception as e:
        #print('Ошибка подключения:', e)
        log.error(f'Ошибка подключения: {e}')
        s.close()
        raise

    #message = 'Хэй, хэй!'
    message = create_presence_meassage('SuperUser',action)
    if isinstance(message, dict):
        message = json.dumps(message)
    #print(f'Отправляю сообщение "{message}" на сервер', end= ' ')
    log.info(f'Отправляю сообщение "{message}" на сервер')
    s.send(message.encode('utf-8'))
    #print('и жду ответа')
    log.info('и жду ответа')
    server_response = json.loads(s.recv(1024).decode('utf-8'))
    #print('Ответ:',server_response)
    log.info(f'Ответ: {server_response}')
    if server_response.get('response') not in StandartServerCodes:
        log.error(f'Неизвестный код ответа от сервера: {server_response.get("response")}')
        s.close()
        raise UnknownCode(server_response.get('response'))
    if server_response.get('response') == OK:
        #print('Сервер нас понимает!')
        log.info('Сервер нас понимает!')
    else:
        #print('Что-то пошло не так..')
        log.error('Что-то пошло не так..')
    s.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_address = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            'Порт должен быть целым числом!'
            log.error('Переданный номер порта для соединения с сервером не целое число')

    start_client()

