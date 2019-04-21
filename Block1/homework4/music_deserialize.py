'''
2: Создать модуль music_deserialize.py. В этом модуле открыть файлы group.json и group.pickle, прочитать из них информацию. Получить объект — словарь из предыдущего задания.
'''

import json,pickle

#pickle
with open('group.pickle', 'rb') as f1:
    my_favourite_group = pickle.load(f1)

print('Прочитали pickle формат, результат:')
print(my_favourite_group)
print(type(my_favourite_group))

print('')

#json
with open('group.json', 'r', encoding='utf-8') as f2:
    my_favourite_group = json.load(f2)

print('Прочитали json формат, результат:')
print(my_favourite_group)
print(type(my_favourite_group))