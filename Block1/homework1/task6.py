# 3. Дан список заполненный произвольными целыми числами.
# Получите новый список, элементами которого будут только уникальные элементы исходного.
#     Примечание. Списки создайте вручную, например так:
# my_list_1 = [2, 2, 5, 12, 8, 2, 12, 5]
#
# В этом случае ответ будет:
# [5, 8]

my_list_1 = [2, 2, 5, 12, 8, 2, 12]
my_list_2 = []
count = 0
i = 0
k = 0
for k in range(len(my_list_1)):
    for i in range(len(my_list_1)):
        if my_list_1[k] == my_list_1[i]:
            count += 1
            if count > 1:
                count = 0
                break
        i += 1
    if count == 1:
        my_list_2.append(my_list_1[k])
    count = 0

print('Список: ', my_list_1)
print('Уникальные элементы: ', my_list_2)

