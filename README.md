### http://127.0.0.1:8000/admin/

User: buchik

Password: buchik#1

### «Продуктовый помощник»

API проекта сайт Foodgram. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

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
### Устанавливаем docker и docker-compose:
```
sudo apt install docker.io
sudo apt install docker-compose
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
