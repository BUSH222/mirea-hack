# Решение команды MISIS Leaf Lovers на хакатоне "цифровой суверенитет"
> Кейс "Платформа управления доступом к вычислительным ресурсам"

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
