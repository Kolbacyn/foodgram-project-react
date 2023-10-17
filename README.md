# Дипломный проект студента Яндекс.Практикума.

# Описание проекта.

Проект представляет собой микроблог.
Реализована возможность регистрации, размещения своих и просмотра чужих публикаций.
Также можно комментировать публикации и подписываться на любимых авторов.
API доступен только аутентифицированным пользователям. Реализованы возможность поиска и фильтрации по тегам.

## Технологии:

- Python 3.9
- Django 3.2.3
- Django REST framework 3.12.4
- React

## Запуск проекта из образов с DockerHub

Для запуска необходимо на создать папку проекта `foodgram` и перейти в нее:

```bash
mkdir foodgram
cd foodgram
```

В папку проекта скопируйте файл `docker-compose.production.yml` и запустите его:

```bash
sudo docker compose -f docker-compose.production.yml up
```

Немного волшебства....

## Запуск проекта из исходников GitHub

Клонируем себе репозиторий: 

```bash 
git clone git@github.com:Kolbacyn/foodgram-project-react.git
```

Выполняем запуск:

```bash
sudo docker compose -f docker-compose.yml up
```

## После запуска: Миграции, сбор статистики

После запуска необходимо выполнить сбор статистики и миграции бэкенда. Статистика фронтенда собирается во время запуска контейнера, после чего он останавливается. 

```bash
sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py migrate

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend python manage.py collectstatic

sudo docker compose -f [имя-файла-docker-compose.yml] exec backend cp -r /app/collected_static/. /static/static/
```

И далее проект доступен на: 

```
http://localhost:8100/
```

## Остановка оркестра контейнеров

В окне, где был запуск **Ctrl+С** или в другом окне:

```bash
sudo docker compose -f docker-compose.yml down
```

## Разработчик

Зольников Юрий

<<<<<<< HEAD
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
=======
[![.github/workflows/main.yml](https://github.com/Kolbacyn/kittygram_final/actions/workflows/main.yml/badge.svg)](https://github.com/kolbacyn/kittygram_final/actions/workflows/main.yml)

![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

>>>>>>> 2e75b00cb6925b074465a291cce0e2389bc30be0
