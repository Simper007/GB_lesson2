import sys, json, time, logging, logs.config.server_config_log, decorators, select
from config import *
from socket import *

log = logging.getLogger('Server_log')
logger = decorators.Log(log)

def read_messages(from_clients,client_list):
    #log.debug('Запуск функции получения сообщений от клиентов')
    message_list = []
    for connection in from_clients:
        try:
            client_message = json.loads(connection.recv(1024).decode("utf-8"))
            log.info(f'Принято сообщение от клиента: {client_message[FROM]}')
            log.debug(f'{client_message}')
            client_message[MESSAGE] = f'{client_message[FROM]}:> {client_message[MESSAGE]}'
            if ACTION in client_message and \
                 client_message[ACTION] == 'Stop server' and \
                 client_message[FROM] == 'Admin':
                log.info(f'Получена команда выключения сервера, ответ: {RESPONSE}: {SHUTDOWN}')
                return {RESPONSE: SHUTDOWN}
            message_list.append(client_message)
        except:
            log.debug(f'Клиент {connection.fileno()} {connection.getpeername()} отключился до передачи сообщения по таймауту ')
            client_list.remove(connection)
    return message_list


def write_messages(messages,to_clients, client_list):
   # log.debug('Запуск функции отправки сообщений клиентам')
    for connection in to_clients:
        for message in messages:
            try:
                connection.send(json.dumps(message).encode('utf-8'))
            except:
                log.info(f'Сокет клиента {connection.fileno()} {connection.getpeername()} недоступен для отправки. Ветроятно он отключился')
                connection.close()
                client_list.remove(connection)

@logger
def check_correct_presence_and_response(presence_message):
    log.debug('Запуск ф-ии проверки корректности запроса')
    if ACTION in presence_message and presence_message[ACTION] == 'Unknown':
        return {RESPONSE: UNKNOWN_ERROR}
    elif ACTION in presence_message and \
                    presence_message[ACTION] == PRESENCE and \
                    TIME in presence_message and \
            isinstance(presence_message[TIME], float):
        # Если всё хорошо шлем ОК
        log.debug(f'Проверка успешна, ответ: {RESPONSE}: {OK}')
        return {RESPONSE: OK}
    else:
        # Иначе шлем код ошибки
        log.warning(f'{RESPONSE}: {WRONG_REQUEST}, {ERROR}: "Не верный запрос"')
        return {RESPONSE: WRONG_REQUEST, ERROR: 'Не верный запрос'}

@logger
def start_server(serv_addr=server_address, serv_port=server_port):
    alive = True

    with socket(AF_INET,SOCK_STREAM) as s:
        if not isinstance(serv_addr,str) or not isinstance(serv_port,int):
            log.error('Полученный адрес сервера или порт не является строкой или числом!')
            raise ValueError

        s.bind((serv_addr,serv_port))
        s.listen(1)
        s.settimeout(0.1)

        clients = []

        log.info('Запуск сервера! Готов к приему клиентов! \n')


        while alive:
            try:
                client, address = s.accept()
                client_message = json.loads(client.recv(1024).decode("utf-8"))
                log.info(f'Принято сообщение от клиента: {client_message}')
                answer = check_correct_presence_and_response(client_message)
                log.info(f"Приветствуем пользователя {client_message.get('user').get('account_name')}!")
                log.info(f'Отправка ответа клиенту: {answer}')
                client.send(json.dumps(answer).encode('utf-8'))
                #client.close
            except OSError as e:
                #за время socket timeout не было подключений
                pass
            else:
                log.info(f'Получен запрос на соединение от {str(address)}')
                clients.append(client)
            finally:
                r = []
                w = []
                e = []
                select_timeout = 0
            try:
                r, w, e = select.select(clients, clients, [], select_timeout)
            except:
                #исключение в случае дисконнекта любого из клиентов
                pass

            req = read_messages(r,clients)
            if req == {RESPONSE: SHUTDOWN}:
                alive = False
                log.info(f'Завершение работы сервера по команде от Admin')
            write_messages(req,w,clients)



if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(1,len(sys.argv)):
            if sys.argv[i] == '-p' and i+1 < len(sys.argv):
                server_port = sys.argv[i+1]
            if sys.argv[i] == '-a' and i+1 < len(sys.argv):
                server_address = sys.argv[i+1]

    #Показывать лог в консоль при запуске сервера напрямую
    server_stream_handler = logging.StreamHandler(sys.stdout)
    server_stream_handler.setLevel(logging.DEBUG)
    server_stream_handler.setFormatter(logs.config.server_config_log.log_format)
    log.addHandler(server_stream_handler)

    start_server()