import logging, os

#Создаем экземпляр логгера
client_log = logging.getLogger('Client_log')
client_log.setLevel(logging.INFO)

#Создаем обработчик
CLIENT_LOG_CONFIG_FOLDER_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
CLIENT_LOG_FILE_PATH = os.path.join(CLIENT_LOG_CONFIG_FOLDER_PATH, 'client.log')
file_hand = logging.FileHandler(CLIENT_LOG_FILE_PATH,encoding='utf-8')
file_hand.setLevel(logging.INFO)
#Определяем формат лога
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s: %(funcName)s - %(message)s ")

#Добавляем формат к обработчику
file_hand.setFormatter(log_format)
#Добавляем обработчик логгеру
client_log.addHandler(file_hand)

if __name__ == '__main__':
    client_log.info('Запуск лога!')
    client_log.warning('Ахтунг!')
    client_log.debug('техно!')
    client_log.error('Типа ожыбка!')
