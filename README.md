API для создания рецептов, меню и списка покупок по меню
## Запуск с помощью Docker-compose
`docker-compose build` <br>
`docker-compose up`

## Установка 
### Предварительные условия
* Python 3
* PostgreSQL
* Redis

### Установка проекта
`git clone https://github.com/taprigorodoff/reci_api` <br>
`pip install -r requirements.txt` <br> 

### Инициализация БД
* создать пустую базу в PostgreSQL
* в файле settings.ini прописать данные для соединения с БД
* перейти в /app <br>
* выполнить скрипт миграции <br>`flask db upgrade` <br>

### Кэширование
* в файле settings.ini прописать данные для соединения с redis

### Запуск
`python3 main.py` <br>

## Документация
Для работы со Swagger перейти по адресу http://127.0.0.1:5000/swagger-ui <br>
Схема БД в [Wiki](https://github.com/taprigorodoff/reci_api/wiki)<br>
