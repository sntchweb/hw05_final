#  Проект социальной сети для публикаций, подписок и комментарования записей


## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:sntchweb/hw05_final.git
```
Cоздать и активировать виртуальное окружение:
```
py -m venv env
```
```
source env/bin/activate
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
