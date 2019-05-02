'''
1. Написать функцию получения IATA-кода города из его названия, используя API Aviasales.
'''

import requests,json

def get_IATA_by_city(city):
    get_link = 'https://www.travelpayouts.com/widgets_suggest_params?q=Из%20'+city+'%20в%20Москву'
    IATA = json.loads(requests.get(get_link).text)
    if (IATA.get('origin')) == None:
        return 'Город не найден!'
    return IATA['origin']['iata']

city = input('Для получения кода IATA введите название города: ')

print('IATA код для города:', get_IATA_by_city(city))
