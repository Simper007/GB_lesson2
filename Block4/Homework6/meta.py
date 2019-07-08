import dis
import re


class ServerVerifier(type):

    def __init__(self, clsname, bases, clsdict):

        methods = []
        method_attributs = []
        class_attributs = []

        for key, value in clsdict.items():
            #print(key, value)
            if re.search("<function", str(value)):
                # print('func',value)
                instr = dis.get_instructions(value)
                # dis.dis(value)
                for i in instr:
                    # print(i)
                    if i.opname == 'LOAD_GLOBAL' or i.opname == 'LOAD_METHOD':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in method_attributs:
                            method_attributs.append(i.argval)
            elif key != '__module__' and key != '__qualname__':
                #print('class method',key)
                class_attributs.append(key)
        if 'create_presence_meassage' in methods:
            raise('Серверное приложение не должно создавать presence-сообщение!')

        # print(methods)
        # print(method_attributs)
        # print(class_attributs)
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        method_attributs = []
        class_attributs = []

        for key, value in clsdict.items():
            #print(key, value)
            if re.search("<function", str(value)):
                # print('func',value)
                instr = dis.get_instructions(value)
                # dis.dis(value)
                for i in instr:
                    # print(i)
                    if i.opname == 'LOAD_GLOBAL' or i.opname == 'LOAD_METHOD':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in method_attributs:
                            method_attributs.append(i.argval)
            elif key != '__module__' and key != '__qualname__':
                #print('class method',key)
                class_attributs.append(key)

        if 'accept' in methods or 'listen' in methods or 'socket' in methods:
            raise('Клиентское приложение не должно использовать вызов accept или listen!')

        # print(methods)
        # print(method_attributs)
        # print(class_attributs)

        super().__init__(clsname, bases, clsdict)
