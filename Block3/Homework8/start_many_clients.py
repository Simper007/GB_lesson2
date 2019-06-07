from subprocess import Popen, CREATE_NEW_CONSOLE
import os, time

process_list = []
user_lists = ['Vanila','Coder','Freeman','xxNAGIBATORxx', 'Skywalker', 'Admin', 'Snegurka','LikeABOSS']
while True:
    user_command = input("Запустить несколько клиентов (s) / Закрыть всех клиентов (x) / Выйти (q) ")

    if user_command == 'q':
        break
    elif user_command == 's':
        process_list.append(Popen(f'python server.py',
                                  creationflags=CREATE_NEW_CONSOLE))
        time.sleep(2)

      #  for user in user_lists[:4]:
      #      process_list.append(Popen(f'python -i client.py localhost 7777 f {user}',
     #                            creationflags=CREATE_NEW_CONSOLE))
            #process_list[-1].communicate('pause')


        for user in user_lists[4:]:
            process_list.append(Popen(f'python -i client.py localhost 7777 f {user}',
                                 creationflags=CREATE_NEW_CONSOLE))
           # process_list[-1].communicate('pause')

        print(' Запущено 4 клиента и сервер')
    elif user_command == 'x':
        for p in process_list:
            p.kill()
        process_list.clear()