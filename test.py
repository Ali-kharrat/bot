import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

START, GIFTCODE, LOCATION, BIO = range(4)

connection  = sqlite3.connect("SSES.db")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["ثبت نام"]]

    await update.message.reply_text("slm be bot khosh amadi",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="ثبت نام"
        ),
    )


    return START


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    cursor  = connection.cursor()
    cursor.execute(f"INSERT INTO user VALUES({user.id},'empty','empty')")
    connection.commit()
    logger.info("Name %s: %s" ,user.id,update.message.text)
    await update.message.reply_text("نام و نام خانوادگی خود را وارد کنید",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GIFTCODE

async def gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global name_
    name_ = update.message.text
    user = update.message.from_user
    cursor  = connection.cursor()
    cursor.execute(f"UPDATE user SET name =  '{name_}' WHERE userID = {user.id}")
    connection.commit()
    reply_keyboard = [["ندارم"]]
    logger.info("نام و نام خوانوادگی %s:%s", user.id,name_)
    await update.message.reply_text(
        "لطفا کد تخفیف خود را وارد کنید",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="ندارم")
    )
    
    return BIO



async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global giftcode
    giftcode = update.message.text
    user = update.message.from_user
    cursor  = connection.cursor()
    cursor.execute(f"UPDATE user SET giftcode =  '{giftcode}' WHERE userID = {user.id}")
    connection.commit()
    logger.info("gift code %s: %s", user.id,giftcode)
    await update.message.reply_text(
        "پیش ثبت نام شما انجام شد به زودی براتون لینک پرداخت ارسال میشود."
    )

    return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6191203365:AAF3pohjgvXATSe1LTFow9aAmM-4fR7L7sM").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [MessageHandler(filters.Regex("ثبت نام"), name)],
            GIFTCODE: [MessageHandler(filters.TEXT,gift_code)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()