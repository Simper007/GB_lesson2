server_address = '0.0.0.0'
server_port = 7777


ACTION = 'action'
TIME = 'time'
USER = 'user'

ACCOUNT_NAME = 'account_name'
RESPONSE = 'response'
ERROR = 'error'
PRESENCE = 'presence'

BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400
SERVER_ERROR = 500
IMPORTANT_NOTICE = 101 # важное уведомление.
CREATED = 201 # объект создан;
NO_AUTH = 401 # не авторизован;
WRONG_PASSW = 402 # неправильный логин/пароль;
BANNED = 403 #(forbidden) — пользователь заблокирован;
NOT_FOUND = 404 #(not found) — пользователь/чат отсутствует на сервере;
CONFLICT = 409 #(conflict) — уже имеется подключение с указанным логином;
GONE = 410 #(gone) — адресат существует, но недоступен (offline).
INTERNAL_ERROR = 500 # ошибка сервера.
