'''
1. Получите текст из файла.
2. Разбейте текст на предложения.
3. Найдите самую используемую форму слова, состоящую из 4 букв и более, на русском языке.
4. Отберите все ссылки.
5. Ссылки на страницы какого домена встречаются чаще всего?
6. Замените все ссылки на текст «Ссылка отобразится после регистрации».
'''
import os, re

#1. Получите текст из файла
with open('text.txt', 'r',encoding='utf-8') as f:
    text_from_file = f.read()

print('Исходный текст:')
print(text_from_file)


#2. Разбейте текст на предложения
print('')
print('Разбивка по предложениям:')
sentences = [re.sub("(^[\s\.]?|[\s\.]?$)","",sentence) for sentence in re.split("\.\s+",text_from_file)] #разбиваем на предложения и удаляем лишние пробелы в начале предложений, точки в последнем предложении
print(sentences)


#3. Найдите самую используемую форму слова, состоящую из 4 букв и более, на русском языке.
tmp = re.findall('[А-Яа-я]{4,}',text_from_file) #ищем все слова с кирилицей более 4 символов
#print(tmp)
tmp = { text1 : tmp.count(text1) for text1 in tmp} #считаем частоту употребления слова
#print(tmp)
print('Cамое распространненное слово: "{}"'.format(sorted(tmp.items(),key=lambda item:item[1],reverse=True)[0][0])) #самое распространненное слово

#import collections
#print('Cамое распространненное слово:', '"{}"'.format(collections.Counter(re.findall('[А-Яа-я]{4,}',text_from_file)).most_common()[0][0]))


#4. Отберите все ссылки
link_pattern = re.compile("\s([a-zа-я\d\-\.]+\.[a-zа-я]{2,6}/?[\w\d\-/]*)")
links = link_pattern.findall(text_from_file)
print('')
print('Список ссылок:', links)

#5. Ссылки на страницы какого домена встречаются чаще всего?
domains = [re.findall('([a-zа-я\d\-]+\.[\w]{2,6})/?[\w\d\-/]*$',domain)[0] for domain in links]
#print(domains)
print('')
print( 'Самый популярный домен: "{}"'.format(sorted({domain : domains.count(domain) for domain in domains}.items(),key=lambda item:item[1],reverse=True)[0][0]))

#6. Замените все ссылки на текст «Ссылка отобразится после регистрации».
print('')
print(link_pattern.sub("«Ссылка отобразится после регистрации»",text_from_file))