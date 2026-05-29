import argparse
import asyncio
from html import escape
from pathlib import Path
from urllib.parse import quote

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.users import GetFullUserRequest

from config import (
    ADMIN_ID,
    API_HASH,
    API_ID,
    BOT_TOKEN,
    DB_NAME,
    FIRST_MESSAGE_BUTTON_TEXT,
    FIRST_MESSAGE_TEXT,
    MAX_STARS_LEVEL,
    MIN_STARS_LEVEL,
    PHOTO_PATH,
    SEND_USERS_WHO_REQUIRE_PREMIUM_TO_CONTACT,
    SEND_USERS_WITH_PAID_MESSAGES,
    SESSION_NAME,
    SHOW_FIRST_MESSAGE_BUTTON,
    START_REPLY,
    TARGET_CHAT,
)

DELETE_MESSAGE_CALLBACK = "delete_found_user_message"


def banner(text: str) -> None:
    print("\n" + "=" * 52)
    print(text)
    print("=" * 52 + "\n")


async def init_db() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS found_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                level INTEGER,
                is_given INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def add_user_if_new(user_id: int, username: str | None, level: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        if username:
            cursor = await db.execute(
                """
                SELECT id
                FROM found_users
                WHERE user_id = ? OR username = ?
                LIMIT 1
                """,
                (user_id, username),
            )
        else:
            cursor = await db.execute(
                """
                SELECT id
                FROM found_users
                WHERE user_id = ?
                LIMIT 1
                """,
                (user_id,),
            )

        exists = await cursor.fetchone()
        if exists:
            return False

        await db.execute(
            """
            INSERT INTO found_users (user_id, username, level)
            VALUES (?, ?, ?)
            """,
            (user_id, username, level),
        )
        await db.commit()
        return True


async def get_random_user() -> str | None:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, username, user_id
            FROM found_users
            WHERE is_given = 0
            ORDER BY RANDOM()
            LIMIT 1
            """
        )
        row = await cursor.fetchone()

        if not row:
            return None

        db_id, username, user_id = row

        await db.execute(
            """
            UPDATE found_users
            SET is_given = 1
            WHERE id = ?
            """,
            (db_id,),
        )
        await db.commit()

        return f"@{username}" if username else f"tg://user?id={user_id}"


def in_level_range(level: int) -> bool:
    if level < MIN_STARS_LEVEL:
        return False
    if MAX_STARS_LEVEL is not None and level > MAX_STARS_LEVEL:
        return False
    return True


def paid_messages_value(full_user) -> int | None:
    value = getattr(full_user.full_user, "send_paid_messages_stars", None)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def requires_premium_to_contact(user, full_user) -> bool:
    return bool(
        getattr(full_user.full_user, "contact_require_premium", False)
        or getattr(user, "contact_require_premium", False)
    )


def profile_text(user) -> str:
    return f"@{user.username}" if user.username else f"tg://user?id={user.id}"


def profile_link(user) -> str:
    return f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.id}"


def found_user_keyboard(user) -> InlineKeyboardMarkup | None:
    keyboard: list[list[InlineKeyboardButton]] = []

    if SHOW_FIRST_MESSAGE_BUTTON and user.username and FIRST_MESSAGE_TEXT:
        draft_text = quote(FIRST_MESSAGE_TEXT)
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=FIRST_MESSAGE_BUTTON_TEXT,
                    url=f"https://t.me/{user.username}?text={draft_text}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🗑 Удалить сообщение",
                callback_data=DELETE_MESSAGE_CALLBACK,
            )
        ]
    )

    if not keyboard:
        return None

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def register_bot_handlers(dp: Dispatcher) -> None:
    @dp.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(START_REPLY)

    @dp.callback_query(lambda callback: callback.data == DELETE_MESSAGE_CALLBACK)
    async def delete_found_user_message(callback: CallbackQuery) -> None:
        if not callback.message:
            await callback.answer("Сообщение уже недоступно", show_alert=True)
            return

        try:
            await callback.message.delete()
            await callback.answer()
        except Exception:
            await callback.answer("Не удалось удалить сообщение", show_alert=True)


def should_send_user(user, full_user, level: int) -> tuple[bool, str, int | None, bool]:
    paid_messages = paid_messages_value(full_user)
    premium_contact = requires_premium_to_contact(user, full_user)

    if not in_level_range(level):
        return False, "level_not_in_range", paid_messages, premium_contact

    if not SEND_USERS_WHO_REQUIRE_PREMIUM_TO_CONTACT and premium_contact:
        return False, "requires_premium_to_contact", paid_messages, premium_contact

    if not SEND_USERS_WITH_PAID_MESSAGES and paid_messages:
        return False, "paid_messages_enabled", paid_messages, premium_contact

    return True, "ok", paid_messages, premium_contact


async def send_found_user(
    bot: Bot,
    user,
    level: int,
    paid_messages: int | None,
    premium_contact: bool,
) -> None:
    profile = escape(profile_text(user))
    link = escape(profile_link(user), quote=True)
    paid_text = f"{paid_messages} звезд" if paid_messages else "бесплатно"
    premium_contact_text = "да" if premium_contact else "нет"
    keyboard = found_user_keyboard(user)

    caption = (
        "🎯 <b>Найден подходящий пользователь</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👤 <b>Профиль</b>\n"
        f"├ 🔗 Ссылка: <a href=\"{link}\">{profile}</a>\n"
        f"└ 🆔 ID: <code>{user.id}</code>\n\n"
        "⭐ <b>Параметры</b>\n"
        f"├ 📊 Уровень Stars: <b>{level}</b>\n"
        f"├ 💬 Стоимость сообщения: <b>{paid_text}</b>\n"
        f"└ 🔒 Писать могут только Premium: <b>{premium_contact_text}</b>\n\n"
        "💾 <i>Пользователь сохранен в базе и повторно отправлен не будет.</i>"
    )

    photo_file = Path(PHOTO_PATH)
    if photo_file.exists():
        await bot.send_photo(
            ADMIN_ID,
            photo=FSInputFile(photo_file),
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            ADMIN_ID,
            caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


async def run_parser() -> None:
    banner("TELEGRAM USER PARSER STARTING")
    await init_db()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    register_bot_handlers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot))

    await client.start()
    banner("PARSER IS RUNNING")

    try:
        checked_users = 0
        found_users = 0

        async for user in client.iter_participants(TARGET_CHAT):
            checked_users += 1
            try:
                if user.bot:
                    continue

                profile = profile_text(user)
                print(f"CHECK USER | {user.id} / {profile}")

                full_user = await client(GetFullUserRequest(user.id))
                stars = getattr(full_user.full_user, "stars_rating", None)

                if not stars or not hasattr(stars, "level"):
                    continue

                level = stars.level
                should_send, reason, paid_messages, premium_contact = should_send_user(
                    user,
                    full_user,
                    level,
                )

                if not should_send:
                    print(f"SKIP | {user.id} / {profile} | {reason}")
                    continue

                is_new = await add_user_if_new(user.id, user.username, level)
                if not is_new:
                    print(f"SKIP DUPLICATE | {user.id} / {profile}")
                    continue

                found_users += 1
                print(
                    f"FOUND TARGET USER | {user.id} / {profile} | "
                    f"{level} lvl | paid={paid_messages or 0}"
                )
                await send_found_user(bot, user, level, paid_messages, premium_contact)

            except FloodWaitError as error:
                print(f"FLOOD WAIT | sleep {error.seconds} sec")
                await asyncio.sleep(error.seconds)
            except Exception as error:
                user_id = getattr(user, "id", "unknown")
                print(f"ERROR | USER: {user_id} | {error}")

        print(
            f"SCAN FINISHED | checked={checked_users} | found_new={found_users} | "
            "bot_stays_online=True"
        )
        await asyncio.Event().wait()
    finally:
        banner("SYSTEM SHUTDOWN")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
        await client.disconnect()
        await bot.session.close()


async def run_bot() -> None:
    banner("SIMPLE TELEGRAM BOT STARTING")

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    register_bot_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telegram parser and bot")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("parser", "bot"),
        default="parser",
        help="parser - search users, bot - run /start bot",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.mode == "bot":
        await run_bot()
    else:
        await run_parser()


if __name__ == "__main__":
    asyncio.run(main())
