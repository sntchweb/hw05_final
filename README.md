#  Проект социальной сети.

## Описание проекта:
Проект социальной сети с возможностью публикации статей,комментарования записей, а также с возможностью подписки на понравившегося автора.

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

## Стек:
- Python 3.9
- Django 2.2
- SQLite
