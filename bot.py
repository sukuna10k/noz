import logging
import threading
import http.server
import socketserver
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import (
    add_user, update_balance, get_balance, add_referral,
    block_user, unblock_user, get_users_count, get_blocked_users_count, get_all_users
)
from config import API_ID, API_HASH, BOT_TOKEN, ADMINS

# Initialize Pyrogram Client
app = Client("Noz_coins_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Command /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user

    # Add the user to the database
    add_user(user.id)

    # Check if the user joined using a referral link
    if len(message.command) > 1:
        referrer_id = message.command[1]  # Extract referrer ID from /start <referrer_id>
        if referrer_id.isdigit() and int(referrer_id) != user.id:
            # Add the referral
            add_referral(int(referrer_id), user.id)
            # Notify the referrer
            try:
                await client.send_message(
                    chat_id=int(referrer_id),
                    text=f"🎉 Someone joined using your referral link! You've earned 10 $NOZ."
                )
            except Exception as e:
                logger.warning(f"Failed to notify referrer {referrer_id}: {e}")

    # Generate the user's link
    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = f"https://t.me/user?id={user.id}"

    # Create the keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Help", callback_data="help")],
            [InlineKeyboardButton("Join Community", url="https://t.me/Stars_chain")],
        ]
    )

    # Welcome message
    text = (
        f"✦ {user_link} ✦ Welcome! 🌟 Earn tokens by sharing your referral link, "
        "or participate in bonus games on [Nozcoin](https://t.me/nozcoin_bot)."
    )

    # Send the welcome message
    await message.reply_photo(
        photo="https://iili.io/2Wg8uK7.md.jpg",
        caption=text,
        reply_markup=keyboard
    )

# Command /help
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    text = (
        "[Nozcoin](https://t.me/nozcoin_bot) helps you earn tokens which you can convert to $TON.\n\n"
        "Click /earn to share your referral link and start earning $NOZ.\n"
        "Click /balance to check your balance.\n"
        "Click /convert to convert your $NOZ to $TON.\n\n"
        "1 invited user = 10 $NOZ = $0.5 TON.\n"
        "You need 1000 $NOZ to convert to $TON."
    )
    await message.reply(text)

# Help button handler
@app.on_callback_query(filters.regex("help"))
async def help_button(client: Client, callback_query: CallbackQuery):
    text = (
        "[Nozcoin](https://t.me/nozcoin_bot) helps you earn tokens which you can convert to $TON.\n\n"
        "Click /earn to share your referral link and start earning $NOZ.\n"
        "Click /balance to check your balance.\n"
        "Click /convert to convert your $NOZ to $TON.\n\n"
        "1 invited user = 10 $NOZ = $0.5 TON.\n"
        "You need 1000 $NOZ to convert to $TON."
    )
    await callback_query.message.reply(text)
    await callback_query.answer()

# Command /earn
@app.on_message(filters.command("earn"))
async def earn_command(client: Client, message: Message):
    user = message.from_user.id
    add_user(user)

    referral_link = f"https://t.me/{client.me.username}?start={user}"
    await message.reply(f"Here is your referral link: {referral_link}\nShare it to earn 10 $NOZ for each invited user.")

# Command /balance
@app.on_message(filters.command("balance"))
async def balance_command(client: Client, message: Message):
    user = message.from_user.id
    balance = get_balance(user)
    await message.reply(f"Your balance: {balance} $NOZ. Share your referral link to earn more $NOZ.")

# Command /convert
@app.on_message(filters.command("convert"))
async def convert_command(client: Client, message: Message):
    user = message.from_user.id
    balance = get_balance(user)
    if balance < 1000:
        await message.reply("Your balance is less than 1000 $NOZ.")
    else:
        await message.reply("Send the proof message in the channel's comments group.")

# Command /broadcast
@app.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("You must reply to a message to broadcast it.")
        return

    reply_message = message.reply_to_message
    all_users = get_all_users()
    successful, failed = 0, 0

    for user_id in all_users:
        try:
            await reply_message.copy(chat_id=user_id)
            successful += 1
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
            failed += 1

    await message.reply(f"Message successfully broadcasted to {successful} users. Failed: {failed} users.")

# Command /status
@app.on_message(filters.command("status") & filters.user(ADMINS))
async def status_command(client: Client, message: Message):
    total_users = get_users_count()
    blocked_users = get_blocked_users_count()
    await message.reply(
        f"Total users: {total_users}\n"
        f"Users who blocked the bot: {blocked_users}"
    )

# Dummy HTTP server for Koyeb health check
def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        logger.info("HTTP server is running for health checks on port 8000")
        httpd.serve_forever()

# Run the bot
if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run()
