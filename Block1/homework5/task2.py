'''
Решить с помощью генераторов списка.
2. Дан список, заполненный произвольными числами. Получить список из элементов исходного, удовлетворяющих следующим условиям:
1. Элемент кратен 3,
2. Элемент положительный,
3. Элемент не кратен 4.
    Примечание: Список с целыми числами создайте вручную в начале файла. Не забудьте включить туда отрицательные числа. 10-20 чисел в списке вполне достаточно.
'''

number_list = [1, 2, 6, 3, 867, 345, -23, 56, -54, -
               1, 0, 57, 87, 14, -48, -78, 9, -4, -47, -9, 12]

filtred_list = [
    number for number in number_list if number %
    3 == 0 and number > 0 and number %
    4 != 0]

print(filtred_list)
