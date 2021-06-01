API для создания рецептов, меню и списка покупок по меню

## Tech Stack
* flask
* flask RESTful
* PostgreSQL
* Redis

## Установка
`git clone https://github.com/taprigorodoff/reci_api` <br>
`pip install -r requirements.txt` <br>

## Инициализация БД
* создать пустую базу в PostgreSQL
* в app/config.py заменить значение переменной SQLALCHEMY_DATABASE_URI на <u>'postgresql://username:password@host:port/database'</u> <br>
* перейти в директорию проекта <br>
* выполнить скрипт миграции <br>`flask db upgrade` <br>

## Запуск
`python3 main.py` <br>
Для работы со Swagger перейти по адресу http://127.0.0.1:5000/swagger-ui

## Документация
Документация и схема БД в [Wiki](https://github.com/taprigorodoff/reci_api/wiki)<br>
