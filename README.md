# Решение команды MISIS Leaf Lovers на хакатоне "цифровой суверенитет"
> Кейс "Платформа управления доступом к вычислительным ресурсам"

## Основной функционал программы
- Предоставлять машины пользователям на ограниченное время по запросам
- Отправлять информацию на почту когда машина готова
- Автоматически переустанавливать и менять операционную систему на рабочих нодах
- Управлять пользователями

## Технологии и инструменты
- Flask
- Postgres
- HTML/CSS
- JS
- Docker

## Библиотеки(основные)
- Flask==3.1.0
- Flask_APScheduler==1.13.1
- Flask_Login==0.6.3
- psutil==6.0.0
- psycopg2==2.9.9
- setuptools==75.6.0

## Члены команды
- Второв Фёдор(team lead, fullstack, разработка: бд, эндпоинты, помогал с фронтом)
- Емельянцев Михаил(backend, разработка эндпоинты и в одиночку написал всю работу с серверами)
- Великанов Вадим(frontend, планировка проекта, js, html, css))
- Панов Никита(devops, разработка: бд, docker-compose и эндпоинты)

## Архитектура и структура проекта
![image](https://github.com/user-attachments/assets/9c612820-5beb-44fd-93af-631aa6136bba)

## Заключение
- Это приложение скачиваемое на мастер ноду позволяет управлять ос на рабочих нодах и предоставлять к рабочим нодам доступ по запросу пользователей. Наше решение уникально тем, что использует технологию PXE которая позволяет переустанавливать ос в автоматическом режиме, облегчая работу системного администратора.


## Инструкция по настройке программы
### Настройка почты
- для настройки почты уведомления администратора о новых запросах отредактируйте файл settings.json, туда запишите admin_email
- Для настройки клиента отправки почты поставьте логин и пароль в mail_login и mail_password

## Настройка ноды из основного сервера
В settings.json заполните поля "serverid" (цифра) ip нодой, а "port" - портом на котором нода и мастер сервер разговаривают

## Настройка ноды
- в конфиге ssh нужно задать password auth = yes
- добавить скрипт python в автозагрузку сервера для связи с shell
- PasswordAuthentication поменять значение на yes
- Поставить высший приритет загрузки с pxe в BIOS
- В настройках домена TFTP в BIOS установить локальный айпи адрес pxe сервера запущенного $ sudo python -m pypxe.server и в настройке зеркала установтть домен netbot/[айди ноды]

## Как запустить программу
Способ 1:
1) Запустить докер контейнер
> docker-compose up --build

Способ 2 (тестовый):

1) Установить библиотеки: `pip install -r requirements.txt`
2) В dbloader поменять dynamic_host = 'localhost'
3) Запустить постргес сервер
4) Запустить файл dbloader.py
5) Запустить файл main.py
