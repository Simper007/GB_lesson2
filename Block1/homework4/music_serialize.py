'''
1. Создать модуль music_serialize.py. В этом модуле определить словарь для вашей любимой музыкальной группы, например:
my_favourite_group = {
‘name’: ‘Г.М.О.’,
‘tracks’: [‘Последний месяц осени’, ‘Шапито’],
‘Albums’: [{‘name’: ‘Делать панк-рок’,‘year’: 2016},
{‘name’: ‘Шапито’,‘year’: 2014}]}

С помощью модулей json и pickle сериализовать данный словарь в json и в байты, вывести результаты в терминал. Записать результаты в файлы group.json, group.pickle соответственно. В файле group.json указать кодировку utf-8.
'''
import json
import pickle

my_favourite_group = {
    'name': 'Daft Punk (Дафт Панк)', 'tracks': [
        'Television Rules the Nation', 'Aerodynamic', 'Instant Crush'], 'Albums': [
            {
                'name': 'Human After All', 'year': 2005}, {
                    'name': 'Discovery', 'year': 2001}, {
                        'name': 'Random Access Memories', 'year': 2013}]}

# pickle
print(pickle.dumps(my_favourite_group))

with open('group.pickle', 'wb') as f1:
    pickle.dump(my_favourite_group, f1)

print('Запись в pickle формате успешна!')

# json

print(json.dumps(my_favourite_group))

with open('group.json', 'w', encoding='utf-8') as f2:
    json.dump(my_favourite_group, f2)

print('Запись в json формате успешна!')
