### Адрес проекта
```
http://51.250.6.114 
http://51.250.6.114/admin/ Админка
```

### Админ:
```
Имя: admin
Фамилия: admin
Имя пользователя: admin
Адрес электронной почты: admin@admin.ru
Пароль: admin
```

### «Продуктовый помощник»

сайт Foodgram - «Продуктовый помощник»
На этом сервисе пользователи смогут

публиковать рецепты
подписываться на публикации других пользователей
добавлять понравившиеся рецепты в список «Избранное»
скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Подготовка и запуск проекта
Клонируем проект 
```
git@github.com:arttronin/foodgram-project-react.git
```
#### Создаем виртуальное окружение
```
python -m venv venv 
```
### Активируем виртуальное окружение
```
source /venv/Scripts/activate 
```
### Команды докера:
```
docker-compose up --build
docker-compose down -v
docker images
docker ps
docker exec -it f5f5ed69e732 bash
docker build -t rishat1991/foodgram_frontend .
docker push rishat1991/foodgram_frontend
```
### Cоздаем .env файл и вписываем данные:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
```

### Технологии:
Python 3.11

Django 3.2

djangorestframework 3.14

nginx

gunicorn

docker-compose

workflow
### Разработчик 
Тронин Артём
# foodgram-project-react
