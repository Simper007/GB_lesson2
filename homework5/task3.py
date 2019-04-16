'''
Решить с помощью генераторов списка.
3. Напишите функцию, которая принимает на вход список. Функция создает из этого списка новый список из квадратных корней чисел (если число положительное) и самих чисел (если число отрицательное) и
возвращает результат (желательно применить генератор и тернарный оператор при необходимости). В результате работы функции исходный список не должен измениться.
Например:
old_list = [1, -3, 4]
result = [1, -3, 2]
Примечание: Список с целыми числами создайте вручную в начале файла. Не забудьте включить туда отрицательные числа. 10-20 чисел в списке вполне достаточно.
'''
import copy, math

old_list = [1, -3, 4]

number_list = [1,2,6,3,144,345,-23,56,-54,-1,0,57,87,14,-48,-78,9,-4,-47,-9, 12]

def sqrt_for_positive(num_list):
     a = copy.deepcopy(num_list)
     a = [int(round(math.sqrt(number),0)) if number>0 else number for number in num_list] #округление до целого, чтобы выводилось как в примере - целые числа
     return a

print(sqrt_for_positive(number_list))

print(sqrt_for_positive(old_list))