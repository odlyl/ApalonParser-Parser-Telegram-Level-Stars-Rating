# Данные Telegram API.
# Их нужно получить на сайте https://my.telegram.org
API_ID = 123456
API_HASH = "your_api_hash"

# Токен бота из @BotFather и твой числовой Telegram ID.
# Именно сюда бот будет отправлять найденных пользователей.
BOT_TOKEN = "your_bot_token"
ADMIN_ID = 123456789

# Сессия userbot-аккаунта и чат, где нужно искать пользователей.
SESSION_NAME = "userbot_session"  # Не менять
TARGET_CHAT = "https://t.me/url_chat"

# Файлы проекта.
DB_NAME = "users.db"  # Не менять
PHOTO_PATH = "newuser.png"  # Не менять

# Фильтр по уровню.
# Если максимальный уровень не нужен, оставь None.
MIN_STARS_LEVEL = 3
MAX_STARS_LEVEL = None

# Отправлять ли пользователей, у которых включены платные сообщения.
# True = отправлять таких пользователей.
# False = пропускать таких пользователей.
SEND_USERS_WITH_PAID_MESSAGES = True

# Отправлять ли пользователей, которым можно написать только с Telegram Premium.
# True = отправлять таких пользователей.
# False = пропускать таких пользователей.
SEND_USERS_WHO_REQUIRE_PREMIUM_TO_CONTACT = True

# Ответ простого бота при запуске режима:
# python main.py bot
START_REPLY = "@odlyl"

# Кнопка для открытия чата с найденным пользователем и готовым первым сообщением.
# Работает только если у найденного пользователя есть username.
# True = показывать кнопку "Написать" с готовым текстом.
# False = не показывать эту кнопку.
SHOW_FIRST_MESSAGE_BUTTON = True
FIRST_MESSAGE_BUTTON_TEXT = "💬 Написать пользователю"
FIRST_MESSAGE_TEXT = "Привет! Хотел с тобой связаться."
