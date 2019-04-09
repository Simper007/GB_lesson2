'''
3. Создайте модуль main.py. Из модулей, реализованных в заданиях 1 и 2, сделайте импорт в main.py всех функций. Вызовите каждую функцию в main.py и проверьте, что все работает как надо.
Примечание: Попробуйте импортировать как весь модуль целиком (например из задачи 1), так и отдельные функции из модуля.
'''

import task1
from task2 import random_element
# C точкой не работает, ошибка ModuleNotFoundError: No module named '__main__.task2'; '__main__' is not a package
# хотя расположены в одном пакете homework3


sample = [1, 2, 3, 4, 5, 6, 7]
print(random_element(sample))

task1.create_dirs()
task1.del_dirs()
