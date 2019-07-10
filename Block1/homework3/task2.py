'''
2. Создайте модуль. В нем создайте функцию, которая принимает список и возвращает из него случайный элемент. Если список пустой, функция должна вернуть None. Проверьте работу функций в этом же модуле.
    Примечание: Список для проверки введите вручную. Или возьмите этот: [1, 2, 3, 4]
'''

from random import choice

#testlist = [1,2,3,4]


def random_element(mylist):
    if len(mylist) > 0:
        return choice(mylist)
    return None

# print(len(testlist))
# print(random_element(testlist))
