# [foodgram](https://foodgram.servebeer.com/recipes/)

<details><summary>Russian language</summary>  

На этом [сервисе](https://foodgram.servebeer.com/recipes/) пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. [Документация API](https://foodgram.servebeer.com/api/docs/)

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
git clone git@github.com:avnosov3/Foodgram.git
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

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=<Указать имя пользователя>
POSTGRES_PASSWORD=<Указать пароль пользователя>
DB_HOST=db
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
10. Создать в админке теги

## Автор
* [Носов Артём](https://github.com/avnosov3)
</details>

<details><summary>English language</summary>  

On this [service](https://foodgram.servebeer.com/recipes/), users can post recipes, subscribe to other posts, add favorite recipes to their Favorites list, and download a summary of the products they need before going to the store. to prepare one or more selected dishes. [API Documentation](https://foodgram.servebeer.com/api/docs/)

## Stack
* python 3.7.9
* django 2.2.16
* drf 3.12.4
* drf-simlejwt 4.7.2
* gunicorn 20.0.4
* postgres 13.0
* nginx 1.21.3
* docker 20.10.16
* docker-compose 3.8

## Launch of the project

1. Clone repository
```
git clone git@github.com:avnosov3/Foodgram.git
```
2. Go to the project folder
```
cd Foodgram
```
3. Create .env file in infra folder
```
cd infra
```
```
SECRET_KEY=<Specify secret key>
DEBUG=True (if the launch is in prod mode, then you need to delete the variable)

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=<Specify username>
POSTGRES_PASSWORD=<Specify password>
DB_HOST=db
DB_PORT=<Specify the port to connect to the database>
``` 
4. Connect ssl according to [instructions](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)
5. Run docker-compose
```
docker-compose up -d --build
```
6. Apply migrations
```
docker-compose exec web python manage.py migrate
```
7. Create super user
```
docker-compose exec web python manage.py createsuperuser
```
8. Collect static
```
docker-compose exec web python manage.py collectstatic --no-input
```
9. Fill in the database
```
docker-compose exec web python manage.py loadjson
```
10. Create tags in admin panel

## Author
* [Artem Nosov](https://github.com/avnosov3)
