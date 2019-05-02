'''
1. Создайте класс Word.
2. Добавьте свойства text и part of speech.
3. Добавьте возможность создавать объект слово со значениями в скобках.
4. Создайте класс Sentence
5. Добавьте свойство content, равное списку, состоящему из номеров слов, входящих в предложение.
6. Добавьте метод show, составляющий предложение.
7. Добавьте метод show_parts, отображающий, какие части речи входят в предложение.
'''

#1. Создайте класс Word.
class Word:
    #2. Добавьте свойства text и part of speech.
    text = "default" #слово
    part_of_speech = "существительное" #часть речи

    def __init__(self,text="default",part_of_speech="существительное"): #3. Добавьте возможность создавать объект слово со значениями в скобках.
            self.text = text
            self.part_of_speech = part_of_speech

    def show_the_word(self):
        print(self.text)

#4. Создайте класс Sentence
class Sentence:
    content = [] #5. Добавьте свойство content, равное списку, состоящему из номеров слов, входящих в предложение
    word_order = {'местоимение':1,'прилагательное':2,'существительное':3,'глагол':4,'наречие':5} #порядок вывода слов согласно части речи

    def __init__(self,content=[]):
        ordered_words = {}

        for f in content:
            ordered_words[f.text]=self.word_order.get(f.part_of_speech),f.part_of_speech       #проставление порядка вывода каждому слову

       # print(ordered_words)
        self.content = list(ordered_words.items())
       # print(self.content)
        self.content.sort(key=lambda i: i[1])    #сортировка согласно порядку частей речи в предложении
       # print(self.content)


    def show(self): #6. Добавьте метод show, составляющий предложение.
        sent = ''
        for f in self.content:
            sent = sent+' '+f[0]
        print(f'{sent}')

    def show_parts(self): #7. Добавьте метод show_parts, отображающий, какие части речи входят в предложение.
        list_of_parts = []

        for parts in self.content:
            list_of_parts.append(parts[1][1])

        print(f'{list_of_parts}')


if __name__ == '__main__':
    our = Word('Наше','местоимение')
    sun = Word('солнце', 'существительное')
    shining = Word('светит','глагол')
    red = Word('красное','прилагательное')
    brightly = Word('ярко','наречие')
    fine = Word('красивое','прилагательное')

    word_list = [shining,red,sun,brightly,our,fine]

    #print(word_list)

    about_sun = Sentence(word_list)
    about_sun.show() # Наше красное красивое солнце светит ярко
    about_sun.show_parts() #['местоимение', 'прилагательное', 'прилагательное', 'существительное', 'глагол', 'наречие']
    #print(about_sun.content)
