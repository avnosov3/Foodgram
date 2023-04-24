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
git@github.com:avnosov3/foodgram.git
```
2. Перейти в папку с проектом
```
cd infra
```
3. Запустить docker-compose
```
docker-compose up -d --build
```
4. Применить миграции
```
docker-compose exec web python manage.py migrate
```
5. Создать супер-юзера
```
docker-compose exec web python manage.py createsuperuser
```
6. Собрать статику
```
docker-compose exec web python manage.py collectstatic --no-input
```
7. Заполнить БД
```
docker-compose exec web python manage.py loadjson
```

## Автор
* [Носов Артём](https://github.com/avnosov3)
