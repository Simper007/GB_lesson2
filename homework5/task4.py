'''
4. Написать функцию, которая принимает на вход число от 1 до 100. Если число равно 13, функция поднимает исключительную ситуации ValueError, иначе возвращает введенное число, возведенное в квадрат.
Далее написать основной код программы. Пользователь вводит число. Введенное число передаем параметром в написанную функцию и печатаем результат, который она вернула.
Обработать возможность возникновения исключительной ситуации, которая поднимается внутри функции.
'''

def check_unlucky_number(numb):
    if numb == 13:
        raise ValueError('Не счастливое число 13!')
    if numb not in range(1,101):
        raise Exception('Число не из диапазона [1,100]')
    return numb**2

print('Возведем в квадрат правильные числа')
number = int (input('Введите число от 1 до 100: '))

try:
    print(check_unlucky_number(number))
except ValueError as e:
    print('Вы ввели неверное число')
    print(e)
except Exception as e:
    print('Возникла ошибка')
    print(e)