import sys
import json
import time
import datetime
import logging
import hmac
import logs.config.client_config_log
import decorators
import re
from sqlalchemy import or_
from socket import *
from config import *
from meta import *
from threading import Thread, Event, Lock
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, Qt, QEvent
from client_database import *
from PyQt5 import QtWidgets, uic, QtGui
from client_gui_settings import Ui_Form, AddContactDialog, DelContactDialog

# Инициализация логирования клиента
log = logging.getLogger('Client_log')
logger = decorators.Log(log)

# Инициализация подключения к БД
db_engine = create_engine('sqlite:///client_db.sqlite3')
db_connection = db_engine.connect()
Session_class = sessionmaker(bind=db_engine)

# Инициализация общих эвентов и блокировок
alive_event = Event()
socket_lock = Lock()


class Client(Thread, QObject):
    """
    Основной класс клиента чата, функции приема/отправки сообщений, изменения списка контактов и т.п.
    """
    global log, logger, main_window, Session_class
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(
            self,
            serv_addr=server_address,
            serv_port=server_port,
            mode='f',
            acc='Guest',
            passw=''):
        Thread.__init__(self)
        QObject.__init__(self)
        self.serv_addr = serv_addr
        self.serv_port = serv_port
        self.action = PRESENCE
        self.mode = mode
        self.account = acc
        self.passw = passw
        self.socket_is_ready = False

        # Последний пользователь, писавший в лс:
        self.last_private_user = ''

        self.alive = True
        self.sock = None
        self.contact_list = []
        self.session = Session_class()
        self.start_client()

    @logger
    def get_contact_list(self, show_progress='Y'):
        """
        Функция запроса списка контактов с сервера
        """

        log.info('Обновление списка контактов с сервера..')
        if show_progress == 'Y':
            print('Обновление списка контактов с сервера..')

        msg = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER_LOGIN: self.account
        }

        try:
            with socket_lock:
                # print('Отправка команды обновления списка')
                self.sock.send(json.dumps(msg).encode('utf-8'))
                answer = json.loads(self.sock.recv(1024).decode('utf-8'))
            if ALERT in answer:
                print(answer[ALERT])
                try:
                    self.session.query(User_contact_list).delete()
                    self.session.commit()
                    for contact in answer[ALERT]:
                        # print(contact)
                        cl = User_contact_list(self.account, contact)
                        self.session.add(cl)
                        self.session.commit()

                except BaseException as e:
                    log.error(
                        'Ошибка изменения списка контактов в БД клиента', e)
                    print('Ошибка изменения списка контактов в БД клиента', e)
                log.info('Список контактов обновлен')
        except BaseException as e:
            log.error(
                'Ошибка отправки команды на обновление списка контактов', e)
            if show_progress == 'Y':
                print('Ошибка получения списка контактов', e)
            return ERROR

    @logger
    def set_contact_list(self, command, user):
        """
        Функция добавления/удаления элемента списка контактов с вызовом синхронизации списка с сервером
        """
        msg = {
            ACTION: command,
            USER_ID: user,
            TIME: time.time(),
            USER_LOGIN: self.account
        }
        try:
            with socket_lock:
                self.sock.send(json.dumps(msg).encode('utf-8'))
                answer = json.loads(self.sock.recv(1024).decode('utf-8'))
            if answer[RESPONSE] == ACCEPTED:
                log.info('Список контактов изменен')
                print('Список контактов изменен')
                self.get_contact_list('N')
            elif answer[RESPONSE] == CONFLICT:
                log.info(
                    'Попытка добавить самих себя или контакт уже есть/уже нет в списке')
                print(
                    'Вы пытаетесь добавить самих себя или контакт уже есть/уже нет в списке')
            elif answer[RESPONSE] == SERVER_ERROR:
                log.error(
                    'Ошибка изменения списка контактов на сервере')
                print('Ошибка списка контактов на сервере')
        except BaseException:
            log.error('Ошибка отправки команды на изменение списка контактов')
            print('Ошибка изменения списка контактов 1')
            return ERROR

    @logger
    def send_message(self, message_to, text):
        """
        Функция отправки сообщения на сервер
        """
        if self.alive:
            msg = {
                ACTION: MSG,
                TIME: time.time(),
                TO: message_to,
                FROM: self.account,
                MESSAGE: text}

            msg = self.chk_msg_before_send(self.account, msg)
            if msg == INT_CMD:
                return 0

            with socket_lock:
                try:
                    self.sock.send(json.dumps(msg).encode('utf-8'))
                    # answer = json.loads(self.sock.recv(1024).decode('utf-8'))
                except Exception as e:
                    log.error('Ошибка отправки сообщения:', e)
                    return -1
                else:
                    return 0
        else:
            log.error('Попытка отправки сообщения при отключенном клиенте')
            return -2

    @logger
    def create_admin_message(self, text, account_name):
        """
        Функция отправки спец сообщения для пользователя Admin
        """
        msg = {
            ACTION: 'Stop server',
            TIME: time.time(),
            TO: SERVER,
            FROM: account_name,
            MESSAGE: text}

        with socket_lock:
            try:
                self.sock.send(json.dumps(msg).encode('utf-8'))
                # answer = json.loads(sock.recv(1024).decode('utf-8'))
            except Exception as e:
                log.error('Ошибка отправки Admin сообщения:', e)
                return -1
        return 0

    def add_msg_to_hist(self, msg_from, msg_to, msg, direction):
        """
        Процедура добавления сообщения в историю пользователя в локальную БД
        """
        msg_hist = Chat_histories(
            self.account,
            msg_from,
            msg_to,
            msg,
            direction,
            datetime.datetime.now())
        self.session.add(msg_hist)
        self.session.commit()
        self.new_message.emit(msg_from)

    def client_exit(self):
        """
        Процедура завершения приложения с отправкой команды о выходе на сервер
        """

        if not self.alive:
            message = {
                ACTION: EXIT,
                TIME: time.time(),
                USER_LOGIN: self.account
            }
            with socket_lock:
                try:
                    self.sock.send(json.dumps(message).encode('utf-8'))
                except OSError:
                    pass

        alive_event.clear()
        self.alive = False
        log.debug('Клиент завершает работу.')
        self.sock.close()
        # log.debug('Клиент завершает работу.')
        time.sleep(0.5)

    def who_online(self):
        """
        Функция отправки команды "Кто в сети?" на сервер
        """
        return self.send_message(SERVER, '!who')

    def chk_msg_before_send(self, account, msg):
        """
        Функция предобработки сообщений перед отправкой на сервер.
        Вызывает внутренние команды, если сообщение содержит ключевые слова
        """
        send_to = msg[TO]
        console_prefix = f':> '
        user_message = msg[MESSAGE]
        # в цикле запрашиваем у пользователя ввод нового сообщения
        if self.mode != 'gui':
            while self.alive:
                user_message = input(console_prefix)
                # TODO
                break

        # Обработка служебных команд пользователя
        if user_message.startswith('!to'):
            # выбор получателя для отправки
            destination = user_message.split()
            print(destination)
            try:
                send_to = destination[1]
                if destination[1] == 'all':
                    send_to = MAIN_CHANNEL
                    console_prefix = f':> '
                else:
                    console_prefix = f'{account} to {destination[1]}:> '
                    log.debug(f'Получатель установлен на: {send_to}')
            except IndexError:
                print('Не задан получатель')
        if user_message == '!help':
            if not self.mode == 'gui':
                log.debug('Вывод справки пользователю по команде !help')
                print(
                    f'{account}! Для отправки личного сообщения напишите: !to имя_получателя')
                print(
                    'Для отправки всем напишите !to all. Быстрый выбор клиента для ответа на последнее лс !r. Для получения списка подключенных клиентов !who.'
                    'Для показа списка контактов введите !show cl. Для обновления списка контактов команда !get cl.'
                    'Для добавления/удаления пользователя спиcка контактов: !add имя/!del имя. История сообщений !hist'
                    'Для выхода напишите !exit')

            else:
                main_window.mess_to_userchat(
                    'Для отправки личного сообщения напишите: !to имя_получателя или дважды кликните по нему в списке, введите сообщение и нажмите Отправить.\n'
                    'Для отправки всем напишите !to all и нажмите Отправить. Для получения списка подключенных клиентов !who или кнопка Кто в сети?.\n'
                    'Для обновления списка контактов c сервера команда !get cl.\n'
                    'Для выхода напишите !exit или нажмите Выход')
            return INT_CMD
        if user_message == '!exit':
            log.info('Пользователь вызвал закрытие клиента - exit')
            print('Выход из программы..')
            self.client_exit()
            main_window.close()
            return INT_CMD
        if user_message == '!hist':
            log.info('Вывод истории сообщений')
            print('История сообщений')
            hist = self.session.query(
                Chat_histories.message_date,
                Chat_histories.message_owner,
                Chat_histories.channel,
                Chat_histories.message).filter_by(
                history_owner=self.account).all()
            for msg in hist:
                print(f'{msg[0]} от {msg[2]} для {msg[3]}')
            return INT_CMD
        if user_message == '!r':
            if self.last_private_user:
                send_to = self.last_private_user
                console_prefix = f'{account} to {self.last_private_user}:> '
                main_window.set_active_chat(send_to)
                log.debug(
                    f'Получатель установлен на последнего писавшего в лс: {self.last_private_user}')
                return INT_CMD
        if user_message == '!who':
            # self.who_online()
            log.debug('Вывод списка пользователей в онлайн - !who')
            msg[TO] = SERVER
            return msg
        if user_message == '!show cl':
            log.debug('Вывод списка контактов - !show cl')
            # print(self.contact_list)
            try:
                self.contact_list = []
                for contact in self.session.query(
                        User_contact_list.in_list_login).filter_by(
                        owner_login=self.account).all():
                    self.contact_list.append(contact[0])
                print(self.contact_list)
            except BaseException:
                log.info('Ошибка показа списка пользователей из БД')
                print('Ошибка показа списка пользователей из БД')
            return INT_CMD
        if user_message == '!get cl':
            log.debug('Запрос списка контактов с сервера - !get cl')
            self.get_contact_list()
            main_window.create_user_list()
            return INT_CMD
        if user_message.startswith('!add'):
            log.debug('Добавление в список контактов - !add')
            usr = user_message.split()[1]
            self.set_contact_list(ADD_CONTACT, usr)
            main_window.create_user_list()
            return INT_CMD
        if user_message.startswith('!del'):
            log.debug('Удаление из списка контактов - !del')
            usr = user_message.split()[1]
            self.set_contact_list(DEL_CONTACT, usr)
            main_window.create_user_list()
            return INT_CMD
        if account == 'Admin' and re.findall('^[!]{3} stop', user_message):
            # Если админ написал !!! stop, то останавливаем сервер
            message_to_send = self.create_admin_message(user_message, account)
            if message_to_send == -1:
                log.error('Ошибка отправки команды выключения сервера')
            else:
                log.info(
                    f'Админ послал команду выключения сервера и сообщение {user_message}')
            return INT_CMD
        elif user_message != '!who' and user_message != '!get cl':
            # Отправка сообщения
            if self.alive:
                # Отправка обычного сообщения
                msg[TO] = send_to
                msg[MESSAGE] = user_message
                main_window.current_chat = send_to
                main_window.set_active_chat()
                return msg
        elif not self.mode == 'gui' and TO in msg and msg[TO] == MAIN_CHANNEL:
            # Если консольный режим то отображаем от кого сообщение
            msg[MESSAGE] = f'{msg[FROM]}:> {msg[MESSAGE]}'
        return msg

    def run(self):
        """
        Процедура чтения сообщений с сервера
        """
        # в цикле оправшиваем сокет на предмет наличия новых сообщений
        while self.alive:
            time.sleep(1)
            if self.socket_is_ready:
                # print('run',self.sock)
                try:
                    with socket_lock:
                        self.sock.settimeout(0.5)
                        # ??? Рвет соединение по таймауту ???
                        message = json.loads(
                            self.sock.recv(1024).decode('utf-8'))
                        # return
                        # #чтобы запустить только в режиме отправки
                        # закомментируйте строчку выше и раскомментируйте эту
                except OSError as e:
                    pass
                    """
                    if self.alive:
                        print(
                            f'Cервер разорвал соединение или получен некорректный ответ! Приложение завершает работу. {e}')
                        log.error(
                            f'Reader: Сервер разорвал соединение или получен некорректный ответ! {e}')
                        self.alive = False
                        self.connection_lost.emit()
                    # self.client_exit()
                    # break
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    print(
                        'Cервер разорвал соединение или получен некорректный ответ! Приложение завершает работу')
                    log.error(
                        'Reader: Сервер разорвал соединение или получен некорректный ответ!')
                    self.alive = False
                    self.connection_lost.emit()
                    """
                else:

                    log.info(f'Получено сообщение с сервера: {message}')
                    if FROM in message and message[FROM] == self.account:
                        if not self.mode == 'gui':
                            print(
                                message[MESSAGE].replace(
                                    f'{self.account}:> ', '(моё)', 1))
                        try:
                            self.add_msg_to_hist(
                                message[FROM], message[TO], message[MESSAGE], 'in')
                            # main_window.history_list_update()
                        except BaseException as e:
                            log.error('Ошибка записи истории чата в БД', e)
                            print('Ошибка записи истории чата в БД', e)

                    elif RESPONSE in message and SHUTDOWN in message[RESPONSE]:
                        log.error(
                            f'Сервер завершает работу: {message[RESPONSE]}')
                        print(
                            f'Сервер завершает работу: {message[RESPONSE]}')
                        main_window.mess_to_userchat(
                            f'Сервер завершает работу: {message[RESPONSE]}\n Приложение закрывается..')
                        self.client_exit()
                        time.sleep(5)
                        QtWidgets.qApp.quit()

                    elif RESPONSE in message and not message[RESPONSE] in (
                            ACCEPTED, CONFLICT, SERVER_ERROR, OK):
                        log.error(
                            f'Неизвестный код ответа сервера {message[RESPONSE]}')
                        print(
                            f'Неизвестный код ответа сервера {message[RESPONSE]}')

                    elif FROM in message and message[FROM] != self.account and message[TO] == MAIN_CHANNEL:
                        print(f'{message[MESSAGE]}')
                        try:
                            self.add_msg_to_hist(
                                message[FROM], message[TO], message[MESSAGE], 'in')
                            # main_window.history_list_update()
                        except BaseException:
                            log.error('Ошибка записи истории чата в БД')
                            print('Ошибка записи истории чата в БД')

                    if TO in message and message[TO] != MAIN_CHANNEL and re.findall(
                            r'[^\(private\)]+', message[FROM]):
                        self.last_private_user = message[FROM]
                        if self.mode == 'gui':
                            message[MESSAGE] = message[MESSAGE].replace(
                                f'(private){message[FROM]}:> ', '')
                        try:
                            self.add_msg_to_hist(
                                message[FROM], message[TO], message[MESSAGE], 'in')
                            # main_window.history_list_update()
                        except BaseException:
                            log.error('Ошибка записи истории чата в БД')
                            print('Ошибка записи истории чата в БД')
                finally:
                    self.sock.settimeout(5)

    @logger
    def create_presence_message(
            self,
            account_name,
            account_password='',
            Action=PRESENCE):
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

    def server_auth(self, secret_key):
        """
        Аутентификация клиента на удаленном сервисе.
        secret_key - ключ шифрования, известный клиенту и серверу
        """
        main_window.conn_window.ui.StatusLabel.setText(f'Аутентификация..')
        main_window.conn_window.repaint()
        time.sleep(0.1)
        try:
            # принимаем случайное послание от сервера
            with socket_lock:
                message = self.sock.recv(32)
            # вычисляем HMAC-функцию
                hash = hmac.new(secret_key, message)
                digest = hash.digest()
            # отправляем ответ серверу
                self.sock.send(digest)
        except BaseException:
            log.error('Ошибка аутентификации сервера')
            main_window.conn_window.ui.StatusLabel.setText(
                f'Ошибка аутентификации сервера')
            main_window.conn_window.repaint()
            time.sleep(0.5)
            return ERROR
        else:
            return OK

    def create_socket(self):
        """
        Создание сокета для общения с сервером
        """
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(5)
        # установка связи с сервером
        log.info(
            f'Попытка подключения к {self.serv_addr} {self.serv_port}')
        main_window.conn_window.ui.StatusLabel.setText(
            f'Попытка подключения к {self.serv_addr} {self.serv_port}')
        main_window.conn_window.repaint()
        # print(f' Попытка подключения к {self.serv_addr} {self.serv_port}')
        connected = False
        for i in range(5):
            log.info(f'Попытка подключения №{i + 1}')
            try:
                # print(f'Попытка подключения №{i + 1}')
                self.sock.connect((self.serv_addr, self.serv_port))
            except (OSError, ConnectionRefusedError) as e:
                print(f'Ошибка подключения, попытка {i + 1}: {e}')
                log.error(f'Ошибка подключения, попытка {i + 1}: {e}')
            else:
                connected = True
                break
            time.sleep(1)
        if not connected:
            self.alive = False
            alive_event.clear()
            main_window.conn_window.ui.StatusLabel.setText(
                f' Ошибка подключения, проверьте сеть')
            main_window.conn_window.repaint()
            return ERROR

        # аутентификация сервера
        secret_key = b'Quick IM the BEST!'
        auth = self.server_auth(secret_key)
        if auth == ERROR:
            return ERROR
        main_window.conn_window.ui.StatusLabel.setText(
            f'Аутентификация успешна')
        main_window.conn_window.repaint()
        time.sleep(0.1)

        # создание приветственного сообщения для сервера
        message = self.create_presence_message(
            self.account, self.passw, self.action)

        if isinstance(message, dict):
            message = json.dumps(message)
        log.debug(
            f'Отправляю приветственное сообщение "{message}" на сервер')
        main_window.conn_window.ui.StatusLabel.setText(f'Авторизация..')
        main_window.conn_window.repaint()
        time.sleep(0.1)
        with socket_lock:
            try:
                self.sock.send(message.encode('utf-8'))
                log.debug('и жду ответа')
                server_response = json.loads(self.sock.recv(1024).decode('utf-8'))
            except Exception as e:
                print('Ошибка при получении ответа от сервера', e)
            else:
                log.debug(f'Ответ: {server_response}')
                # Если сервер ответил нестандартным кодом, то завершаем работу
                if server_response.get(RESPONSE) not in StandartServerCodes:
                    log.error(
                        f'Неизвестный код ответа от сервера: {server_response.get(RESPONSE)}')
                    raise UnknownCode(server_response.get(RESPONSE))
                # Если сервер ответил Неверный пароль, то завершаем работу
                if server_response.get('response') == WRONG_PASSW:
                    print(f'Пароль неверен! Попробуйте переподключиться с другим паролем!')
                    log.warning(
                        f'Пароль неверен! Попробуйте переподключиться с другим паролем!')

                    main_window.conn_window.ui.StatusLabel.setText(
                        f'Пароль неверен!')
                    main_window.conn_window.repaint()
                    return ERROR

                # Если все хорошо, то переключаем режим клиента в переданный в
                # параметре или оставляем по-умолчанию - полный
                if server_response.get('response') == OK:
                    print('Соединение установлено!')
                    log.info('Авторизация успешна. Соединение установлено!')
                    main_window.conn_window.ui.StatusLabel.setText(
                        'Статус: Авторизация успешна. Подключено')
                    main_window.conn_window.repaint()
                    time.sleep(0.5)
                    del main_window.conn_window
                    return OK
                else:
                    print('Что-то пошло не так.. Ответ сервера нераспознан')
                    log.error('Ответ сервера нераспознан')
                    return ERROR

    @logger
    def start_client(self):
        """
        Процедура запуска транспорта для сообщений
        """
        log.info('Запуск клиента')
        print('<<< Quick IM >>>')
        # Если имя аккаунта не передано, то спросим
        if len(sys.argv) < 3 and self.account == account:
            self.account = input('Введите имя аккаунта: ')
            if len(self.account) == 0:  # Если пустой ввод, то имя по-умолчнию
                self.account = 'Guest'

        # Если пароль аккаунта не передан, то спросим
        if len(sys.argv) < 4 and self.passw == '' and self.mode == 'gui':
            main_window.conn_window.ui.StatusLabel.setText(
                'Пароль не задан. Введите пароль')
            return app.exec_()
        elif len(sys.argv) < 4 and self.passw == '' and mode == 'con':
            self.passw = input('Пароль не задан. Введите пароль: ')

        print(f'Здравствуйте {self.account}!')
        if self.serv_addr == '0.0.0.0':
            self.serv_addr = 'localhost'

        if not isinstance(
                self.serv_addr,
                str) or not isinstance(
                self.serv_port,
                int):
            log.error(
                'Полученный адрес сервера или порт не является строкой или числом!')
            raise ValueError

        # Пытаемся подключиться
        connected = self.create_socket()
        if connected == ERROR:
            return self.client_exit()

        alive_event.set()

        try:
            print('main', self.sock)
            self.get_contact_list('N')
            self.socket_is_ready = True
        except BaseException:
            log.error('Ошибка загрузки списка контактов с сервера')

        if self.mode == 'r':
            print('Клиент в режиме чтения')
            log.debug('Клиент в режиме чтения')
            self.run(self.sock, self.account)
        elif self.mode == 'w':
            print('Клиент в режиме записи')
            log.debug('Клиент в режиме записи')
            # self.chk_msg_before_send(self.sock, self.account)
        elif self.mode == 'f' or self.mode == 'gui':

            log.debug('Клиент в полнофункциональном режиме')
            print(
                f'Отправка сообщений всем пользователям в канал {MAIN_CHANNEL}')
            print('Для получения помощи наберите !help')
            main_window.mess_to_userchat(f'Отправка сообщений всем пользователям в канал {MAIN_CHANNEL} \n'
                                         'Для получения помощи нажмите Помощь или наберите !help')

        else:
            self.client_exit()
            # self.sock.close()
            raise Exception('Не верный режим клиента')
        """
        # self.db_connection.close()
        s.close()
        exit(0)
        """


class c_window(QtWidgets.QWidget):
    """
    Окно подключения, логин/пароль. Вызывается из класса главного окна
    """
    global server_address, server_port, Session_class, mode, account, pwd

    def __init__(self):
        super(c_window, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        """
        Инициализация интерфейса окна подключения
        """
        self.ui.ExitButton.clicked.connect(QtWidgets.qApp.quit)
        self.ui.ConnectButton.clicked.connect(self.connectPressed)
        self.session = Session_class()
        if len(sys.argv) >= 5:
            self.ui.LoginLine.setText(str(account))
            self.ui.PwdLine.setText(str(pwd))
            self.ui.ServAddrLine.setText(str(server_address))
            self.ui.ServAddrPort.setText(str(server_port))
            self.connectPressed()
        else:
            try:
                q = self.session.query(Last_user).first()
                self.ui.LoginLine.setText(str(q.login))
                if q.save_pwd == 1:
                    self.ui.PwdLine.setText(str(q.pwd))
                    self.ui.PwdSaveCheckBox.toggle()
                self.ui.ServAddrLine.setText(str(q.server_addr))
                self.ui.ServAddrPort.setText(str(q.server_port))
            except BaseException as e:
                log.error(
                    f'Ошибка сохранения последнего логина/пароля в БД {e}')

    def event(self, e):
        """
        Обработка Enter и Esc в окне подключения
        """
        if e.type() == QEvent.KeyPress and e.key() == 16777221:
            self.connectPressed()

        if e.type() == QEvent.KeyPress and e.key() == 16777216:
            QtWidgets.qApp.quit()
        if alive_event.isSet():
            self.close()

        return QtWidgets.QWidget.event(self, e)

    def connectPressed(self):
        """
        Обработка нажатия кнопки Подключить в окне подключения.
        Сохраняет последний введеный логин/пароль в БД, вызывает подключение
        и обновление списка пользователей главного окна из локального списка пользователей
        """
        if not self.ui.PwdSaveCheckBox.isChecked():
            try:
                self.session.query(Last_user.save_pwd).update({"save_pwd": 0})
                self.session.commit()
            except BaseException:
                self.ui.StatusLabel.setText(
                    'Ошибка изменения флага сохранения пароля в БД')
                self.repaint()
                time.sleep(10)
        elif self.ui.PwdSaveCheckBox.isChecked():
            try:
                self.ui.StatusLabel.setText('Сохранение пароля в БД')
                self.repaint()
                q = self.session.query(Last_user).first()
                q.save_pwd = 1
                q.pwd = self.ui.PwdLine.text()
                q.login = self.ui.LoginLine.text()
                self.session.commit()
            except BaseException:
                self.ui.StatusLabel.setText('Ошибка сохранения пароля в БД')
                self.repaint()
                time.sleep(10)

        self.ui.StatusLabel.setText('Подключение...')
        self.account = self.ui.LoginLine.text()
        self.pwd = self.ui.PwdLine.text()
        main_window.start_client()
        main_window.setWindowTitle(f'Python Chat v0.1 - {self.account}')
        main_window.create_user_list()


class m_window(QtWidgets.QMainWindow):
    """
    Класс главного окна приложения
    """
    global server_address, server_port, Session_class, mode

    def __init__(self):
        super(m_window, self).__init__()
        self.ui = uic.loadUi('main_window.ui', self)
        self.conn_window = c_window()
        self.initUI()
        self.show()

    def initUI(self):
        """
        Инициализация интерфейса главного окна
        """
        self.ui.ExitButton.clicked.connect(self.safe_exit)
        self.ui.ChatMessList.setWordWrap(True)
        self.ui.SendButton.setDisabled(True)
        self.current_chat = MAIN_CHANNEL
        self.ui.textBox.textChanged.connect(self.set_active_send)
        self.ui.SendButton.clicked.connect(self.on_send)
        self.messages = QtWidgets.QMessageBox()
        self.ui.Add_user_button.clicked.connect(self.add_to_cl)
        self.ui.Del_user_button.clicked.connect(self.del_from_cl)
        self.ui.UserList.doubleClicked.connect(self.select_active_user)
        self.ui.MCButton.clicked.connect(self.to_all)
        self.history_model = None
        self.session = Session_class()
        self.ui.SendButton.setAutoDefault(True)

    def safe_exit(self):
        """
        Закрытие GUI с остановкой потока доставщика
        """
        if alive_event.isSet():
            self.client.client_exit()
        QtWidgets.qApp.quit()

    def event(self, e):
        """
        Обработка нажатий на Esc и Enter в основном окне
        """
        if e.type() == QEvent.KeyPress and e.key() == 16777221:
            self.on_send()

        if e.type() == QEvent.KeyPress and e.key() == 16777216:
            QtWidgets.qApp.quit()

        return QtWidgets.QMainWindow.event(self, e)

    def to_all(self):
        """
        Переключение отправки на общий канал
        """
        self.current_chat = MAIN_CHANNEL
        self.set_active_chat()

    def add_to_cl(self):
        """
        Обработка нажатия кнопки "Добавить контакт" главного окна
        Вызывает окно для ввода имени контакта
        """
        global add_dialog
        add_dialog = AddContactDialog()
        add_dialog.ui.buttonBox.accepted.connect(self.add_ok)
        add_dialog.show()

    def add_ok(self):
        """
        Обработка нажатия кнопки "Ок" при добавлении контакта
        Отправка запроса на сервер и обновление списка контактов
        """
        global add_dialog
        user = add_dialog.ui.plainTextEdit.toPlainText()
        if not user:
            add_dialog.ui.add_user_info_label.setText(
                'Имя не может быть пустым!')
            add_dialog.repaint()
            return
        # print(user)
        self.client.set_contact_list(ADD_CONTACT, user)
        add_dialog.close()
        self.create_user_list()

    def del_from_cl(self):
        """
        Обработка нажатия кнопки "Удалить контакт" главного окна
        Вызывает окно для ввода имени контакта
        """
        global del_dialog
        del_dialog = DelContactDialog()
        i = 0
        try:
            del_dialog.ui.cl_comboBox.addItems(sorted([contact[0] for contact in self.session.query(
                User_contact_list.in_list_login).filter_by(owner_login=self.account).all()]))
        except BaseException:
            log.error('Ошибка формирования списка для формы удаления')
        del_dialog.ui.del_form_buttonBox.accepted.connect(self.del_ok)
        del_dialog.show()

    def del_ok(self):
        """
        Обработка нажатия кнопки "Ок" при удалении контакта
        Отправка запроса на сервер и обновление списка контактов
        """
        global del_dialog
        user = del_dialog.cl_comboBox.currentText()
        # print(user)
        self.client.set_contact_list(DEL_CONTACT, user)
        del_dialog.close()
        self.create_user_list()

    def select_active_user(self):
        """
        Функция обработчик даблклика по контакту. Меняет канал отправки
        """
        self.current_chat = self.ui.UserList.currentIndex().data()
        self.set_active_chat()

    def set_active_send(self):
        """
        При изменении текста в окне ввода делаем кнопку "Отправить" активной
        """
        self.ui.SendButton.setEnabled(True)

    def on_send(self):
        """
        Обработчик нажатия кнопки "Отправить"
        Забираем текст, очищаем поле ввода, делаем кнопку неактивной, отправляем сообщение на сервер
        """
        message_text = self.ui.textBox.toPlainText()
        self.ui.textBox.clear()
        self.ui.SendButton.setDisabled(True)
        if not message_text or message_text == 'Начните печатать здесь..':
            return
        try:
            # print(self.current_chat)
            self.client.send_message(self.current_chat, message_text)
        except Exception as err:
            self.messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            if err.errno:
                log.error(f'on_send: Потеряно соединение с сервером! {err}')
                self.messages.critical(
                    self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError) as e:
            log.error(f'on_send: Потеряно соединение с сервером! {e}')
            self.messages.critical(
                self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.client.add_msg_to_hist(
                self.account, self.current_chat, message_text, 'out')
            log.debug(
                f'Отправлено сообщение для {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(str)
    def history_list_update(self, str=''):
        """
        Процедура обновления главного окна с сообщениями.
        Разные цвета для входящих, исходящих и сообщений от сервера
        """
        if self.current_chat == MAIN_CHANNEL:
            hist_list = sorted(
                self.session.query(
                    Chat_histories.message_owner,
                    Chat_histories.channel,
                    Chat_histories.message,
                    Chat_histories.message_date,
                    Chat_histories.direction).filter_by(
                    history_owner=self.account).filter(
                    or_(
                        Chat_histories.channel == v for v in (
                            self.current_chat,
                            self.account))).all(),
                key=lambda item: item[3])
        else:
            hist_list = sorted(
                self.session.query(
                    Chat_histories.message_owner,
                    Chat_histories.channel,
                    Chat_histories.message,
                    Chat_histories.message_date,
                    Chat_histories.direction).filter_by(
                    history_owner=self.account).filter(
                    or_(
                        Chat_histories.message_owner == v for v in (
                            self.current_chat,
                            self.account,
                            SERVER))).filter(
                    or_(
                        Chat_histories.channel == v for v in (
                            self.current_chat,
                            self.account))).all(),
                key=lambda item: item[3])

        # Если модель не создана, создадим.
        if not self.history_model:
            self.history_model = QtGui.QStandardItemModel()
            self.ui.ChatMessList.setModel(self.history_model)
        # Очистим от старых записей
        self.history_model.clear()
        # Берём не более 20 последних записей.
        length = len(hist_list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_index, length):
            item = hist_list[i]
            # print(item)
            if item[4] == 'in' and item[1] == MAIN_CHANNEL and item[0] != self.account:
                mess = QtGui.QStandardItem(
                    f'{item[3].replace(microsecond=0)} Входящее от {item[0]}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QtGui.QBrush(QtGui.QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            elif item[4] == 'in' and item[1] != MAIN_CHANNEL and item[0] == SERVER:
                mess = QtGui.QStandardItem(
                    f'{item[3].replace(microsecond=0)} Системное сообщение:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QtGui.QBrush(QtGui.QColor(145, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            elif item[4] == 'in' and item[1] != MAIN_CHANNEL and item[0] != SERVER:
                mess = QtGui.QStandardItem(
                    f'{item[3].replace(microsecond=0)} Входящее ЛС от {item[0]}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QtGui.QBrush(QtGui.QColor(190, 203, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            elif item[4] == 'out':
                mess = QtGui.QStandardItem(
                    f'{item[3].replace(microsecond=0)} Исходящее в канал {item[1]}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QtGui.QBrush(QtGui.QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.ChatMessList.scrollToBottom()

    def mess_to_userchat(self, text):
        """
        Вывод произвольного сообщения пользователю в окно чата
        """
        if not self.history_model:
            self.history_model = QtGui.QStandardItemModel()
            self.ui.ChatMessList.setModel(self.history_model)
        mess = QtGui.QStandardItem(text)
        mess.setEditable(False)
        mess.setBackground(QtGui.QBrush(QtGui.QColor(255, 220, 220)))
        mess.setTextAlignment(Qt.AlignLeft)
        self.history_model.appendRow(mess)
        self.ui.ChatMessList.scrollToBottom()

    def set_active_chat(self):
        """
        Вывод произвольного сообщения пользователю в окно чата
        """
        self.ui.statusbar.showMessage(f'Отправка в канал: {self.current_chat}')
        self.repaint()

    def create_user_list(self):
        """
        Формирование списка контактов из локальной БД
        """
        self.ui.UserList.setColumnCount(1)
        self.ui.UserList.setRowCount(30)
        self.UserList.setHorizontalHeaderLabels(['Список контактов:'])
        i = 0
        try:
            for contact in self.session.query(User_contact_list).filter_by(
                    owner_login=self.account).all():
                self.ui.UserList.setItem(
                    0, i, QtWidgets.QTableWidgetItem(contact.in_list_login))
                i = i + 1
        except BaseException as e:
            log.error(
                f'Main_window: Ошибка загрузки списка контактов из БД - {e}')
            pass
        self.ui.UserList.setRowCount(i)
        self.ui.UserList.resizeColumnsToContents()
        self.ui.UserList.resizeRowsToContents()
        self.ui.UserList.horizontalHeader().setStretchLastSection(True)
        self.ui.UserList.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection)
        self.ui.UserList.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.repaint()

    def start_client(self):
        """
        Запуск обработчика сообщений
        """
        self.account = self.conn_window.account
        self.client = Client(
            acc=self.conn_window.account,
            passw=self.conn_window.pwd,
            mode='gui',
            serv_addr=self.conn_window.ui.ServAddrLine.text(),
            serv_port=int(
                self.conn_window.ui.ServAddrPort.text()))
        self.client.setDaemon(True)
        self.client.start()
        self.client.new_message.connect(self.history_list_update)
        self.client.connection_lost.connect(self.connection_lost)
        self.ui.WhoButton.clicked.connect(self.client.who_online)
        self.ui.HelpButton.clicked.connect(
            lambda: self.client.send_message(
                self.current_chat, '!help'))

    @pyqtSlot()
    def connection_lost(self):
        """
        Выдача сообщения о ошибке связи и завершение работы приложения
        """
        self.messages.warning(
            self,
            'Сбой соединения',
            'Потеряно соединение с сервером.')
        self.close()


if __name__ == "__main__":
    # Проверка аргументов при запуске через консоль
    if len(sys.argv) > 1:  # адрес сервера
        server_address = sys.argv[1]
    if len(sys.argv) > 2:  # порт сервера
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print('Порт должен быть целым числом!')
            log.error(
                'Переданный номер порта для соединения с сервером не целое число')
        try:  # имя аккаунта в чате
            account = sys.argv[3]
        except IndexError:
            pass
        try:  # пароль
            pwd = sys.argv[4]
        except IndexError:
            pass
        try:  # режим запуска, r - только чтение, w - только отправка, f - полноценный клиент, gui - полноценный с gui
            mode = sys.argv[5]
        except IndexError:
            pass

    if len(sys.argv) < 3 or mode == 'gui':
        # TODO Вернуть обработку всех аргументов в гуи при запуске из консоли
        app = QtWidgets.QApplication(sys.argv)
        # db = sqlalchemy(app)
        main_window = m_window()
        app.exec_()
    else:
        # запуск основного кода клиента в консольном режиме
        c = Client(acc=account, mode=mode, passw=pwd)
        c.start_client()

    db_connection.close()
    # sys.exit(0)
