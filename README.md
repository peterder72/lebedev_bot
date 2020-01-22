# Лебедев Бот

## Описание

Простой бот, который делает картинки с Лебедевым по шаблону. Использует [API основы](https://cmtt-ru.github.io/osnova-api/swagger.html)

![Пример картинки](img/meme.png)

Программа работает на Python 3.6+ с использованием *Pillow* для создания картинки и *requests* для API. Во время работы обращается к API Основы и Imgur

## Установка

Для запуска скрипта сначала необходимо установить необходимые библиотеки:

```bash

python3 -m pip install -r requirements.txt

```

Также, для авторизации необходимы токены Основы и Imgur. Они должны находиться в файле *auth.env* (исключен из системы контроля версий). Формат файла указан ниже.

```bash

TJ_TOKEN=XXXXXXX
IMGUR_CLIENT=XXXXXX

```

И запускаете *lebedev.py*. Всё.

Во время первого запуска скрипт создаст файл конфигурации, чтобы не заспамить *все* прошлые комментарии, где вас упоминали.

## Принцип работы

Скрипт каждые 10 секунд проверяет все упоминания себя через систему уведомлений TJ. Из-за того, что система прочтения уведомлений работает нестабильно (*вообще не работает*), скрипт создает файл *config.json*, где хранит ID последнего прочитанного уведомления. Во время первого запуска бот пропускает все упоминания, так как API Основы может вернуть *все* упоминания с самого создания аккаунта (или введения упоминаний, смотря что было раньше).

Функция получения уведомлений возвращает список упоминаний, с которыми уже можно работать. Скрипт создает картинку с помощью *PIL* в файле *mememaker.py*, и загружает ее на *Imgur* с анонимным токеном. API Основы отказалось принимать картинки через */uploader/upload* и постоянно возвращало 400, из-за чего и был вставлен этот костыль.

## Еще в разработке

- Аргументы командной строки
- Более гибкая регулярка
- Еще больше обработки ошибок
- Подчистка кода класса Бота