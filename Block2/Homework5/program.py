'''
1. Создайте классы Noun и Verb.
2. Настройте наследование от Word.
3. Добавьте защищенное свойство «Грамматические характеристики».
4. Перестройте работу метода show класса Sentence.
5. Перестройте работу метода show_part класса Sentence, чтобы он показывал грамматические характеристики.
'''
from Block2.Homework4.main import *

class Noun(Word):
    _grammatical_characteristics = 'сложное'

    def __init__(self, text=False):
        self.part_of_speech = 'существительное'
        if text:
            self.text = text

class Verb(Word):
    _grammatical_characteristics = 'простой'

    def __init__(self, text=False):
        self.part_of_speech = 'глагол'
        if text:
            self.text = text


if __name__ == '__main__':

    our = Word('Нам','местоимение')
    its_time = Noun('пора')
    eat = Verb('есть')
    bread = Noun('хлеб')
    tasty = Word('вкусный')
    znak = Word('!','знак препинания')

    word_list = [eat,bread,its_time,our,znak,tasty]

    #print(eat.text,eat.part_of_speech,eat._grammatical_characteristics)
    #print(bread.text,bread.part_of_speech)

    about_food = Sentence(word_list)
    about_food.show() #Нам хлеб пора есть!
    about_food.show_parts() #['местоимение', ('существительное', 'сложное'), ('существительное', 'сложное'), ('глагол', 'простой'), 'знак препинания']
    #print(about_food.content) #[('Нам', (1, 'местоимение')), ('хлеб', (3, 'существительное', 'сложное')), ('пора', (3, 'существительное', 'сложное')), ('есть', (4, 'глагол', 'простой'))]