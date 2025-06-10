import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import BadRequest

# === CONFIG ===
BOT_TOKEN = "8043406036:AAHfFIEcS8IYs6wmem86IuJSMuCK3Oy3ytg"  # Replace with your actual bot token
FORCE_SUB_CHANNEL = "@Joker_offical0"  # Replace with your channel username

# === TERABOX SCRAPER ===
def get_terabox_video_info(share_link):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(share_link, headers=headers, timeout=10)
        if "password" in resp.text:
            return {"error": "🔒 Password protected links aren't supported."}
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "Unknown Title"
        return {
            "title": title,
            "note": "📄 Note: Direct video link extraction from Terabox is limited.",
            "link": share_link
        }
    except Exception as e:
        return {"error": f"❌ Error: {str(e)}"}

# === FORCE SUBSCRIBE CHECK ===
async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

# === INLINE BUTTON ===
def join_channel_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL.strip('@')}")]
    ])

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_subscribed(user_id, context):
        await update.message.reply_text(
            "🚫 You must join our channel to use this bot.",
            reply_markup=join_channel_button()
        )
        return
    await update.message.reply_text("👋 Welcome! Send me a Terabox link to get started.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_subscribed(user_id, context):
        await update.message.reply_text(
            "🚫 Please join our channel to continue.",
            reply_markup=join_channel_button()
        )
        return

    url = update.message.text.strip()
    if "terabox.com" not in url:
        await update.message.reply_text("❌ Not a valid Terabox link.")
        return

    info = get_terabox_video_info(url)
    if "error" in info:
        await update.message.reply_text(info["error"])
    else:
        await update.message.reply_text(
            f"🎬 *Title:* {info['title']}\n🔗 *Link:* {info['link']}\n📝 {info['note']}",
            parse_mode='Markdown'
        )

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()   
