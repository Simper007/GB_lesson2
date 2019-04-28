'''
1. Получить количество учеников с сайта geekbrains.ru:
a) при помощи регулярных выражений,
b) при помощи библиотеки BeautifulSoup.
'''

import bs4, re

with open('index.html', 'r',encoding='utf-8') as f:
    html_source = f.read()


users = re.compile('total-users">[а-яА-Я\s]+([0-9 ]+)[а-яА-Я\s]+</span')
#users = re.compile('total-users">.*?</span')

print('Количество учеников: {}'.format(re.sub(" ","",users.findall(html_source)[0])))

s = bs4.BeautifulSoup(html_source,'html.parser');

span_list = s.find_all('span',class_='total-users')
#span_list = s('span',class_='total-users')

print('Текст кол-ва через BeautifulSoup:', [t.text for t in span_list][0])

#print(s.span.string)