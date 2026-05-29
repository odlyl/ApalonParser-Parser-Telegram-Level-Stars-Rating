# Parser Telegram Level Stars Rating

Скрипт для поиска пользователей в Telegram-чате по уровню Stars. Если пользователь подходит под фильтры, бот отправляет администратору карточку с профилем и кнопками.

Контакт автора: [@odlyl](https://t.me/odlyl)

## Возможности

- Поиск пользователей в выбранном Telegram-чате.
- Фильтр по минимальному и максимальному уровню Stars.
- Фильтр пользователей с платными сообщениями.
- Фильтр пользователей, которым можно писать только с Telegram Premium.
- Отправка найденных пользователей администратору через Telegram-бота.
- Кнопка для открытия чата с готовым первым сообщением.
- Кнопка удаления карточки найденного пользователя.
- База `users.db`, чтобы один и тот же пользователь не отправлялся повторно.

## Требования

- Python 3.10 или новее.
- Telegram-аккаунт для userbot-сессии.
- Telegram-бот из [@BotFather](https://t.me/BotFather).
- `API_ID` и `API_HASH` с сайта [my.telegram.org](https://my.telegram.org).
- Доступ к чату, который нужно проверять.
- Библиотеки из `requirements.txt`.

## Безопасность

Не публикуй реальные данные:

- `API_ID`
- `API_HASH`
- `BOT_TOKEN`
- `ADMIN_ID`
- `config/local.py`
- `userbot_session.session`
- `users.db`

Файл `config/local.py` добавлен в `.gitignore`, поэтому он нужен только локально и не должен попадать на GitHub.

## Установка

```bash
git clone https://github.com/your-username/telegram-stars-user-parser.git
cd telegram-stars-user-parser
pip install -r requirements.txt
```

Если `pip` не работает:

```bash
py -m pip install -r requirements.txt
```

## Настройка

Скопируй пример конфига:

```bash
copy config\example.py config\local.py
```

Открой `config/local.py` и заполни свои данные:

```python
API_ID = 123456
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
ADMIN_ID = 123456789
TARGET_CHAT = "https://t.me/example_chat"
```

Фильтр по уровню Stars:

```python
MIN_STARS_LEVEL = 3
MAX_STARS_LEVEL = None
```

`MAX_STARS_LEVEL = None` означает, что верхней границы нет. Если нужно искать только от 3 до 10 уровня:

```python
MIN_STARS_LEVEL = 3
MAX_STARS_LEVEL = 10
```

Фильтр платных сообщений:

```python
SEND_USERS_WITH_PAID_MESSAGES = True
```

- `True` - отправлять пользователей с платными сообщениями.
- `False` - пропускать пользователей с платными сообщениями.

Фильтр ограничения “писать могут только Premium”:

```python
SEND_USERS_WHO_REQUIRE_PREMIUM_TO_CONTACT = True
```

- `True` - отправлять таких пользователей.
- `False` - пропускать таких пользователей.

Кнопка с готовым первым сообщением:

```python
SHOW_FIRST_MESSAGE_BUTTON = True
FIRST_MESSAGE_BUTTON_TEXT = "💬 Написать пользователю"
FIRST_MESSAGE_TEXT = "Привет! Хотел с тобой связаться."
```

Кнопка работает только если у найденного пользователя есть публичный `username`.

## Запуск

```bash
python main.py
```

Если `python` не работает:

```bash
py main.py
```

При первом запуске Telethon может попросить номер телефона, код из Telegram и облачный пароль. Это нужно для создания userbot-сессии.

## Как работает скрипт

1. Подключается к Telegram через Telethon.
2. Открывает чат из `TARGET_CHAT`.
3. Проверяет участников чата.
4. Пропускает ботов.
5. Получает уровень Stars и дополнительные параметры пользователя.
6. Сравнивает пользователя с фильтрами из `config/local.py`.
7. Проверяет `users.db`.
8. Если пользователь уже есть в базе по ID или username, он не отправляется повторно.
9. Если пользователь новый и подходит под фильтры, бот отправляет карточку администратору.
10. После проверки бот остается включенным, чтобы работали кнопки под карточками.

## Частые проблемы

### Бот ничего не присылает

Проверь, что ты написал боту `/start`, правильно указал `BOT_TOKEN` и `ADMIN_ID`, а userbot-аккаунт имеет доступ к `TARGET_CHAT`.

### FLOOD WAIT

Telegram временно ограничил запросы. Скрипт подождет нужное время и продолжит работу.

### Нет кнопки “Написать пользователю”

Скорее всего, у найденного пользователя нет публичного `username`. Telegram не позволяет открыть чат с готовым текстом без username.

## Автор

Telegram: [@odlyl](https://t.me/odlyl)
