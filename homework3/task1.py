'''
1. Создайте модуль (модуль — программа на Python, т.е. файл с расширением .py).
В нем напишите функцию, создающую директории от dir_1 до dir_9 в папке, из которой запущен данный код.
Затем создайте вторую функцию, удаляющую эти папки.
Проверьте работу функций в этом же модуле.
'''

import os

#print(os.getcwd())

def create_dirs():
    for i in range(1, 10):
        os.mkdir(os.path.join(os.getcwd(),'dir_{}'.format(i)))
        print('Создана папка:', os.path.join(os.getcwd(),'dir_{}'.format(i)))


def del_dirs():
    for i in range(1, 10):
        os.rmdir(os.path.join(os.getcwd(),'dir_{}'.format(i)))
        print('Папка', os.path.join(os.getcwd(), 'dir_{}'.format(i)), 'удалена')


#create_dirs()
#del_dirs()