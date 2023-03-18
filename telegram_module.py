from telegram import Update, ForceReply, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv, find_dotenv
import os
from config import TG_ENABLED



load_dotenv(find_dotenv())
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def sendMessage(tekst) -> None:
    try:
        if TG_ENABLED == True:
            updater = Updater(token=TG_TOKEN, use_context=True)
            updater.bot.send_message(chat_id=TG_CHAT_ID,text=tekst)
    except Exception as e: print(e)


def pause(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    global isBotPaused
    isBotPaused = False if isBotPaused else True
    sendMessage(f'Bot is now {"paused" if {isBotPaused} else "not paused"}')


def main() -> None:
    """Start the bot."""
    if TG_ENABLED == True:
        updater = Updater(token=TG_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        updater.start_polling()
        updater.bot.send_message(chat_id=TG_CHAT_ID,text=f'Bot started succesfully!')
        #updater.idle() #commented out for threading





