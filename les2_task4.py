# 3: Давайте опишем пару сущностей player и enemy через словарь, который будет иметь ключи и значения:
# name — строка, полученная от пользователя,
# health = 100,
# damage = 50.
#
# Поэкспериментируйте с значениями урона и жизней по желанию.
# Теперь надо создать функцию attack(person1, person2).
# Примечание: имена аргументов можете указать свои.
# Функция в качестве аргумента будет принимать атакующего и атакуемого.
# В теле функция должна получить параметр damage атакующего и отнять это количество от health атакуемого. Функция должна сама работать со словарями и изменять их значения.

players = {'player_health':100,'player_damage':50,'player_armor':1.2,'enemy_health':150,'enemy_damage':30,'enemy_armor':1.3}
player = input('Введите имя игрока: ')
enemy = input('Введите имя соперника: ')


print(players)

def attack(player, enemy):
    global players
    if (players.get('player_name') == None) or (players.get('enemy_name') == None):
        players.setdefault('player_name', player)
        players.setdefault('enemy_name', enemy)
    if players.get('player_health') > 0 and players.get('enemy_health') > 0:
        if players.get('player_name')== player:
            a = players.get('enemy_health') - players.get('player_damage')
            print(players.get('player_name'),'наносит удар',players.get('enemy_name'), 'силой', players.get('player_damage') )
            print('У', players.get('enemy_name'), 'осталось ', a, 'здоровья')
            players.pop('enemy_health')
            players.setdefault('enemy_health', a)
            if a <= 0:
                print(players.get('player_name'),'победил',players.get('enemy_name'), 'в не равном бою!')

        if players.get('player_name')== enemy:
            b = players.get('player_health') - players.get('enemy_damage')
            print(players.get('enemy_name'), 'наносит удар', players.get('player_name'), 'силой', players.get('enemy_damage'))
            print('У', players.get('player_name'), 'осталось ', b, 'здоровья')
            players.pop('player_health')
            players.setdefault('player_health', b)
            if b <= 0:
                print(players.get('enemy_name'),'победил',players.get('player_name'), 'в не равном бою!')

   # print(players)

print('На арене',players.get('player_name'),'и',players.get('enemy_name'))
print('Да начнется битва!')
print(' ')

while players.get('player_health') > 0 and players.get('enemy_health') > 0:
    attack(player, enemy)
    attack(enemy, player)