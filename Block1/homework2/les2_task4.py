# 3: Давайте опишем пару сущностей player и enemy через словарь, который будет иметь ключи и значения:
# name — строка, полученная от пользователя,
# health = 100,
# damage = 50.
#
# Поэкспериментируйте с значениями урона и жизней по желанию.
# Теперь надо создать функцию attack(person1, person2).
# Примечание: имена аргументов можете указать свои.
# Функция в качестве аргумента будет принимать атакующего и атакуемого.
# В теле функция должна получить параметр damage атакующего и отнять это
# количество от health атакуемого. Функция должна сама работать со
# словарями и изменять их значения.

players = {
    'player_health': 100,
    'player_damage': 50,
    'player_armor': 1.2,
    'enemy_health': 150,
    'enemy_damage': 30,
    'enemy_armor': 1.3}
player = input('Введите имя игрока: ')
enemy = input('Введите имя соперника: ')


# print(players)

def real_damage(player):
    if players.get('player_name') == player:
        return round(players.get('player_damage') /
                     players.get('enemy_armor'), 2)
    else:
        return round(players.get('enemy_damage') /
                     players.get('player_armor'), 2)


def attack(player, enemy):
    global players
    if (players.get('player_name') is None) or (
            players.get('enemy_name') is None):
        players.setdefault('player_name', player)
        players.setdefault('enemy_name', enemy)
    if players.get('player_health') > 0 and players.get('enemy_health') > 0:
        if players.get('player_name') == player:
            a = players.get('enemy_health') - \
                real_damage(players.get('player_name'))
            print(
                players.get('player_name'),
                'наносит удар',
                players.get('enemy_name'),
                'силой',
                real_damage(
                    players.get('player_name')))
            print(
                'У',
                players.get('enemy_name'),
                'осталось ',
                round(
                    a,
                    2),
                'здоровья')
            players.pop('enemy_health')
            players.setdefault('enemy_health', round(a, 2))
            if a <= 0:
                print(
                    players.get('player_name'),
                    'победил',
                    players.get('enemy_name'),
                    'в не равном бою!')

        if players.get('player_name') == enemy:
            b = players.get('player_health') - \
                real_damage(players.get('enemy_name'))
            print(
                players.get('enemy_name'),
                'наносит удар',
                players.get('player_name'),
                'силой',
                real_damage(
                    players.get('enemy_name')))
            print(
                'У',
                players.get('player_name'),
                'осталось ',
                round(
                    b,
                    2),
                'здоровья')
            players.pop('player_health')
            players.setdefault('player_health', round(b, 2))
            if b <= 0:
                print(
                    players.get('enemy_name'),
                    'победил',
                    players.get('player_name'),
                    'в не равном бою!')

   # print(players)


print('На арене', player, 'и', enemy)
print('Да начнется битва!')
print(' ')

while players.get('player_health') > 0 and players.get('enemy_health') > 0:
    attack(player, enemy)
    attack(enemy, player)
