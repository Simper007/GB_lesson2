import sys, json, time, logging, logs.config.client_config_log, decorators, re, os
from socket import *
from config import *
from threading import Thread

#Инициализация логирования клиента
log = logging.getLogger('Client_log')
logger = decorators.Log(log)

#Общая переменная для читателя и писателя сообщений
#Последний пользователь, писавший в лс:
last_private_user = ''

#функция создания сообщения в чате
def create_message(message_to, text, account_name='Guest'):
    return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

#функция спец сообщения для пользователя Admin
def create_admin_message(text, account_name):
    return {ACTION: 'Stop server', TIME: time.time(), TO: SERVER, FROM: account_name, MESSAGE: text}

#процедура чтения сообщений с сервера
def client_reader(sock, account):
    global alive, last_private_user
    #в цикле оправшиваем сокет на предмет наличия новых сообщений
    while alive:
        try:
            message = json.loads(sock.recv(1024).decode('utf-8'))
            log.info(f'Получено сообщение с сервера: {message}')
            if message[FROM] == account:
                #TODO
                print(message[MESSAGE].replace(f'{account}:> ','(me)',1))
            else:
                print(f'{message[MESSAGE]}')
            if message[TO] != MAIN_CHANNEL and re.findall('[^\(private\)]+',message[FROM]):
                last_private_user = message[FROM]
        except:
            if alive:
                print('Cервер разорвал соединение или получен некорректный ответ! Приложение завершает работу')
                log.error('Reader: Сервер разорвал соединение или получен некорректный ответ!')
                sock.close()
            alive = False
            break
    sys.exit(0)

#процедура отправки сообщений на сервер
def client_writer(sock, account):
    global alive
    send_to = MAIN_CHANNEL
    console_prefix = f':> '
    #в цикле запрашиваем у пользователя ввод нового сообщения
    while alive:
        user_message = input(console_prefix)
        #Обработка служебных команд пользователя
        if user_message.startswith('to'): #выбор получателя для отправки
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
            print('Для отправки всем напишите to all. Быстрый выбор клиента для ответа на последнее лс r. Для получения списка подключенных клиентов who. Для выхода напишите exit')
            log.debug('Вывод справки пользователю по команде help')
            continue
        if user_message == 'exit':
            log.info('Пользователь вызвал закрытие клиента - exit')
            alive = False
            sock.close()
            break
        if user_message == 'r':
            if last_private_user:
                send_to = last_private_user
                console_prefix = f'{account} to {last_private_user}:> '
                log.debug(f'Получатель установлен на последнего писавшего в лс: {last_private_user}')
                continue
        if user_message == 'who':
            message_to_send = create_message(SERVER, user_message, account)
            log.debug('Вывод списка пользователей в онлайн - who')
        if account == 'Admin' and re.findall('^[!]{3} stop',user_message):
            #Если админ написал !!! stop, то останавливаем сервер
            message_to_send = create_admin_message(user_message, account)
            log.info(f'Админ послал команду выключения сервера и сообщение {user_message}')
        elif user_message != 'who':
            #Формирование обычного сообщения
            message_to_send = create_message(send_to, user_message, account)
            log.debug('Формирование обычного сообщения')

        #Отправка сообщения
        try:
            if alive:
                sock.send(json.dumps(message_to_send).encode('utf-8'))
                log.info(f'Отправлено сообщение на сервер: {message_to_send}')
            else:
                break
        except:
            if alive:
                print('Сервер разорвал соединение! Приложение завершает работу')
                log.error('Writer: Сервер разорвал соединение!')
                sock.close()
            alive = False
            break

@logger
def create_presence_meassage(account_name, Action=PRESENCE):
    log.debug('Формирование приветственного сообщения')

    #Проверка параметров на соответствие протоколу
    if len(account_name)> 25:
        log.error('Имя пользователя более 25 символов!')
        raise ValueError

    if not isinstance(account_name, str):
        log.error('Полученное имя пользователя не является строкой символов')
        raise TypeError

    #Приветственное сообщение
    message = {
        ACTION: Action,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return message


#Основная функция клиента
@logger
def start_client(serv_addr=server_address, serv_port=server_port,action=PRESENCE, mode='f', account='Guest'):
    log.info('Запуск клиента')
    print('<<< Console IM >>>')
    #Если имя аккаунта не передано, то спросим
    if len(sys.argv) < 3:
        account = input('Введите имя аккаунта: ')
        if len(account) == 0: #Если пустой ввод, то имя по-умолчнию
            account='Guest'

    print(f'Здравствуйте {account}!')
    #Создаем сокет для общения с сервером
    with socket(AF_INET,SOCK_STREAM) as s:

        if not isinstance(serv_addr,str) or not isinstance(serv_port,int):
            log.error('Полученный адрес сервера или порт не является строкой или числом!')
            raise ValueError

        # установка связи с сервером
        try:
            if serv_addr == '0.0.0.0':
                serv_addr = 'localhost'
            log.info(f' Попытка подключения к {serv_addr} {serv_port}')
            s.connect((serv_addr,serv_port))
        except Exception as e:
            print('Ошибка подключения:', e)
            log.error(f'Ошибка подключения: {e}')
            raise

        #создание приветственного сообщения для сервера
        message = create_presence_meassage(account,action)

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
        #Если все хорошо, то переключаем режим клиента в переданный в параметре или оставляем по-умолчанию - полный
        if server_response.get('response') == OK:
            print('Соединение установлено!')
            log.info('Авторизация успешна. Соединение установлено!')
            if mode == 'r':
                print('Клиент в режиме чтения')
                log.debug('Клиент в режиме чтения')
                client_reader(s,account)
            elif mode == 'w':
                print('Клиент в режиме записи')
                log.debug('Клиент в режиме записи')
                client_writer(s, account)
            elif mode == 'f':
                log.debug('Клиент в полнофункциональном режиме')
                print(f'Отправка сообщений всем пользователям в канал {MAIN_CHANNEL}')
                print('Для получения помощи наберите help')
                #читаем сообщения в отдельном потоке
                read_thread = Thread(target=client_reader,args=(s,account))
                read_thread.daemon=True
                read_thread.start()
                #read_thread.join()
                client_writer(s, account)
            else:
                s.close()
                raise Exception('Не верный режим клиента')
        else:
            #print('Что-то пошло не так..')
            log.error('Что-то пошло не так..')
    return 0


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
    #запуск основного кода клиента
    start_client(account=account,mode=mode)
    #sys.exit(0)

