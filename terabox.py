from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from pymongo import MongoClient
import time
import threading
import uuid
import urllib.parse
from urllib.parse import urlparse
import requests

OWNER_ID = 7663297585

load_dotenv('config.env', override=True)
logging.basicConfig(
    level=logging.INFO,  
    format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s - %(filename)s:%(lineno)d"
)

logger = logging.getLogger(__name__)

logging.getLogger("pyrogram.session").setLevel(logging.ERROR)
logging.getLogger("pyrogram.connection").setLevel(logging.ERROR)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.ERROR)

aria2 = Aria2API(
    Aria2Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)
options = {
    "max-tries": "50",
    "retry-wait": "3",
    "continue": "true",
    "allow-overwrite": "true",
    "min-split-size": "4M",  # File chunks
    "split": "16",  # Increase the number of parts for faster download
    "max-connection-per-server": "8",  # More connections per server
    "max-concurrent-downloads": "5",  # Multiple downloads in parallel
    "dir": "/tmp/aria2_downloads",  # Temporary directory
    "max-download-limit": "0",  # Unlimited download speed
    "min-download-limit": "1M",  # Minimum download speed to keep the connection alive
}
aria2.set_global_options(options)



API_ID = os.environ.get('TELEGRAM_API', '')
if len(API_ID) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

API_HASH = os.environ.get('TELEGRAM_HASH', '')
if len(API_HASH) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)
    
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '')
if len(DUMP_CHAT_ID) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    DUMP_CHAT_ID = int(DUMP_CHAT_ID)

FSUB_ID = os.environ.get('FSUB_ID', '')
if len(FSUB_ID) == 0:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    FSUB_ID = int(FSUB_ID)

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if len(DATABASE_URL) == 0:
    logging.error("DATABASE_URL variable is missing! Exiting now")
    exit(1)

SHORTENER_API = os.environ.get('SHORTENER_API', '')
if len(SHORTENER_API) == 0:
    logging.error("SHORTENER_API variable is missing! Exiting now")
    exit(1)

USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING', '')
if len(USER_SESSION_STRING) == 0:
    logging.info("USER_SESSION_STRING variable is missing! Bot will split Files in 2Gb...")
    USER_SESSION_STRING = None

DATABASE_NAME = "terabox"
COLLECTION_NAME = "user_requests"

client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

app = Client("user_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# with Client("user_session", api_id=API_ID, api_hash=API_HASH) as app:
#     print("Session string generated successfully!")
#     print(f"Session String: {app.export_session_string()}")

user = None
SPLIT_SIZE = 2093796556
if USER_SESSION_STRING:
    user = Client("jetu", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION_STRING)
    SPLIT_SIZE = 4241280205

VALID_DOMAINS = [
    'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 
    'momerybox.com', 'teraboxapp.com', '1024tera.com', 
    'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com', 
    'teraboxlink.com', 'terafileshare.com', 'teraboxshare.com'
]
last_update_time = 0

async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(FSUB_ID, user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False
    
def is_valid_url(url):
    parsed_url = urlparse(url)
    return any(parsed_url.netloc.endswith(domain) for domain in VALID_DOMAINS)

def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

def shorten_url(url):
    #You can change api_url with your choice shortener
    api_url = 'https://seturl.in/api'
    params = {
        "api": SHORTENER_API,
        "url": url
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        else:
            logger.error(f"Failed to shorten URL: {data}")
            return None
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return None

def generate_uuid(user_id):
    token = str(uuid.uuid4())
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"token": token, "token_status": "inactive", "token_expiry": None}},
        upsert=True
    )
    return token

def activate_token(user_id, token):
    user_data = collection.find_one({"user_id": user_id, "token": token})
    if user_data:
        collection.update_one(
            {"user_id": user_id, "token": token},
            {"$set": {"token_status": "active", "token_expiry": datetime.now() + timedelta(hours=12)}}
        )
        return True
    return False

def has_valid_token(user_id):
    user_data = collection.find_one({"user_id": user_id})
    if user_data and user_data.get("token_status") == "active":
        if datetime.now() < user_data.get("token_expiry"):
            return True
    return False

import time
from pyrogram import Client, filters
from pyrogram.types import Message

@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    # Debugging: Print when the command is triggered
    print("Ping command triggered.")

    start_time = time.time()  # Record the time before processing
    
    try:
        # Send the initial quick response
        response_msg = await message.reply_text("🏓 Pong!")
        print("Sent initial Pong message.")
    except Exception as e:
        print(f"Error sending Pong message: {e}")

    # Calculate response time
    end_time = time.time()
    response_time = round((end_time - start_time) * 1000)  # Convert to milliseconds
    
    try:
        # Edit the message with the response time
        await response_msg.edit_text(f"🏓 Pong! Response time: {response_time} ms")
        print("Edited message with response time.")
    except Exception as e:
        print(f"Error editing Pong message: {e}")

import psutil
import platform
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# Global variables to track stats
start_time = datetime.now()
download_count = 0
total_download_size = 0

@app.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    # Only allow the owner to access stats
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⚠️ This command is only available to the bot owner.")
        return
    
    # Get system stats
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    # Get MongoDB stats
    user_count = collection.count_documents({})
    active_tokens = collection.count_documents({"token_status": "active"})
    
    # Calculate uptime
    uptime = datetime.now() - start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Format the stats message
    stats_text = (
        f"📊 <b>BOT STATISTICS</b> 📊\n\n"
        f"<b>System Information:</b>\n"
        f"• OS: {platform.system()} {platform.release()}\n"
        f"• CPU Usage: {cpu_usage}%\n"
        f"• RAM Usage: {ram_usage}%\n"
        f"• Disk Usage: {disk_usage}%\n\n"
        
        f"<b>Bot Information:</b>\n"
        f"• Uptime: {days}d, {hours}h, {minutes}m, {seconds}s\n"
        f"• Total Users: {user_count}\n"
        f"• Active Tokens: {active_tokens}\n"
        f"• Downloads: {download_count}\n"
        f"• Total Downloaded: {format_size(total_download_size)}\n\n"
        
        f"<b>Database Information:</b>\n"
        f"• Connection: {'✅ Connected' if client else '❌ Disconnected'}\n"
        f"• Database: {DATABASE_NAME}\n"
        f"• Collection: {COLLECTION_NAME}\n\n"
        
        f"<b>Bot Version:</b> 1.0.0\n"

        
        f"🚀 <b>Powered by:</b> <a href='https://t.me/NyxKingx'>NʏxKɪɴɢ❤️🚀</a>"
    )
    
    try:
        await message.reply_text(stats_text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error sending stats: {e}")
        await message.reply_text("Error generating stats. Check logs for details.")


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/jffmain")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/NyxKingX")
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])
    final_msg = (
        "🌟 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅ ʙᴏᴛ!\n\n"
        "ᴊᴜsᴛ sᴇɴᴅ ᴍᴇ ᴀ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ, ᴀɴᴅ ɪ'ʟʟ ꜰᴇᴛᴄʜ ᴛʜᴇ ᴠɪᴅᴇᴏ ꜰᴏʀ ʏᴏᴜ 🎬🚀"
    )
    image_url = "https://i.ibb.co/dsXGtrGt/anime-girl-lollipop-2k-wallpaper-uhdpaper-com-375-5-d.jpg"

    if len(message.command) > 1 and len(message.command[1]) == 36:
        token = message.command[1]
        user_id = message.from_user.id

        if activate_token(user_id, token):
            caption = "🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ.\n\nYour token has been activated successfully! You can now use the bot."
        else:
            caption = "🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ.\n\nInvalid token. Please generate a new one using /start."

        await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=caption, reply_markup=reply_markup)

    else:
        user_id = message.from_user.id
        if not has_valid_token(user_id):
            token = generate_uuid(user_id)
            long_url = f"https://t.me/{app.me.username}?start={token}"

            # 👑 Bypass shortening for OWNER
            if user_id == OWNER_ID:
                short_url = long_url
            else:
                short_url = shorten_url(long_url)

            if short_url:
                reply_markup2 = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Generate Token Link", url=short_url)],
                    [join_button, developer_button],
                ])
                caption = (
                    "🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ.\n\n"
                    "Please generate your Token, which will be valid for 12Hrs."
                )

                await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=caption, reply_markup=reply_markup2)
            else:
                await message.reply_text("Failed to generate the final link. Please try again.")
        else:
            await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=final_msg, reply_markup=reply_markup)

async def update_status_message(status_message, text):
    try:
        await status_message.edit_text(text)
    except Exception as e:
        logger.error(f"Failed to update status message: {e}")

@app.on_message(filters.text)
async def handle_message(client: Client, message: Message):
    if message.text.startswith('/'):
        return

    if not message.from_user:
        return

    user_id = message.from_user.id

    # 👑 Bypass all checks for the OWNER
    if user_id != OWNER_ID:
        # Check if user is a member
        is_member = await is_user_member(client, user_id)
        if not is_member:
            join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/jffmain")
            reply_markup = InlineKeyboardMarkup([[join_button]])
            await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.", reply_markup=reply_markup)
            return

        # Token validation
        if not has_valid_token(user_id):
            await message.reply_text(
                "Your token has expired or you haven't generated one yet.\n"
                "Please generate a new token using /start."
            )
            return
    
    url = None
    for word in message.text.split():
        if is_valid_url(word):
            url = word
            break

    if not url:
        await message.reply_text("Please provide a valid Terabox link.")
        return

    encoded_url = urllib.parse.quote(url)
    final_url = f"https://teradlrobot.cheemsbackup.workers.dev/?url={encoded_url}"

    download = aria2.add_uris([final_url], options={
        'continue': 'true',
        'split': '16',  # More parallel download
    })
    status_message = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...🤤")

    start_time = datetime.now()

    while not download.is_complete:
        await asyncio.sleep(5)
        download.update()
        progress = download.progress

        elapsed_time = datetime.now() - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

        status_text = (
            f"📥 <b>{download.name}</b>\n"
            f"⏳ <b>Progress:</b> [{('★' * int(progress / 10))}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
            f"⚡ <b>Speed:</b> {format_size(download.download_speed)}/s | <b>ETA:</b> {download.eta}\n"
            f"🕒 <b>Elapsed:</b> {elapsed_minutes}m {elapsed_seconds}s\n"
            f"📝 <b>File Size:</b> {format_size(download.total_length)}\n"
            f"👤 <b>User:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | ID: {user_id}\n"
            )
        while True:
            try:
                await update_status_message(status_message, status_text)
                break
            except FloodWait as e:
                logger.error(f"Flood wait detected! Sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)

    file_path = download.files[0].path
    caption = (
        f"✨ {download.name}\n"
        f"👤 <b>Lᴇᴀᴄʜᴇᴅ ʙʏ:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>\n"
        f"📥 <b>ᴜsᴇʀ ʟɪɴᴋ:</b> <a href='tg://user?id={user_id}'>tg://user?id={user_id}</a>\n\n"
        f"🚀 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ:</b> <a href='https://t.me/NyxKingx'>NʏxKɪɴɢ❤️🚀</a>"
    )

    last_update_time = time.time()
    UPDATE_INTERVAL = 5

    async def update_status(message, text):
        nonlocal last_update_time
        current_time = time.time()
        if current_time - last_update_time >= UPDATE_INTERVAL:
            try:
                await message.edit_text(text)
                last_update_time = current_time
            except FloodWait as e:
                logger.warning(f"FloodWait: Sleeping for {e.value}s")
                await asyncio.sleep(e.value)
                await update_status(message, text)
            except Exception as e:
                logger.error(f"Error updating status: {e}")

    async def upload_progress(current, total):
        progress = (current / total) * 100
        elapsed_time = datetime.now() - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

        status_text = (
            f"⚡️ <b>Uᴘʟᴏᴀᴅ Sᴛᴀᴛᴜs</b> ⚡️\n\n"
            f"📁 <b>Fɪʟᴇ:</b> <code>{download.name}</code>\n"
            f"📊 <b>Pʀᴏɢʀᴇss:</b> [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
            f"📦 <b>Sɪᴢᴇ:</b> {format_size(current)} / {format_size(total)}\n"
            f"🚀 <b>Sᴛᴀᴛᴜs:</b> Uᴘʟᴏᴀᴅɪɴɢ ᴛᴏ Tᴇʟᴇɢʀᴀᴍ...\n"
            f"🧠 <b>Eɴɢɪɴᴇ:</b> <u>PyroFork v2.2.11</u>\n"
            f"⚙️ <b>Sᴘᴇᴇᴅ:</b> {format_size(current / elapsed_time.seconds if elapsed_time.seconds > 0 else 0)}/s\n"
            f"⏳ <b>ᴛɪᴍᴇ:</b> {elapsed_minutes}m {elapsed_seconds}s ᴇʟᴀᴘsᴇᴅ\n"
            f"🙋 <b>Uꜱᴇʀ:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | <code>{user_id}</code>\n"
        )
        await update_status(status_message, status_text)

    async def split_video_with_ffmpeg(input_path, output_prefix, split_size):
        try:
            original_ext = os.path.splitext(input_path)[1].lower() or '.mp4'
            start_time = datetime.now()
            last_progress_update = time.time()
            
            proc = await asyncio.create_subprocess_exec(
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', input_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            total_duration = float(stdout.decode().strip())
            
            file_size = os.path.getsize(input_path)
            parts = math.ceil(file_size / split_size)
            
            if parts == 1:
                return [input_path]
            
            duration_per_part = total_duration / parts
            split_files = []
            
            for i in range(parts):
                current_time = time.time()
                if current_time - last_progress_update >= UPDATE_INTERVAL:
                    elapsed = datetime.now() - start_time
                    status_text = (
                        f"✂️ <b>Sᴘʟɪᴛᴛɪɴɢ Fɪʟᴇ</b>\n\n"
                        f"📁 <b>Fɪʟᴇ:</b> <code>{os.path.basename(input_path)}</code>\n"
                        f"🧩 <b>Pᴀʀᴛ:</b> {i+1}/{parts}\n"
                        f"⏱️ <b>Eʟᴀᴘꜱᴇᴅ:</b> {elapsed.seconds // 60}m {elapsed.seconds % 60}s"
                    )
                    await update_status(status_message, status_text)
                    last_progress_update = current_time
                
                output_path = f"{output_prefix}.{i+1:03d}{original_ext}"
                cmd = [
                    'xtra', '-y', '-ss', str(i * duration_per_part),
                    '-i', input_path, '-t', str(duration_per_part),
                    '-c', 'copy', '-map', '0',
                    '-avoid_negative_ts', 'make_zero',
                    output_path
                ]
                
                proc = await asyncio.create_subprocess_exec(*cmd)
                await proc.wait()
                split_files.append(output_path)
            
            return split_files
        except Exception as e:
            logger.error(f"Split error: {e}")
            raise

    async def handle_upload():
        file_size = os.path.getsize(file_path)
        
        if file_size > SPLIT_SIZE:
            await update_status(
                status_message,
                f"✂️ Sᴘʟɪᴛᴛɪɴɢ  {download.name} ({format_size(file_size)})"
            )
            
            split_files = await split_video_with_ffmpeg(
                file_path,
                os.path.splitext(file_path)[0],
                SPLIT_SIZE
            )
            
            try:
                for i, part in enumerate(split_files):
                    part_caption = f"{caption}\n\nPart {i+1}/{len(split_files)}"
                    await update_status(
                        status_message,
                        f"📤 <b>Uᴘʟᴏᴀᴅɪɴɢ Pᴀʀᴛ</b> {i+1}/{len(split_files)}\n"
                        f"📁 <b>Fɪʟᴇ:</b> <code>{os.path.basename(part)}</code>"
                        f"📦 <b>Sɪᴢᴇ:</b> {format_size(os.path.getsize(part))}"
                    )
                    
                    if USER_SESSION_STRING:
                        sent = await user.send_video(
                            DUMP_CHAT_ID, part, 
                            caption=part_caption,
                            progress=upload_progress
                        )
                        await app.copy_message(
                            message.chat.id, DUMP_CHAT_ID, sent.id
                        )
                    else:
                        sent = await client.send_video(
                            DUMP_CHAT_ID, part,
                            caption=part_caption,
                            progress=upload_progress
                        )
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption
                        )
                    os.remove(part)
            finally:
                for part in split_files:
                    try: os.remove(part)
                    except: pass
        else:
            await update_status(
                status_message,
                f"📤 Uᴘʟᴏᴀᴅɪɴɢ  {download.name}\n"
                f"Size: {format_size(file_size)}"
            )
            
            if USER_SESSION_STRING:
                sent = await user.send_video(
                    DUMP_CHAT_ID, file_path,
                    caption=caption,
                    progress=upload_progress
                )
                await app.copy_message(
                    message.chat.id, DUMP_CHAT_ID, sent.id
                )
            else:
                sent = await client.send_video(
                    DUMP_CHAT_ID, file_path,
                    caption=caption,
                    progress=upload_progress
                )
                await client.send_video(
                    message.chat.id, sent.video.file_id,
                    caption=caption
                )
        if os.path.exists(file_path):
            os.remove(file_path)

    start_time = datetime.now()
    await handle_upload()

    try:
        await status_message.delete()
        await message.delete()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        



async def start_user_client():
    if user:
        await user.start()
        logger.info("User client started.")

def run_user():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_user_client())

if __name__ == "__main__":
    if user:
        logger.info("Starting both bot and user clients...")
        user_thread = threading.Thread(target=run_user)
        user_thread.start()

    logger.info("Starting bot client...")
    logger.info("Bot client Started...")
    # print(f"Your session string: {app.session_string}")
    app.run()