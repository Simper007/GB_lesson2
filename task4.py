# 1. Даны два произвольных списка. Удалите из первого списка элементы, присутствующие во втором.

my_list_1 = [2, 5, 8, 2, 12, 12, 2, 7, 4, 11, 56]
my_list_2 = [2, 7, 12, 3, 4]

for elem2 in my_list_2:
    for elem1 in my_list_1:
        if elem2 in my_list_1:
            my_list_1.remove(elem2)

print(my_list_1)

