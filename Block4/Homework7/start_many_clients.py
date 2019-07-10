from subprocess import Popen, CREATE_NEW_CONSOLE
import os
import time

process_list = []
user_lists = [
    ('Vanila',
     'Sky'),
    ('Coder',
     'redoC'),
    ('xxNAGIBATORxx',
     '2011'),
    ('Skywalker',
     'Luke'),
    ('Simper',
     '123'),
    ('Freeman',
     'Half-Life 3'),
    ('Admin',
     'qwerty'),
    ('Snegurka',
     'snowman'),
    ('LikeABOSS',
     'BB')]
while True:
    user_command = input(
        "Запустить несколько клиентов (s) / Закрыть всех клиентов (x) / Выйти (q) ")

    if user_command == 'q':
        break
    elif user_command == 's':
        process_list.append(Popen(f'python server.py -a 0.0.0.0 -p 7777',
                                  creationflags=CREATE_NEW_CONSOLE))
        time.sleep(2)
        '''
        #только чтение
        for user,pwd in user_lists[:2]:
            process_list.append(Popen(f'python -i client.py localhost 7777 {user} {pwd} r',
                                 creationflags=CREATE_NEW_CONSOLE))
            #process_list[-1].communicate('pause')

        #только запись
        for user in user_lists[2:4]:
            process_list.append(Popen(f'python -i client.py localhost 7777 {user} w',
                                 creationflags=CREATE_NEW_CONSOLE))
            #process_list[-1].communicate('pause')
        '''
        # полный клиент
        for user, pwd in user_lists[4:]:
            print(user, pwd)
            process_list.append(
                Popen(
                    f'python client.py localhost 7777 {user} {pwd} gui',
                    creationflags=CREATE_NEW_CONSOLE))

        print(' Запущено 5 клиентов с gui и сервер')
    elif user_command == 'x':
        for p in process_list:
            p.kill()
        process_list.clear()
