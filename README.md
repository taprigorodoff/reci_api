API для создания рецептов, меню и списка покупок по меню

## Tech Stack
* Python 3
* PostgreSQL
* Redis

## Установка проекта
`git clone https://github.com/taprigorodoff/reci_api` <br>
`pip install -r requirements.txt` <br> //venv

## Инициализация БД
* создать пустую базу в PostgreSQL
* в файле конфигурации app/config.py заменить значение переменной SQLALCHEMY_DATABASE_URI на 'postgresql://username:password@host:port/database' <br>
* перейти в /app <br>
* выполнить скрипт миграции <br>`flask db upgrade` <br>

## Кэширование
* в файле конфигурации app/config.py заменить значение переменной CACHE_REDIS_URL на 'redis://host:port/database' или 'redis://username:password@host:port/database'

## Запуск
`python3 main.py` <br><br>
Для работы со Swagger перейти по адресу http://127.0.0.1:5000/swagger-ui

## Документация
Документация и схема БД в [Wiki](https://github.com/taprigorodoff/reci_api/wiki)<br>
