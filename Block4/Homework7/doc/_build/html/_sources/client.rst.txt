Client module
=================================================

Клиентское приложение для обмена сообщениями. Поддерживает
отправку сообщений пользователям которые находятся в сети.

.. image:: _static/Client.png

Поддерживает аргументы коммандной строки:

``python client.py {имя сервера} {порт} {имя пользователя} {пароль}``

1. {имя сервера} - адрес сервера сообщений.
2. {порт} - порт по которому принимаются подключения
3. {имя пользователя} - имя пользователя с которым произойдёт вход в систему.
4. {пароль} - пароль пользователя.

Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

Примеры использования:

* ``python client.py``

*Запуск приложения с параметрами по умолчанию.*

* ``python client.py 127.0.0.1 7777``

*Запуск приложения с указанием подключаться к серверу по адресу 127.0.0.1:7777*

* ``python 127.0.0.1 7777 Simper 123``

*Запуск приложения с пользователем Simper и паролем 123 и указанием подключаться к серверу по адресу 127.0.0.1:7777*


client.py
~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал клиентского приложения.

	
.. autoclass:: client.Client
	:members:
	
.. autoclass:: client.m_window
	:members:
	
.. autoclass:: client.c_window
	:members:


client_database.py
~~~~~~~~~~~~~~~~~~

.. autoclass:: client_database.Chat_histories
	:members:
	
.. autoclass:: client_database.User_contact_list
	:members:
	
.. autoclass:: client_database.Last_user
	:members:
	

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: main_window.Ui_MainWindow
	:members:
	
client_gui_settings.py
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client_gui_settings.Ui_Form
	:members:

.. autoclass:: client_gui_settings.AddContactDialog
	:members:

.. autoclass:: client_gui_settings.DelContactDialog
	:members:


	