"""
This ChatGPT Telegram Bot program takes the user's messages as input queries for ChatGPT, then returns ChatGPT's answer in a message.

Usage:
Send /start to initiate a conversation with ChatGPT.
Send /help to get a list of commands recognized by ChatGPT Telegram Bot.
Send a normal message after sending /start to ask a question to ChatGPT.
Send /quit to quit the conversation with ChatGPT.
Press Control-C on the command line to stop the bot.
"""

import asyncio
from dotenv import load_dotenv
import logging
import os
from revChatGPT.ChatGPT import Chatbot
from telegram import constants, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

CHOOSING = range(1)

class ChatGPTChatBot():
    def __init__(self):
        self.chatbot = Chatbot({"session_token": os.environ['CHATGPT_SESSION_TOKEN']}, conversation_id=None, parent_id=None)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a ChatGPT bot. Send /help to get a list of commands, or just send me a question to ask!")
        return CHOOSING

    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_query = update.message.text
        loop = asyncio.get_event_loop()
        response, _ = await asyncio.gather(
            loop.run_in_executor(None, self.chatbot.ask, user_query),
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        )
        response_text = response['message']
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
        return CHOOSING

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=(
            "/start: Start ChatGPT Bot.\n"
            "/help: Get a list of valid commands.\n"
            "/quit: Quit conversation."
        ))
        return CHOOSING

    async def quit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Quitting ChatGPT chat...")
        return ConversationHandler.END

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
        return CHOOSING

def main() -> None:
    application = ApplicationBuilder().token(os.environ['TELEGRAM_BOT_TOKEN']).build()
    gptbot = ChatGPTChatBot()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', gptbot.start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), gptbot.chatgpt
                ),
                CommandHandler('help', gptbot.help),
                CommandHandler('quit', gptbot.quit)
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, gptbot.unknown)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()