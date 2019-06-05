import sys, json, time, logging, logs.config.client_config_log, decorators, re
from socket import *
from config import *

log = logging.getLogger('Client_log')
logger = decorators.Log(log)

def create_message(message_to, text, account_name='Guest'):
    return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

def create_admin_message(message_to, text, account_name):
    return {ACTION: 'Stop server', TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

def read_only_client(sock):
    while True:
        try:
            message = json.loads(sock.recv(1024).decode('utf-8'))
            log.info(f'Получено сообщение с сервера: {message}')
            print(message[MESSAGE])
        except:
            print('Сервер разорвал соединение!')
            log.error('Сервер разорвал соединение!')
            sock.close()
            break

def write_only_client(sock, account):
    while True:
        user_message = input(':> ')
        if account == 'Admin' and re.findall('^[!]{3}',user_message):
            message_to_send = create_admin_message('#all', user_message, account)
            log.info(f'Админ послал команду выключения сервера и сообщение {user_message}')
        else:
            message_to_send = create_message('#all', user_message, account)
        try:
            sock.send(json.dumps(message_to_send).encode('utf-8'))
        except:
            print('Сервер разорвал соединение!')
            log.error('Сервер разорвал соединение!')
            sock.close()
            break
        log.info(f'Отправлено сообщение на сервер: {message_to_send}')


@logger
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


@logger
def start_client(serv_addr=server_address, serv_port=server_port,action=PRESENCE, mode='f', account='Guest'):
    log.info('Запуск клиента')
    print(f'Здравствуйте {account}!')
    #print(serv_addr,serv_port)
    with socket(AF_INET,SOCK_STREAM) as s:

        if not isinstance(serv_addr,str) or not isinstance(serv_port,int):
            log.error('Полученный адрес сервера или порт не является строкой или числом!')
            raise ValueError

        try:
            #log.info(f'{serv_addr}, {serv_port}')
            if serv_addr != '0.0.0.0':
                s.connect((serv_addr,serv_port))
            else:
                s.connect(('localhost', serv_port))
        except Exception as e:
            print('Ошибка подключения:', e)
            log.error(f'Ошибка подключения: {e}')
            raise

        #message = 'Хэй, хэй!'
        message = create_presence_meassage(account,action)
        if isinstance(message, dict):
            message = json.dumps(message)
        #print(f'Отправляю сообщение "{message}" на сервер')
        log.info(f'Отправляю сообщение "{message}" на сервер')
        s.send(message.encode('utf-8'))
        #print('и жду ответа')
        log.info('и жду ответа')
        server_response = json.loads(s.recv(1024).decode('utf-8'))
        #print('Ответ:',server_response)
        log.info(f'Ответ: {server_response}')
        if server_response.get('response') not in StandartServerCodes:
            log.error(f'Неизвестный код ответа от сервера: {server_response.get("response")}')
            raise UnknownCode(server_response.get('response'))
        if server_response.get('response') == OK:
            print('Соединение установлено!')
            log.info('Сервер нас понимает!')
            if mode == 'r':
                print('Клиент в режиме чтения')
                log.debug('Клиент в режиме чтения')
                read_only_client(s)
            elif mode == 'w':
                print('Клиент в режиме записи')
                log.debug('Клиент в режиме записи')
                write_only_client(s, account)
            elif mode == 'f':
                log.debug('Клиент в полнофункциональном режиме')
                pass
            else:
                raise Exception('Не верный режим клиента')
        else:
            #print('Что-то пошло не так..')
            log.error('Что-то пошло не так..')
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_address = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print('Порт должен быть целым числом!')
            log.error('Переданный номер порта для соединения с сервером не целое число')
        try:
            mode = sys.argv[3]
        except IndexError:
            pass
        try:
            account = sys.argv[4]
        except IndexError:
            pass

    start_client(account=account,mode=mode)

