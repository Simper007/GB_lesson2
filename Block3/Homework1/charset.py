'''
Урок 1. Концепции хранения информации
1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode и также проверить тип и содержимое переменных.
2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на кириллице.
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
'''

#1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание соответствующих переменных.
print('1 задание: в строке')
word_1 = "разработка"
word_2 = "сокет"
word_3 = "декоратор"

print(word_1)
print(type(word_1))
print(word_2)
print(type(word_2))
print(word_3)
print(type(word_3))

#Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode и также проверить тип и содержимое переменных.
print('')
print('1 задание: в юникод символах')
word_u_1 = "\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0" #utf-8
word_u_2 = b'\xd1\x81\xd0\xbe\xd0\xba\xd0\xb5\xd1\x82' #utf-8
word_u_3 = "\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440" #utf-16

print(word_u_1) #ÑÐ°Ð·ÑÐ°Ð±Ð¾ÑÐºÐ°
print(type(word_u_1))
print(word_u_2.decode('utf-8')) #сокет
print(type(word_u_2))
print(word_u_3) #декоратор
print(type(word_u_3))

#2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
print('')
print('2 задание: в байтах')
word_2_1 = b"class"
word_2_2 = b"function"
word_2_3 = b"method"


print(word_2_1)
print(type(word_2_1))
print(len(word_2_1))
print(word_2_2)
print(type(word_2_2))
print(len(word_2_2))
print(word_2_3)
print(type(word_2_3))
print(len(word_2_3))

#3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
print('')
print('3 задание: в байтах')
word_3_1 = b"attribute"
#word_3_2 = b"класс" #bytes can only contain ASCII literal characters. Нельзя, т.к. кириллицы нет в кодировке ASCII
#word_3_3 = b"функция" #bytes can only contain ASCII literal characters. Нельзя, т.к. кириллицы нет в кодировке ASCII
word_3_4 = b"type"
print(word_3_1)
print(word_3_4)

#4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое
print('')
print('4 задание: в байтах')
word_4_1 = "разработка".encode('utf-8')
word_4_2 = "администрирование".encode('utf-8')
word_4_3 = b"protocol"
word_4_4 = b"standard"

print(word_4_1)
print(type(word_4_1))
print(len(word_4_1))
print(word_4_2)
print(type(word_4_2))
print(len(word_4_2))
print(word_4_3)
print(type(word_4_3))
print(len(word_4_3))
print(word_4_4)
print(type(word_4_4))
print(len(word_4_4))

#и выполнить обратное преобразование (используя методы encode и decode).
word_4_1 = word_4_1.decode('utf-8')
word_4_2 = word_4_2.decode('utf-8')

print('')
print('4 задание: в строке')
print(word_4_1)
print(type(word_4_1))
print(len(word_4_1))
print(word_4_2)
print(type(word_4_2))
print(len(word_4_2))

#5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на кириллице.
print('')
print('5 задание:')
import subprocess

args = ['ping', 'yandex.ru']
sub_ping = subprocess.Popen (args, stdout=subprocess.PIPE)

for line in sub_ping.stdout:
    print(line.decode('cp866'))

args[1] = 'youtube.com'

sub_ping = subprocess.Popen (args, stdout=subprocess.PIPE)

for line in sub_ping.stdout:
    print(line.decode('cp866'))

#6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
print('')
print('6 задание:')

with open('test_file.txt', 'w') as f:
     f.writelines('сетевое программирование\n')
     f.writelines(f'{word_2}\n')
     f.writelines(f'{word_3}\n')

#Проверить кодировку файла по умолчанию.
import locale
print('')
def_codepage = locale.getpreferredencoding() #предпочтительная кодировка
                                             #или
def_codepage = locale.getdefaultlocale()[1]  #кодировка из локали по-умолчанию

print('По умолчанию:', def_codepage)
print('')

print('6 задание: читаем в кодировке по умолчанию')
with open('test_file.txt', 'r', encoding=def_codepage) as f:
    text = f.read()
    print(text)

'''
сетевое программирование
сокет
декоратор   
'''

#Принудительно открыть файл в формате Unicode и вывести его содержимое.
print('6 задание: читаем принудительно в кодировке utf-8')
with open('test_file.txt', 'r', encoding='utf-8',errors='replace') as f:
#'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte. Просто так принудительно не открывается из-за несоответсвия кодировке. Заменяем нераспознаное на знаки вопросов
    text = f.read()
    print(text)

'''
������� ����������������
�����
���������
'''