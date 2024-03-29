# Книжный online-магазин

Сайт позволяет ознакомиться с ассортиментом online-магазина, выбрать понравившуюся вам книгу и оформить заказ. Для удобства вы можете воспользоваться поиском по названию книги.

На сайте есть три независимых интерфейса. Первый - публичный. Он предназначен для покупателей и позволяет им просматривать асортимент магазина, добавлять товары в корзину и быстро оформлять заказ. В личном профиле покупатель может отследить все свои заказы, даты оформления и даты доставок, изменение статуса заказов.

Второй интерфейс предназначен для персонала сайта. В нем реализован функционал для менеджеров сайта, позволяющий добавлять, редактировать и удалять товары. Так же персонал может редактировать и удалять при необходимости данные клиентов, контролировать и обновлять статусы размещенных заказов, получать информацию об адресах доставок.

Третий интерфейс - это админ-панель. Преимущественно ей пользуются разработчики при разработке сайта.


## Подготовка к деплою сайта
Скачайте код:
```
git clone https://github.com/Woodwine/BOOKSHOP-BACKEND.git
```
Перейдите в каталог проекта.
Проверьте, что python установлен, комндой:
```
python3 --version
```
**Важно!** Версия python должна быть не ниже 3.6.
В каталоге проекта создайте виртуальное окружение:
```
python3 -m venv env
```
Активируйте его командой:
- MacOS/Linux: `source env/bin/activate`
- Windows: `.\env\Scripts\activate`

Установите зависимости, необходимые для проекта, в вритуальное окружение:
```
pip install -r requirements.txt
```
Создайте файл .env в каталоге YUMMY, добавте в него перечисленые константы, необходимые для корректной работы сайта 
(значения для DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY добавте свои):
```
DEBUG=False
DB_NAME=your_db_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password
SECRET_KEY=django-insecure-^jkhaddg@kyu5679$((319267hj=67gsa
```
Перейдите в каталог yummy_project, откройте файл settings.py и добавте в переменную ALLOWED_HOSTS список строк, представляющих имена хоста / домена, которые будут обслуживать этот сайт, и в переменную CORS_ALLOWED_ORIGINS список источников, которым разрешено отправлять запросы. Для примера:
```
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
```
Соберите все необходимые static-файлы командой:
```
python3 manage.py collectstatic
```
После создания базы данных, параметры которой вы прописали в .env, проведите миграции, для того чтоб в пустой базе данных создались необходимые таблицы и зависимости:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Для создания суперюзера воспользуйтесь командой:
```
python3 manage.py createsuperuser
```
