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



## Как запустить программу
Способ 1:
1) Запустить докер контейнер
Способ 2 (тестовый):
1) Запустить постргес сервер
2) Запустить файл dbloader.py
3) Запустить файл main.py
