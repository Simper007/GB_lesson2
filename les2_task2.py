def max_of_3(a, b, c):
    return max(a, b, c)

data=[]
data.append(input('Введите число 1: '))
data.append(input('Введите число 2: '))
data.append(input('Введите число 3: '))

print('Наибольшее из них:', max_of_3(data[0],data[1],data[2]))