from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_TOKEN = "123456789:abc"
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

BOT_TOKEN = "8280733179:AAFe9vdIJvIV5v1yAfk7qZMy7nn-0ndB2eI"
FAN_NOMI = "Fizika"

DATA = {
    "maruzalar": {
        "title": "Ma'ruzalar",
        "topics": [
            {"id": "m1", "name": "1-mavzu. Elektron tijorat xavfsizligi", "file_id": "BQACAgIAAxkBAAMPaeZ6j-D3qk6NmFiHiT01MX87LQwAAiGnAALETzhLGaKRyTGAhPw7BA"},
            {"id": "m2", "name": "2-mavzu. Molekulyar fizika", "file_id": ""},
            {"id": "m3", "name": "3-mavzu. Elektr", "file_id": ""},
        ],
    },
    "laboratoriya": {
        "title": "Laboratoriya ishlari",
        "topics": [
            {"id": "l1", "name": "1-laboratoriya. Qattiq_jismlarning_zichligini_gidrostatik_usul_bilan_aniqlash", "file_id": "BQACAgIAAxkBAAMVaeZ8Yj-TkjREXIQI2RxK1opPmd0AAjmnAALETzhLr6D9pXBBQjI7BA"},
            {"id": "l2", "name": "2-laboratoriya. Arximed qonuni", "file_id": ""},
        ],
    },
    "amaliyot": {
        "title": "Amaliyot",
        "topics": [
            {"id": "a1", "name": "1-amaliyot. Nyuton qonunlari", "file_id": ""},
            {"id": "a2", "name": "2-amaliyot. Bosim", "file_id": ""},
        ],
    },
}

SEARCH_MODE = "search_mode"


def topic_status(file_id: str) -> str:
    return "✅" if file_id.strip() else "⏳"


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📚 Ma'ruzalar", callback_data="section:maruzalar")],
        [InlineKeyboardButton("🧪 Laboratoriya ishlari", callback_data="section:laboratoriya")],
        [InlineKeyboardButton("📝 Amaliyot", callback_data="section:amaliyot")],
        [InlineKeyboardButton("🔍 Qidiruv", callback_data="search")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]
    ])


def get_section_keyboard(section_key: str) -> InlineKeyboardMarkup:
    section = DATA[section_key]
    keyboard = []

    for topic in section["topics"]:
        status = topic_status(topic["file_id"])
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {topic['name']}",
                callback_data=f"topic:{section_key}:{topic['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def find_topic_by_id(section_key: str, topic_id: str):
    section = DATA.get(section_key)
    if not section:
        return None

    for topic in section["topics"]:
        if topic["id"] == topic_id:
            return topic

    return None


def search_topics(query: str):
    query = query.strip().lower()
    results = []

    for section_key, section_data in DATA.items():
        for topic in section_data["topics"]:
            if query in topic["name"].lower():
                results.append({
                    "section_key": section_key,
                    "section_title": section_data["title"],
                    "topic": topic,
                })

    return results


def build_search_results_keyboard(results) -> InlineKeyboardMarkup:
    keyboard = []

    for item in results:
        topic = item["topic"]
        status = topic_status(topic["file_id"])
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {topic['name']} ({item['section_title']})",
                callback_data=f"topic:{item['section_key']}:{topic['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[SEARCH_MODE] = False

    text = (
        f"Assalomu alaykum!\n\n"
        f"Bu *{FAN_NOMI}* bo'yicha ta'lim boti.\n"
        f"Kerakli bo'limni tanlang:"
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown",
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown",
        )


async def section_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    section_key = query.data.split(":")[1]
    section = DATA.get(section_key)

    if not section:
        await query.edit_message_text(
            "Bo'lim topilmadi.",
            reply_markup=get_back_keyboard(),
        )
        return

    await query.edit_message_text(
        f"📂 *{section['title']}*\n\nKerakli mavzuni tanlang:",
        reply_markup=get_section_keyboard(section_key),
        parse_mode="Markdown",
    )


async def topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, section_key, topic_id = query.data.split(":")
    topic = find_topic_by_id(section_key, topic_id)

    if not topic:
        await query.message.reply_text(
            "Mavzu topilmadi.",
            reply_markup=get_back_keyboard(),
        )
        return

    file_id = topic["file_id"].strip()

    if not file_id:
        await query.message.reply_text(
            f"⏳ {topic['name']} uchun PDF hali yuklanmagan.",
            reply_markup=get_back_keyboard(),
        )
        return

    await context.bot.send_chat_action(
        chat_id=query.message.chat_id,
        action=ChatAction.UPLOAD_DOCUMENT,
    )

    await query.message.reply_document(
        document=file_id,
        caption=f"📄 {topic['name']}",
        reply_markup=get_back_keyboard(),
    )


async def search_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    context.user_data[SEARCH_MODE] = True

    await query.edit_message_text(
        "🔍 Qidiruv rejimi yoqildi.\n\nMavzu nomini yozing.",
        reply_markup=get_back_keyboard(),
    )


async def search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get(SEARCH_MODE, False):
        return

    query_text = update.message.text.strip()
    results = search_topics(query_text)
    context.user_data[SEARCH_MODE] = False

    if not results:
        await update.message.reply_text(
            f"❌ '{query_text}' bo'yicha hech narsa topilmadi.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await update.message.reply_text(
        f"🔎 '{query_text}' bo'yicha topilgan natijalar:",
        reply_markup=build_search_results_keyboard(results),
    )


async def back_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[SEARCH_MODE] = False
    await start_handler(update, context)


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document

    if not document:
        return

    if document.mime_type != "application/pdf":
        await update.message.reply_text("Faqat PDF yuboring.")
        return

    await update.message.reply_text(
        f"Fayl nomi: {document.file_name}\n\nfile_id:\n{document.file_id}"
    )


async def unknown_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get(SEARCH_MODE, False):
        return

    await update.message.reply_text(
        "Iltimos, menyudan foydalaning yoki /start bosing.",
        reply_markup=get_main_menu_keyboard(),
    )


def main() -> None:
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    get_updates_request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(section_handler, pattern=r"^section:"))
    application.add_handler(CallbackQueryHandler(topic_handler, pattern=r"^topic:"))
    application.add_handler(CallbackQueryHandler(search_button_handler, pattern=r"^search$"))
    application.add_handler(CallbackQueryHandler(back_main_handler, pattern=r"^back_main$"))
    application.add_handler(MessageHandler(filters.Document.PDF, document_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_text_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text_handler))

    print("Bot ishga tushdi...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()