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
import sys, json, time
from config import *
from socket import *

def check_correct_presence_and_response(presence_message):
    if ACTION in presence_message and presence_message[ACTION] == 'Unknown':
        return {RESPONSE: UNKNOWN_ERROR}
    elif ACTION in presence_message and \
                    presence_message[ACTION] == PRESENCE and \
                    TIME in presence_message and \
            isinstance(presence_message[TIME], float):
        # Если всё хорошо шлем ОК
        return {RESPONSE: OK}
    else:
        # Иначе шлем код ошибки
        return {RESPONSE: WRONG_REQUEST, ERROR: 'Не верный запрос'}

def start_server(serv_addr=server_address, serv_port=server_port):
    s = socket(AF_INET,SOCK_STREAM)

    if not isinstance(serv_addr,str) or not isinstance(serv_port,int):
        s.close()
        raise ValueError

    s.bind((serv_addr,serv_port))
    s.listen(1)
    print('Готов к приему клиентов! \n')
    #answer = 'Сервер сообщение получил! Привет клиент!'

    while True:
        client, address = s.accept()
        client_message = json.loads(client.recv(1024).decode("utf-8"))
        print(f'Принято сообщение от клиента: {client_message}')
        answer = check_correct_presence_and_response(client_message)
        print(f"Приветствуем пользователя {client_message.get('user').get('account_name')}!")
        print('Отправка ответа клиенту:',answer)
        client.send(json.dumps(answer).encode('utf-8'))
        client.close

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for i in range(1,len(sys.argv)):
            if sys.argv[i] == '-p' and i+1 < len(sys.argv):
                server_port = sys.argv[i+1]
            if sys.argv[i] == '-a' and i+1 < len(sys.argv):
                server_address = sys.argv[i+1]

#    print(server_address,server_port)
    start_server()