import sys, json, time, logging, logs.config.client_config_log, decorators, re, os
from socket import *
from config import *
from meta import *
from threading import Thread
from client_database import *
from PyQt5 import QtWidgets, QtCore, QtGui
from connect_window import Ui_Form

# Инициализация логирования клиента
log = logging.getLogger('Client_log')
logger = decorators.Log(log)

#Основная функция клиента
class Client(metaclass=ClientVerifier):
    global log, logger, conn_window

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
        self.contact_list = []
        self.db_engine = create_engine('sqlite:///client_db.sqlite3')
        self.db_connection = self.db_engine.connect()
        self.Session = sessionmaker(bind=self.db_engine)
        self.session = self.Session()

    @logger
    def get_contact_list(self, sock,show_progress='Y'):

        log.info('Обновление списка контактов с сервера..')
        if show_progress == 'Y':
            print('Обновление списка контактов с сервера..')

        msg = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER_LOGIN: self.account
         }

        try:
            #print('Отправка команды обновления списка')
            sock.send(json.dumps(msg).encode('utf-8'))
        except:
            log.error('Ошибка отправки команды на обновление списка контактов')
            if show_progress == 'Y':
                print('Ошибка получения списка контактов')
            return

    @logger
    def set_contact_list(self,sock,command,user):
        msg = {
        ACTION: command,
        USER_ID: user,
        TIME: time.time(),
        USER_LOGIN: self.account
         }
        try:
            sock.send(json.dumps(msg).encode('utf-8'))
        except:
            log.error('Ошибка отправки команды на изменение списка контактов')
            print('Ошибка изменения списка контактов 1')
            return

    # функция создания сообщения в чате
    @logger
    def create_message(self, message_to, text, account_name='Guest'):
        return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

    # функция спец сообщения для пользователя Admin
    @logger
    def create_admin_message(self, text, account_name):
        return {ACTION: 'Stop server', TIME: time.time(), TO: SERVER, FROM: account_name, MESSAGE: text}

    # процедура чтения сообщений с сервера
    def client_reader(self, sock, account):
        # в цикле оправшиваем сокет на предмет наличия новых сообщений
        while self.alive:
            try:
                message = json.loads(sock.recv(1024).decode('utf-8'))
                log.info(f'Получено сообщение с сервера: {message}')
                if FROM in message and message[FROM] == account:
                    # TODO
                    print(message[MESSAGE].replace(f'{account}:> ', '(me)', 1))
                    try:
                        msg_hist = Chat_histories(self.account,message[FROM],message[TO],message[MESSAGE])
                        self.session.add(msg_hist)
                        self.session.commit()
                    except:
                        log.error('Ошибка записи истории чата в БД')
                        print('Ошибка записи истории чата в БД')
                elif ALERT in message:
                    #self.contact_list = message[ALERT]
                    try:
                        self.session.query(User_contact_list).delete()
                        self.session.commit()
                        for contact in message[ALERT]:
                            print(contact)
                            cl = User_contact_list(self.account,contact)
                            self.session.add(cl)
                            self.session.commit()

                    except:
                        log.error('Ошибка изменения списка контактов в БД клиента')
                        print('Ошибка изменения списка контактов в БД клиента')

                    log.info('Список контактов обновлен')
                    #print('Список контактов обновлен')
                elif RESPONSE in message:
                    if message[RESPONSE] == ACCEPTED:
                        log.info('Список контактов изменен')
                        print('Список контактов изменен')
                        self.get_contact_list(sock, 'N')
                    elif message[RESPONSE] == CONFLICT:
                        log.info('Попытка добавить самих себя или контакт уже есть/уже нет в списке')
                        print('Вы пытаетесь добавить самих себя или контакт уже есть/уже нет в списке')
                    elif message[RESPONSE] == SERVER_ERROR:
                        log.error('Ошибка изменения списка контактов на сервере')
                        print('Ошибка списка контактов на сервере')
                    else:
                        log.error(f'Неизвестный код ответа сервера {message[RESPONSE]}')
                        print(f'Неизвестный код ответа сервера {message[RESPONSE]}')

                elif FROM in message and message[FROM] != account:
                    print(f'{message[MESSAGE]}')
                    try:
                        msg_hist = Chat_histories(self.account,message[FROM],message[TO],message[MESSAGE])
                        self.session.add(msg_hist)
                        self.session.commit()
                    except:
                        log.error('Ошибка записи истории чата в БД')
                        print('Ошибка записи истории чата в БД')

                if TO in message and message[TO] != MAIN_CHANNEL and re.findall('[^\(private\)]+', message[FROM]):
                    self.last_private_user = message[FROM]
                    try:
                        msg_hist = Chat_histories(self.account,message[FROM],message[TO],message[MESSAGE])
                        self.session.add(msg_hist)
                        self.session.commit()
                    except:
                        log.error('Ошибка записи истории чата в БД')
                        print('Ошибка записи истории чата в БД')

            except:
                if self.alive:
                    print('Cервер разорвал соединение или получен некорректный ответ! Приложение завершает работу')
                    log.error('Reader: Сервер разорвал соединение или получен некорректный ответ!')
                    sock.close()
                self.alive = False
                break

    # процедура отправки сообщений на сервер
    def client_writer(self, sock, account):
        send_to = MAIN_CHANNEL
        console_prefix = f':> '
        # в цикле запрашиваем у пользователя ввод нового сообщения
        while self.alive:
            user_message = input(console_prefix)
            # Обработка служебных команд пользователя
            if user_message.startswith('!to'):  # выбор получателя для отправки
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
            if user_message == '!help':
                print(f'{account}! Для отправки личного сообщения напишите: to имя_получателя')
                print(
                    'Для отправки всем напишите !to all. Быстрый выбор клиента для ответа на последнее лс !r. Для получения списка подключенных клиентов !who.'
                    'Для показа списка контактов введите !show cl. Для обновления списка контактов команда !get cl.'
                    'Для добавления/удаления пользователя спиcка контактов: !add имя/!del имя. История сообщений !hist'
                    'Для выхода напишите !exit')
                log.debug('Вывод справки пользователю по команде !help')
                continue
            if user_message == '!exit':
                log.info('Пользователь вызвал закрытие клиента - exit')
                print('Выход из программы..')
                self.alive = False
                #sock.close()
                break
            if user_message == '!hist':
                log.info('Вывод истории сообщений')
                print('История сообщений')
                hist = self.session.query(Chat_histories.message_date, Chat_histories.message_owner,Chat_histories.channel,Chat_histories.message).filter_by(history_owner=self.account).all()
                for msg in hist:
                    print(f'{msg[0]} to {msg[2]} from {msg[3]}')
                continue
            if user_message == '!r':
                if self.last_private_user:
                    send_to = self.last_private_user
                    console_prefix = f'{account} to {self.last_private_user}:> '
                    log.debug(f'Получатель установлен на последнего писавшего в лс: {self.last_private_user}')
                    continue
            if user_message == '!who':
                message_to_send = self.create_message(SERVER, user_message, account)
                log.debug('Вывод списка пользователей в онлайн - !who')
            if user_message == '!show cl':
                log.debug('Вывод списка контактов - !show cl')
                #print(self.contact_list)
                try:
                    self.contact_list = []
                    for contact in self.session.query(User_contact_list.in_list_login).filter_by(owner_login=self.account).all():
                        self.contact_list.append(contact[0])
                    print(self.contact_list)
                except:
                    log.info('Ошибка показа списка пользователей из БД')
                    print('Ошибка показа списка пользователей из БД')
                continue
            if user_message == '!get cl':
                log.debug('Запрос списка контактов с сервера - !get cl')
                self.get_contact_list(sock)
                continue
            if user_message.startswith('!add'):
                log.debug('Добавление в список контактов - !add')
                usr = user_message.split()[1]
                self.set_contact_list(sock,ADD_CONTACT,usr)
                continue
            if user_message.startswith('!del'):
                log.debug('Удаление из списка контактов - !del')
                usr = user_message.split()[1]
                self.set_contact_list(sock,DEL_CONTACT,usr)
                continue
            if account == 'Admin' and re.findall('^[!]{3} stop', user_message):
                # Если админ написал !!! stop, то останавливаем сервер
                message_to_send = self.create_admin_message(user_message, account)
                log.info(f'Админ послал команду выключения сервера и сообщение {user_message}')
            elif user_message != '!who' and user_message != '!get cl':
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
        if len(sys.argv) < 4 and self.passw == '' and self.mode=='gui':
            conn_window.ui.StatusLabel.setText('Пароль не задан. Введите пароль')
            return app.exec()
        elif len(sys.argv) < 4 and self.passw == '' and mode=='con':
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
                log.info(f'Попытка подключения к {self.serv_addr} {self.serv_port}')
                conn_window.ui.StatusLabel.setText(f'Попытка подключения к {self.serv_addr} {self.serv_port}')
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
            conn_window.ui.StatusLabel.setText(f'Авторизация..')
            conn_window.update()
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
                conn_window.ui.StatusLabel.setText(f'Пароль неверен!')
                conn_window.update()
                self.alive = False
                return app.exec()
            #Если все хорошо, то переключаем режим клиента в переданный в параметре или оставляем по-умолчанию - полный
            if server_response.get('response') == OK:
                print('Соединение установлено!')
                log.info('Авторизация успешна. Соединение установлено!')
                conn_window.ui.StatusLabel.setText('Статус: Подключено')
                conn_window.update()
                conn_window.close()
                if self.mode == 'r':
                    print('Клиент в режиме чтения')
                    log.debug('Клиент в режиме чтения')
                    self.client_reader(s,self.account)
                elif self.mode == 'w':
                    print('Клиент в режиме записи')
                    log.debug('Клиент в режиме записи')
                    self.client_writer(s, self.account)
                elif self.mode == 'f' or self.mode == 'gui':
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
                    #self.get_contact_list(s)
                    while self.alive:
                        time.sleep(1)
                        continue
                else:
                    s.close()
                    raise Exception('Не верный режим клиента')
            else:
                #print('Что-то пошло не так..')
                log.error('Что-то пошло не так..')

        self.db_connection.close()
        s.close()
        exit(0)

class c_window(QtWidgets.QWidget):
    global server_address, server_port
    def __init__(self):
        super(c_window, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        self.ui.ExitButton.clicked.connect(QtWidgets.qApp.quit)
        self.ui.ConnectButton.clicked.connect(self.connectPressed)
        self.db_engine = create_engine('sqlite:///client_db.sqlite3')
        self.db_connection = self.db_engine.connect()
        self.Session = sessionmaker(bind=self.db_engine)
        self.session = self.Session()
        try:
            q = self.session.query(Last_user).first()
            self.ui.LoginLine.setText(q.login)
            if q.save_pwd == 1:
                self.ui.PwdLine.setText(q.pwd)
                self.ui.PwdSaveCheckBox.toggle()
            self.ui.ServAddrLine.setText(q.server_addr)
            self.ui.ServAddrPort.setText(q.server_port)
        except:
            pass





    def connectPressed(self):
        if not self.ui.PwdSaveCheckBox.isChecked():
            try:
                self.session.query(Last_user.save_pwd).update({"save_pwd": 0})
                self.session.commit()
            except:
                self.ui.StatusLabel.setText('Ошибка изменения флага сохранения пароля в БД')
                self.repaint()
                time.sleep(10)
        elif self.ui.PwdSaveCheckBox.isChecked():
            try:
                self.ui.StatusLabel.setText('Сохранение пароля в БД')
                self.repaint()
                q = self.session.query(Last_user).first()
                q.save_pwd = 1
                q.pwd = self.ui.PwdLine.text()
                self.session.commit()
            except:
                self.ui.StatusLabel.setText('Ошибка сохранения пароля в БД')
                self.repaint()
                time.sleep(10)

        self.db_connection.close()
        self.ui.StatusLabel.setText('Подключение...')
        self.account = self.ui.LoginLine.text()
        self.pwd = self.ui.PwdLine.text()
        server_address = self.ui.ServAddrLine.text()
        server_port = self.ui.ServAddrPort.text()
        # запуск основного кода клиента
        c = Client(acc=self.account, passw=self.pwd, mode='gui')
        c.start_client()
        #self.close()
        #QtWidgets.qApp.

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
        try: #пароль
            pwd = sys.argv[4]
        except IndexError:
            pass
        try: #режим запуска, r - только чтение, w - только отправка, f - полноценный клиент
            mode = sys.argv[5]
        except IndexError:
            pass

    if len(sys.argv) < 3:
        app = QtWidgets.QApplication(sys.argv)
        conn_window = c_window()
        app.exec()
        # запуск основного кода клиента
        #c = Client(acc=conn_window.account, mode=mode, passw=conn_window.pwd)
        #c.start_client()
    else:
        c = Client(acc=account,mode=mode, passw=pwd)
        c.start_client()
    #sys.exit(0)