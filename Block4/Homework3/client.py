import sys, json, time, logging, logs.config.client_config_log, decorators, re, os
from socket import *
from config import *
from meta import *
from threading import Thread

# Инициализация логирования клиента
log = logging.getLogger('Client_log')
logger = decorators.Log(log)

#Основная функция клиента
class Client(metaclass=ClientVerifier):
    global log, logger
        #, PRESENCE, MAIN_CHANNEL, ACTIONS, MSG, TIME,TO,FROM,MESSAGE, SERVER, ACTION, ACCOUNT_NAME, USER, RESPONSE, StandartServerCodes, UnknownCode

    def __init__(self,serv_addr=server_address, serv_port=server_port, mode='f', acc='Guest', passw=''):
        self.serv_addr = serv_addr
        self.serv_port = serv_port
        self.action = PRESENCE
        self.mode = mode
        self.account = acc
        self.passw = passw
        # Последний пользователь, писавший в лс:
        self.last_private_user = ''
        self.alive = True

    # функция создания сообщения в чате
    def create_message(self, message_to, text, account_name='Guest'):
        return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

    # функция спец сообщения для пользователя Admin
    def create_admin_message(self, text, account_name):
        return {ACTION: 'Stop server', TIME: time.time(), TO: SERVER, FROM: account_name, MESSAGE: text}

    # процедура чтения сообщений с сервера
    def client_reader(self, sock, account):
        # в цикле оправшиваем сокет на предмет наличия новых сообщений
        while self.alive:
            try:
                message = json.loads(sock.recv(1024).decode('utf-8'))
                log.info(f'Получено сообщение с сервера: {message}')
                if message[FROM] == account:
                    # TODO
                    print(message[MESSAGE].replace(f'{account}:> ', '(me)', 1))
                else:
                    print(f'{message[MESSAGE]}')
                if message[TO] != MAIN_CHANNEL and re.findall('[^\(private\)]+', message[FROM]):
                    self.last_private_user = message[FROM]
            except:
                if self.alive:
                    print('Cервер разорвал соединение или получен некорректный ответ! Приложение завершает работу')
                    log.error('Reader: Сервер разорвал соединение или получен некорректный ответ!')
                    sock.close()
                self.alive = False
                break
        sys.exit(0)

    # процедура отправки сообщений на сервер
    def client_writer(self, sock, account):
        send_to = MAIN_CHANNEL
        console_prefix = f':> '
        # в цикле запрашиваем у пользователя ввод нового сообщения
        while self.alive:
            user_message = input(console_prefix)
            # Обработка служебных команд пользователя
            if user_message.startswith('to'):  # выбор получателя для отправки
                destination = user_message.split()
                try:
                    send_to = destination[1]
                    if destination[1] == 'all':
                        send_to = MAIN_CHANNEL
                        console_prefix = f':> '
                    else:
                        console_prefix = f'{account} to {destination[1]}:> '
                    log.debug(f'Получатель установлен на: {send_to}')
                    continue
                except IndexError:
                    print('Не задан получатель')
            if user_message == 'help':
                print(f'{account}! Для отправки личного сообщения напишите: to имя_получателя')
                print(
                    'Для отправки всем напишите to all. Быстрый выбор клиента для ответа на последнее лс r. Для получения списка подключенных клиентов who. Для выхода напишите exit')
                log.debug('Вывод справки пользователю по команде help')
                continue
            if user_message == 'exit':
                log.info('Пользователь вызвал закрытие клиента - exit')
                print('Выход из программы..')
                self.alive = False
                #sock.close()
                break
            if user_message == 'r':
                if self.last_private_user:
                    send_to = self.last_private_user
                    console_prefix = f'{account} to {self.last_private_user}:> '
                    log.debug(f'Получатель установлен на последнего писавшего в лс: {self.last_private_user}')
                    continue
            if user_message == 'who':
                message_to_send = self.create_message(SERVER, user_message, account)
                log.debug('Вывод списка пользователей в онлайн - who')
            if account == 'Admin' and re.findall('^[!]{3} stop', user_message):
                # Если админ написал !!! stop, то останавливаем сервер
                message_to_send = self.create_admin_message(user_message, account)
                log.info(f'Админ послал команду выключения сервера и сообщение {user_message}')
            elif user_message != 'who':
                # Формирование обычного сообщения
                message_to_send = self.create_message(send_to, user_message, account)
                log.debug('Формирование обычного сообщения')

            # Отправка сообщения
            try:
                if self.alive:
                    sock.send(json.dumps(message_to_send).encode('utf-8'))
                    log.info(f'Отправлено сообщение на сервер: {message_to_send}')
                else:
                    break
            except:
                if self.alive:
                    print('Сервер разорвал соединение! Приложение завершает работу')
                    log.error('Writer: Сервер разорвал соединение!')
                    sock.close()
                self.alive = False
                break

    @logger
    def create_presence_meassage(self,account_name, account_password='', Action=PRESENCE):
        log.debug('Формирование приветственного сообщения')

        # Проверка параметров на соответствие протоколу
        if len(account_name) > 25:
            log.error('Имя пользователя более 25 символов!')
            raise ValueError

        if not isinstance(account_name, str):
            log.error('Полученное имя пользователя не является строкой символов')
            raise TypeError

        # Приветственное сообщение
        message = {
            ACTION: Action,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name,
                ACCOUNT_PASSWORD: account_password
            }
        }
        return message

    @logger
    def start_client(self):
        log.info('Запуск клиента')
        print('<<< Console IM >>>')
        #Если имя аккаунта не передано, то спросим
        if len(sys.argv) < 3 and self.account == account:
            self.account = input('Введите имя аккаунта: ')
            if len(self.account) == 0: #Если пустой ввод, то имя по-умолчнию
                self.account='Guest'

        #Если пароль аккаунта не передан, то спросим
        if len(sys.argv) < 4 and self.passw == '':
            self.passw = input('Пароль не задан. Введите пароль: ')

        print(f'Здравствуйте {self.account}!')
        #Создаем сокет для общения с сервером
        with socket(AF_INET,SOCK_STREAM) as s:

            if not isinstance(self.serv_addr,str) or not isinstance(self.serv_port,int):
                log.error('Полученный адрес сервера или порт не является строкой или числом!')
                raise ValueError

            # установка связи с сервером
            try:
                if self.serv_addr == '0.0.0.0':
                    self.serv_addr = 'localhost'
                log.info(f' Попытка подключения к {self.serv_addr} {self.serv_port}')
                #print(f' Попытка подключения к {self.serv_addr} {self.serv_port}')
                s.connect((self.serv_addr,self.serv_port))
            except Exception as e:
                print('Ошибка подключения:', e)
                log.error(f'Ошибка подключения: {e}')
                raise

            #создание приветственного сообщения для сервера
            message = self.create_presence_meassage(self.account,self.passw,self.action)

            if isinstance(message, dict):
                message = json.dumps(message)
            log.debug(f'Отправляю приветственное сообщение "{message}" на сервер')
            s.send(message.encode('utf-8'))
            log.debug('и жду ответа')
            server_response = json.loads(s.recv(1024).decode('utf-8'))
            log.debug(f'Ответ: {server_response}')
            #Если сервер ответил нестандартным кодом, то завершаем работу
            if server_response.get(RESPONSE) not in StandartServerCodes:
                log.error(f'Неизвестный код ответа от сервера: {server_response.get(RESPONSE)}')
                raise UnknownCode(server_response.get(RESPONSE))
            #Если сервер ответил Неверный пароль, то завершаем работу
            if server_response.get('response') == WRONG_PASSW:
                print(f'Пароль неверен! Попробуйте переподключиться с другим паролем!')
                log.warning(f'Пароль неверен! Попробуйте переподключиться с другим паролем!')
                self.alive = False
            #Если все хорошо, то переключаем режим клиента в переданный в параметре или оставляем по-умолчанию - полный
            if server_response.get('response') == OK:
                print('Соединение установлено!')
                log.info('Авторизация успешна. Соединение установлено!')
                if self.mode == 'r':
                    print('Клиент в режиме чтения')
                    log.debug('Клиент в режиме чтения')
                    self.client_reader(s,self.account)
                elif self.mode == 'w':
                    print('Клиент в режиме записи')
                    log.debug('Клиент в режиме записи')
                    self.client_writer(s, self.account)
                elif self.mode == 'f':
                    log.debug('Клиент в полнофункциональном режиме')
                    print(f'Отправка сообщений всем пользователям в канал {MAIN_CHANNEL}')
                    print('Для получения помощи наберите help')
                    #читаем сообщения в отдельном потоке
                    read_thread = Thread(target=self.client_reader,args=(s,self.account))
                    read_thread.daemon=True
                    read_thread.start()
                    #read_thread.join()
                    write_thread = Thread(target=self.client_writer,args=(s,self.account))
                    write_thread.daemon=True
                    write_thread.start()
                    #self.client_writer(s, self.account)
                    while self.alive:
                        time.sleep(1)
                        continue
                else:
                    s.close()
                    raise Exception('Не верный режим клиента')
            else:
                #print('Что-то пошло не так..')
                log.error('Что-то пошло не так..')
        s.close()
        exit(0)


if __name__ == "__main__":
    #Проверка аргументов при запуске через консоль
    if len(sys.argv) > 1: #адрес сервера
        server_address = sys.argv[1]
    if len(sys.argv) > 2: #порт сервера
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print('Порт должен быть целым числом!')
            log.error('Переданный номер порта для соединения с сервером не целое число')
        try: #имя аккаунта в чате
            account = sys.argv[3]
        except IndexError:
            pass
        try: #режим запуска, r - только чтение, w - только отправка, f - полноценный клиент
            mode = sys.argv[4]
        except IndexError:
            pass
        try: #пароль
            pwd = sys.argv[5]
        except IndexError:
            pass

    #запуск основного кода клиента
    c = Client(acc=account,mode=mode, passw=pwd)
    c.start_client()
    #sys.exit(0)