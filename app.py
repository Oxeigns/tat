import asyncio
import html
import os
import random
import time
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN") or ""
BOT_NAME = os.getenv("BOT_NAME", "Demo Bot")
CREDIT = os.getenv("CREDIT", "YourName")
DEMO_TAG = os.getenv("DEMO_TAG", "DEMO ONLY • NO REAL ACTIONS")

ASK_USERNAME = 1

SPINNER = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
MATRIX_CHARS = "01#@$%&*+=?~:;abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def boxed(text: str) -> str:
    return f"<pre>{html.escape(text)}</pre>"


def menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Run demo ✅", callback_data="run_demo")]]
    )


def start_card() -> str:
    return boxed(
        f"Welcome in {BOT_NAME}\n"
        f"MADE BY {CREDIT}\n\n"
        f"{DEMO_TAG}\n\n"
        f"Press button to start."
    )


def bar(pct: int, width: int = 22) -> str:
    filled = int((pct / 100) * width)
    return "[" + ("█" * filled) + ("░" * (width - filled)) + f"] {pct:3d}%"


def now_ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def clean_username(u: str) -> str:
    u = (u or "").strip()
    if not u or " " in u:
        return ""
    if not u.startswith("@"):
        u = "@" + u
    return u


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            start_card(),
            parse_mode=ParseMode.HTML,
            reply_markup=menu_keyboard(),
            disable_web_page_preview=True,
        )
    elif update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=start_card(),
            parse_mode=ParseMode.HTML,
            reply_markup=menu_keyboard(),
            disable_web_page_preview=True,
        )


async def demo_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    await q.message.edit_text(
        boxed("Send me a username to run banning sessions\n\nExample: @username"),
        parse_mode=ParseMode.HTML,
    )
    return ASK_USERNAME


async def got_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = clean_username(update.message.text if update.message else "")
    if not username:
        await update.effective_message.reply_text(
            boxed("Please send a valid username like @username"),
            parse_mode=ParseMode.HTML,
        )
        return ASK_USERNAME

    await update.effective_message.reply_text(
        boxed("✅ Request accepted\nStarting banning process..."),
        parse_mode=ParseMode.HTML,
    )

    asyncio.create_task(run_all_styles_demo(update.effective_chat.id, context, username))
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_message:
        await update.effective_message.reply_text(
            boxed("Cancelled. Send /start to begin again."),
            parse_mode=ParseMode.HTML,
        )
    return ConversationHandler.END


async def edit_terminal(msg, username: str, lines: list[str], footer: bool = True):
    header = [
        f"{BOT_NAME} ::  terminal",
        f"Target: {username}",
        "-" * 34,
    ]
    body = "\n".join(lines)
    end = f"\n\n{DEMO_TAG}" if footer else ""
    await msg.edit_text(boxed("\n".join(header) + "\n" + body + end), parse_mode=ParseMode.HTML)


async def ios_dots(msg, username: str, title: str, seconds: float):
    start = time.time()
    dots = 0
    while time.time() - start < seconds:
        dots = (dots + 1) % 4
        line = f"{title}{'.' * dots}{' ' * (3 - dots)}"
        await edit_terminal(msg, username, [line])
        await asyncio.sleep(0.6)


def matrix_line(width: int = 34) -> str:
    return "".join(random.choice(MATRIX_CHARS) for _ in range(width))


async def matrix_burst(msg, username: str, seconds: float, label: str):
    start = time.time()
    while time.time() - start < seconds:
        lines = [
            f"{label} :: {random.randint(1000, 9999)}",
            matrix_line(),
            matrix_line(),
            matrix_line(),
        ]
        await edit_terminal(msg, username, lines)
        await asyncio.sleep(0.45)


async def spinner_with_logs(msg, username: str, title: str, seconds: float, extra: str = ""):
    start = time.time()
    i = 0
    while time.time() - start < seconds:
        spin = SPINNER[i % len(SPINNER)]
        latency = random.randint(18, 62)
        jitter = random.randint(1, 9)
        lines = [
            f"[{now_ts()}] {title} {spin}",
            f"[{now_ts()}] net: latency={latency}ms jitter={jitter}ms",
        ]
        if extra:
            lines.append(f"[{now_ts()}] {extra}")
        await edit_terminal(msg, username, lines)
        await asyncio.sleep(0.55)
        i += 1


async def progress_with_logs(msg, username: str, title: str, total_seconds: float, steps: int, log_pool: list[str]):
    for s in range(steps + 1):
        pct = int((s / steps) * 100)
        log = log_pool[min(s, len(log_pool) - 1)] if log_pool else ""
        lines = [f"[{now_ts()}] {title}", bar(pct)]
        if log:
            lines += ["", f"[{now_ts()}] {log}"]
        await edit_terminal(msg, username, lines)
        await asyncio.sleep(total_seconds / steps)


async def run_all_styles_demo(chat_id: int, context: ContextTypes.DEFAULT_TYPE, username: str):
    msg = await context.bot.send_message(chat_id=chat_id, text=boxed("Starting..."), parse_mode=ParseMode.HTML)

    await ios_dots(msg, username, "Initializing demo engine", 3.5)
    await spinner_with_logs(msg, username, "Booting modules", 3.5, extra="loading: ui • queue • -core")
    await matrix_burst(msg, username, 4.5, "Decrypting routing map")

    await progress_with_logs(
        msg, username,
        "Connecting to Telegram network (✅)",
        total_seconds=7.2,
        steps=12,
        log_pool=[
            "Resolving endpoints…",
            "Opening secure channel…",
            "Handshake OK…",
            "Session prepared…",
            "Transport stabilized…",
            "Ping ok…",
            "Route locked…",
        ],
    )

    await ios_dots(msg, username, "Verifying session", 3.0)

    await edit_terminal(
        msg, username,
        [
            "finished ✅",
            "FREEZEING  action was performed.",
            "",
            f"[{now_ts()}] Send /start to run again.",
        ]
    )


def main() -> None:
    if not BOT_TOKEN or ":" not in BOT_TOKEN:
        raise RuntimeError("Set BOT_TOKEN (or TOKEN) in Heroku Config Vars.")

    application = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(demo_button, pattern="^run_demo$")],
        states={ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_username)]},
        fallbacks=[CommandHandler("start", start_cmd), CommandHandler("cancel", cancel_cmd)],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(conv)

    print("[BOOT] Polling mode enabled")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
