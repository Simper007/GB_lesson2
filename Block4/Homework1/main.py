'''
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate).
Таблица должна состоять из двух колонок и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2

Unreachable
10.0.0.3
10.0.0.4
'''
import subprocess, re
import ipaddress
from tabulate import tabulate

def host_ping(hosts):
    x = ipaddress.ip_address('0.0.0.0')
    for host in hosts:
        try:
            if type(host) != type(x):
                ip = ipaddress.ip_address(host)
            else:
                ip = host
        except:
            args = ['ping', host, '-n', '1']
        else:
            args = ['ping', str(ip), '-n', '1']

        sub_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
        res = []
        for line in sub_ping.stdout:
            res.append(line.decode('cp866'))
            #print(line.decode('cp866'))

        losses = re.findall('([\d]{1,3})\% потерь',res[6])
        bad_ping_message = re.findall('узел недоступен',res[2])

        if losses[0] == '100' or bad_ping_message:
            print(f'Узел {host} недоступен')
        else:
            print(f'Узел {host} доступен')

def host_range_ping(range):
    subnet = ipaddress.ip_network(range)
    for ip in subnet:
        args = ['ping', str(ip), '-n', '1']
        sub_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
        res = []
        for line in sub_ping.stdout:
            res.append(line.decode('cp866'))

        losses = re.findall('([\d]{1,3})\% потерь', res[6])
        bad_ping_message = re.findall('узел недоступен', res[2])

        if losses[0] == '100' or bad_ping_message:
            print(f'Узел {str(ip)} недоступен')
        else:
            print(f'Узел {str(ip)} доступен')


def host_range_ping_tab(range):
    subnet = ipaddress.ip_network(range)
    ip_status_list = {}
    unreachable = []
    reacheble = []
    for ip in subnet:
        args = ['ping', str(ip), '-n', '1']
        sub_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
        res = []
        for line in sub_ping.stdout:
            res.append(line.decode('cp866'))
            #print(line.decode('cp866'))

        losses = re.findall('([\d]{1,3})\% потерь', res[6])
        bad_ping_message = re.findall('узел недоступен', res[2])
        if losses[0] == '100' or bad_ping_message:
            unreachable.append(str(ip))
        else:
            reacheble.append(str(ip))

    ip_status_list['Доступные узлы'] =  tuple(reacheble)
    ip_status_list['Недоступные узлы'] = tuple(unreachable)
    print(tabulate(ip_status_list, headers='keys'))



if __name__ == '__main__':
    test_ip = ipaddress.ip_address('192.168.1.8')
    check_sites = ['ya.ru','192.168.1.10','192.168.0.3','192.168.1.11']
    check_sites.append(test_ip)
    print('Список узлов для пинга:')
    print(check_sites)
    print()
    host_ping(check_sites)
    print()
    print('Пинг диапазона:')
    host_range_ping('192.168.1.10/31')
    print()
    print('Пинг диапазона с форматированием:')
    print()
    host_range_ping_tab('192.168.1.8/30')

'''
Список узлов для пинга:
['ya.ru', '192.168.1.10', '192.168.0.3', '192.168.1.11', IPv4Address('192.168.1.8')]

Узел ya.ru доступен
Узел 192.168.1.10 доступен
Узел 192.168.0.3 недоступен
Узел 192.168.1.11 недоступен
Узел 192.168.1.8 доступен

Пинг диапазона:
Узел 192.168.1.10 доступен
Узел 192.168.1.11 недоступен

Пинг диапазона с форматированием:

Доступные узлы    Недоступные узлы
----------------  ------------------
192.168.1.8       192.168.1.11
192.168.1.9
192.168.1.10
'''