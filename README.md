# [foodgram](https://foodgram.servebeer.com/recipes/)

На этом [сервисе](https://foodgram.servebeer.com/recipes/) пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Техно-стек
* python 3.7.9
* django 2.2.16
* drf 3.12.4
* drf-simlejwt 4.7.2
* gunicorn 20.0.4
* postgres 13.0
* nginx 1.21.3
* docker 20.10.16
* docker-compose 3.8

## Запуск проекта

1. Клонировать репозиторий
```
git@github.com:avnosov3/Foodgram.git
```
2. Перейти в папку с проектом
```
cd Foodgram
```
3. Создать файл .env в папке infra
```
cd infra
```
```
SECRET_KEY=<Указать секретный ключ>
DEBUG=True (если запуск в боевом режиме, то необходимо удалить пермеенную)
HOST=<Указать хост>

DB_ENGINE=django.db.backends.postgresql
DB_NAME=<Указать название БД>
POSTGRES_USER=<Указать имя пользователя>
POSTGRES_PASSWORD=<Указать пароль пользователя>
DB_HOST=127.0.0.1
DB_PORT=<Указать порт для подключения к базе>
``` 
4. Подключить ssl по [инструкции](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)
5. Запустить docker-compose
```
docker-compose up -d --build
```
6. Применить миграции
```
docker-compose exec web python manage.py migrate
```
7. Создать супер-юзера
```
docker-compose exec web python manage.py createsuperuser
```
8. Собрать статику
```
docker-compose exec web python manage.py collectstatic --no-input
```
9. Заполнить БД
```
docker-compose exec web python manage.py loadjson
```

## Автор
* [Носов Артём](https://github.com/avnosov3)
