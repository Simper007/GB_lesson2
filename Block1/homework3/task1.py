'''
1. Создайте модуль (модуль — программа на Python, т.е. файл с расширением .py).
В нем напишите функцию, создающую директории от dir_1 до dir_9 в папке, из которой запущен данный код.
Затем создайте вторую функцию, удаляющую эти папки.
Проверьте работу функций в этом же модуле.
'''

import os
import shutil

# print(os.getcwd())


def create_dirs():
    for i in range(1, 10):
        os.mkdir(os.path.join(os.getcwd(), 'dir_{}'.format(i)))

    return print('Созданы папки:', os.path.join(os.getcwd(), 'dir_[1-9]'))


def del_dirs():
    for i in range(1, 10):
        os.rmdir(os.path.join(os.getcwd(), 'dir_{}'.format(i)))

    return print('Папки', os.path.join(os.getcwd(), 'dir_[1-9]'), 'удалены')

# create_dirs()
# del_dirs()
