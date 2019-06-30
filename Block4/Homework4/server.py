import sys, json, time, logging, logs.config.server_config_log, decorators, select
from config import *
from socket import *
from descriptors import *
from meta import *
from server_database import *

log = logging.getLogger('Server_log')
logger = decorators.Log(log)

#класс серверного сокета
class ServerSocket(socket):
    port = SockVerify()
    address = SockVerify()

    def __init__(self,p_addr='0.0.0.0',p_port=7777):
        super().__init__()
        self.address = p_addr
        self.port = p_port
        self.bind((self.address, self.port))
        self.listen(1)
        self.settimeout(0.1)

class Server(metaclass=ServerVerifier):
    global log, logger
    # Список сокетов клиентов и словарь аккаунтов клиентов с информацией о сокете
    clients = []
    names = {}
    alive = True

    def __init__(self,serv_addr=server_address,serv_port=server_port):
        self.serv_addr=serv_addr
        self.serv_port=serv_port
        self.db_engine = create_engine('sqlite:///db.sqlite3')
        self.db_connection = self.db_engine.connect()
        self.Session = sessionmaker(bind=self.db_engine)
        self.session = self.Session()

    # Функция чтения сообщений с сокетов клиентов
    def read_messages(self,from_clients, client_list):
        # список всех полученных сообщений
        message_list = []
        for connection in from_clients:
            if self.alive:
                try:
                    client_message = json.loads(connection.recv(1024).decode("utf-8"))
                    #log.info(f'Принято сообщение от клиента: {client_message[FROM]}')
                    log.debug(f'{client_message}')
                    # Если спец сообщение от Admin, то вырубаем сервер
                    if ACTION in client_message and FROM in client_message and \
                            client_message[ACTION] == 'Stop server' and \
                            client_message[FROM] == 'Admin':
                        log.info(f'Получена команда выключения сервера, ответ: {RESPONSE}: {SHUTDOWN}')
                        self.alive = False
                        #return {RESPONSE: SHUTDOWN}

                    #if ACTION in client_message and client_message[ACTION] == MSG:
                    message_list.append((client_message, connection))
                except:
                    log.debug(
                        f'Клиент {connection.fileno()} {connection.getpeername()} отключился до передачи сообщения по таймауту ')
                    self.names = {key: val for key, val in self.names.items() if val != connection}
                    client_list.remove(connection)
        return message_list

    # Функция записи сообщений в сокеты клиентов
    def write_messages(self,messages, to_clients, client_list):
        for message, sender in messages:
            if self.alive:

                if ACTION in message and message[ACTION] == GET_CONTACTS:
                    connection = self.names[message[USER_LOGIN]]
                    contact_list = []
                    log.debug(f'Запрос списка контактов из БД')
                    if self.session.query(
                            exists().where(User_contact_list.owner_login == message[USER_LOGIN])).scalar():
                        for contact in self.session.query(User_contact_list.in_list_login).filter(User_contact_list.owner_login == message[USER_LOGIN]).all():
                            contact_list.append(contact[0])
                    else:
                        contact_list = []

                    msg = {
                        RESPONSE: ACCEPTED,
                        ALERT: contact_list
                    }
                    print(msg)
                    try:
                        connection.send(json.dumps(msg).encode('utf-8'))
                    except:
                        log.error('Ошибка ответа на изменение списка контактов')

                elif ACTION in message and message[ACTION] == ADD_CONTACT:
                    connection = self.names[message[USER_LOGIN]]
                    if self.session.query(exists().where(User_contact_list.owner_login == message[USER_LOGIN]).where(User_contact_list.in_list_login == message[USER_ID])).scalar():
                        log.warning('Контакт уже есть в списоке контактов')
                        msg = {RESPONSE: CONFLICT}
                    else:
                        if message[USER_LOGIN] != message[USER_ID]:
                            try:
                                contact = User_contact_list(message[USER_LOGIN], message[USER_ID])
                                self.session.add(contact)
                                self.session.commit()
                                msg = {RESPONSE: ACCEPTED}
                            except:
                                log.error('Не удалось добавить контакт в БД')
                                msg = {RESPONSE: SERVER_ERROR}
                        else:
                            log.warning('Попытка добавления самих себя в список контактов')
                            msg = {RESPONSE: CONFLICT}
                    try:
                        print(f'Отправка ответа {msg}')
                        connection.send(json.dumps(msg).encode('utf-8'))
                    except:
                        log.error('Ошибка ответа на изменение списка контактов')

                elif ACTION in message and message[ACTION] == DEL_CONTACT:
                    connection = self.names[message[USER_LOGIN]]
                    if self.session.query(exists().where(User_contact_list.owner_login == message[USER_LOGIN]).where(
                                                         User_contact_list.in_list_login == message[USER_ID])).scalar():
                        try:
                            self.session.query(User_contact_list).filter_by(owner_login = message[USER_LOGIN],
                                                                            in_list_login = message[
                                                                                USER_ID]).delete()
                            self.session.commit()
                        except:
                            log.error('Не удалось удалить контакт из БД')
                            msg = {RESPONSE: SERVER_ERROR}
                        else:
                            log.info('Удаление контакта из списка успешно')
                            msg = {RESPONSE: ACCEPTED}
                    else:
                        log.error('Контакт для удаления не находится в списке контактов')
                        msg = {RESPONSE: CONFLICT}
                    try:
                        connection.send(json.dumps(msg).encode('utf-8'))
                    except:
                        log.error('Ошибка ответа на изменение списка контактов')


                # Если приватный канал, то отправка только одному получателю
                if ACTION in message and message[ACTION] == MSG and message[TO] != MAIN_CHANNEL and message[TO] != message[FROM]:
                    # получаем пользователя, которому отправляем сообщение
                    to = message[TO]
                    # обработка сервером команды who
                    if message[MESSAGE] != '!who':
                        message[MESSAGE] = f'(private){message[FROM]}:> {message[MESSAGE]}'
                    try:
                        connection = self.names[to]
                    except:
                        connection = self.names[message[FROM]]
                        if message[TO] == SERVER and message[MESSAGE] == '!who':
                            message[TO] = message[FROM]
                            client_names = [key for key in self.names.keys()]
                            message[MESSAGE] = f'<:SERVER:> Список клиентов в онлайн: {client_names}'
                            log.debug(
                                f'Пользователем {message[FROM]} запрошен список пользователей онлайн: {message[MESSAGE]}')
                        else:
                            message[TO] = message[FROM]
                            message[FROM] = SERVER
                            message[MESSAGE] = f'<:SERVER:> Клиент {to} не подключен. Отправка сообщения не возможна!'
                            log.warning(message)
                    # отправка сообщения
                    try:
                        connection.send(json.dumps(message).encode('utf-8'))
                    except:
                        log.warning(
                            f'Сокет клиента {connection.fileno()} {connection.getpeername()} недоступен для отправки. Вероятно он отключился')
                        self.names = {key: val for key, val in self.names.items() if val != connection}
                        connection.close()
                        client_list.remove(connection)
                # если общий канал, то отправка сообщения всем клиентам
                elif message[ACTION] == MSG and message[TO] == MAIN_CHANNEL:
                    message[MESSAGE] = f'{message[FROM]}:> {message[MESSAGE]}'
                    for connection in to_clients:
                        # отправка сообщения
                        try:
                            connection.send(json.dumps(message).encode('utf-8'))
                        except:
                            log.warning(
                                f'Сокет клиента {connection.fileno()} {connection.getpeername()} недоступен для отправки. Вероятно он отключился')
                            self.names = {key: val for key, val in self.names.items() if val != connection}
                            connection.close()
                            client_list.remove(connection)

    # Функция проверки корректности приветственного сообщения и формирования ответа
    @logger
    def check_correct_presence_and_response(self,presence_message):
        log.debug('Запуск ф-ии проверки корректности запроса')
        if ACTION in presence_message and presence_message[ACTION] == 'Unknown':
            return {RESPONSE: UNKNOWN_ERROR}
        elif ACTION in presence_message and \
                presence_message[ACTION] == PRESENCE and \
                TIME in presence_message and \
                isinstance(presence_message[TIME], float):

            if not self.session.query(exists().where(User.login == presence_message['user'][ACCOUNT_NAME])).scalar():
                #Новый клиент, добавляем логин в базу
                u = User(presence_message['user'][ACCOUNT_NAME], presence_message['user'][ACCOUNT_PASSWORD])
                self.session.add(u)
                #Добавляем дату сессии
                ses = User_sessions(presence_message['user'][ACCOUNT_NAME],f'{self.address[0]}:{self.address[1]}')
                self.session.add(ses)
                self.session.commit()
                log.debug(f'Новый пользователь. Проверка успешна, ответ: {RESPONSE}: {OK}')
                return {RESPONSE: OK}
            else:
                # проверка пароля
                chk = self.session.query(User).filter_by(login=presence_message['user'][ACCOUNT_NAME]).first()
                if chk.password == presence_message['user'][ACCOUNT_PASSWORD] or presence_message['user'][ACCOUNT_NAME]==account:
                    #если пароль совпал, добавляем дату сессии
                    ses = User_sessions(presence_message['user'][ACCOUNT_NAME], f'{self.address[0]}:{self.address[1]}')
                    self.session.add(ses)
                    self.session.commit()
                    #Если всё хорошо шлем ОК
                    log.debug(f'Проверка пароля успешна, ответ: {RESPONSE}: {OK}')
                    return {RESPONSE: OK}
                else:
                    log.warning(f'{RESPONSE}: {WRONG_PASSW}, {ERROR}: Не верный пароль. Ввели {presence_message["user"][ACCOUNT_PASSWORD]}, сохраненный пароль {chk.password}')
                    return {RESPONSE: WRONG_PASSW, ERROR: 'Не верный пароль!'}
        else:
            # Иначе шлем код ошибки
            log.warning(f'{RESPONSE}: {WRONG_REQUEST}, {ERROR}: "Не верный запрос"')
            return {RESPONSE: WRONG_REQUEST, ERROR: 'Не верный запрос'}

    @logger
    def start_server(self):

        # создаем сокет для работы с клиентами
        s = ServerSocket(self.serv_addr,self.serv_port)

        #print(self.serv_addr,self.serv_port)
        log.info('Запуск сервера! Готов к приему клиентов! \n')
        while self.alive:
            try:
                # Прием запросов на подключение, проверка приветственного сообщения и ответ
                client, self.address = s.accept()
                log.info(f'Получен запрос на соединение от {self.address[0]}:{self.address[1]}')
                #print(client, address)
                client_message = json.loads(client.recv(1024).decode("utf-8"))
                log.info(f'Принято сообщение от клиента: {client_message}')
                answer = self.check_correct_presence_and_response(client_message)
                client_name = client_message.get('user').get('account_name')
                log.info(f"Приветствуем пользователя {client_name}!")
                log.info(f'Отправка ответа клиенту: {answer}')
                client.send(json.dumps(answer).encode('utf-8'))
            except OSError as e:
                # за время socket timeout не было подключений
                pass
            else:
                self.names[client_name] = client
                self.clients.append(client)
            finally:
                r = []
                w = []
                e = []
                select_timeout = 0
            try:
                r, w, e = select.select(self.clients, self.clients, e, select_timeout)
            except:
                # исключение в случае дисконнекта любого из клиентов
                pass

            req = self.read_messages(r, self.clients)
            self.write_messages(req, w, self.clients)

        self.db_connection.close()
        s.close()
        exit(0)



if __name__ == "__main__":
    # Проверка аргументов при запуске из консоли
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-p' and i + 1 < len(sys.argv):
                server_port = sys.argv[i + 1]
            if sys.argv[i] == '-a' and i + 1 < len(sys.argv):
                server_address = sys.argv[i + 1]

    # Показывать лог в консоль при запуске сервера напрямую
    server_stream_handler = logging.StreamHandler(sys.stdout)
    server_stream_handler.setLevel(logging.DEBUG)
    server_stream_handler.setFormatter(logs.config.server_config_log.log_format)
    log.addHandler(server_stream_handler)

    my_server = Server(server_address,server_port)
    my_server.start_server()
