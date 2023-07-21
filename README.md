#  Проект социальной сети для публикаций, подписок и комментарования записей.

## Стек:
Python 3.9, Django 2.2, SQLite

## Как запустить проект:
Клонировать репозиторий:
```
git clone git@github.com:sntchweb/hw05_final.git
```
Cоздать и активировать виртуальное окружение:
```
py -m venv env
```
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
py -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
py manage.py migrate
```
Запустить проект:
```
py manage.py runserver
```
