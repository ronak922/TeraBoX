from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
import asyncio  # For asyncio.TimeoutError
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
# Add this to your imports at the top
from pyrogram.errors import FloodWait, MessageDeleteForbidden, MessageNotModified

from pyrogram import Client, filters, idle
from helper import *
from pymongo import MongoClient
from pyrogram import enums
import os
import ffmpeg
# from pymetadata import extractMetadata, createParser
# from metadata import extractMetadata, createParser
import json
import aiohttp
import time
import threading
import uuid
import urllib.parse
from urllib.parse import urlparse
import requests

OWNER_ID = 7663297585
ADMINS = [OWNER_ID]  # Add more admin IDs as needed

logger = logging.getLogger(__name__)


# Headers setup
my_headers_raw = os.getenv("MY_HEADERS", "{}")
try:
    my_headers = json.loads(my_headers_raw)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON for MY_HEADERS: {e}")
    my_headers = {}

# Around line 40-50, update the headers
my_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.terabox.com/"
}


# Cookie and Headers (MY_COOKIE and MY_HEADERS must be in JSON string format)
cookie_string = os.getenv("MY_COOKIE", "browserid=avLKUlrztrL0C84414VnnfWxLrQ1vJblh4m8WCMxL7TZWIMpPdno52qQb27fk957PE6sUd5VZJ1ATlUe; lang=en; TSID=DLpCxYPseu0EL2J5S2Hf36yFszAufv2G; __bid_n=1964760716d8bd55e14207; g_state={\"i_l\":0}; ndus=Yd6IpupteHuieos8muZScO1E7xfuRT_csD6LBOF3; ndut_fmt=06E6B9E2AC0209A19E5F21774DDD4A03B26FC67DA9EB68D3E790C416E35F3957; csrfToken=XMXR2_q-9p3ckuuFAqeZId9d")

# Safe cookie parsing with additional logging for invalid cookies
if cookie_string:
    try:
        my_cookie = dict(item.split("=", 1) for item in cookie_string.split("; ") if "=" in item)
    except Exception as e:
        logger.error(f"Error parsing cookie string: {e}")
        my_cookie = {}
else:
    logger.warning("MY_COOKIE not set!")
    my_cookie = {}



load_dotenv('config.env', override=True)
logging.basicConfig(
    level=logging.INFO,  
    format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s - %(filename)s:%(lineno)d"
)

logger = logging.getLogger(__name__)

logging.getLogger("pyrogram.session").setLevel(logging.ERROR)
logging.getLogger("pyrogram.connection").setLevel(logging.ERROR)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.ERROR)

# from aria2p import Aria2API, Aria2Client

aria2 = Aria2API(
    Aria2Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

# SUPER BOOSTED SETTINGS
options = {
    # Connection Boost
    "max-connection-per-server": "16",     # Increased from 16 to 32
    "split": "128",                        # Increased from 128 to 256
    "min-split-size": "1M",              # Decreased from 1M to 512K for more parallel downloads
    "piece-length": "1M",                  # Keep as is

    # Concurrent Downloads
    "max-concurrent-downloads": "10",      # Increased from 5 to 10

    # Retry Settings
    "max-tries": "20",                     # Keep as is
    "retry-wait": "1",                     # Decreased from 2 to 1 for faster retry
    "connect-timeout": "5",                # Keep as is
    "timeout": "10",                       # Keep as is

    # Performance
    "disk-cache": "256M",                  # Increased from 128M to 256M
    "file-allocation": "none",             # Keep as is
    "async-dns": "true",                   # Keep as is
    "enable-http-keep-alive": "true",      # Keep as is
    "enable-http-pipelining": "true",      # Keep as is
    
    # Additional optimizations
    "enable-mmap": "true",                 # New: Use memory mapping for files
    "optimize-concurrent-downloads": "true", # New: Optimize concurrent downloads
    "http-accept-gzip": "true",            # New: Accept gzip compression
    "content-disposition-default-utf8": "true", # New: Handle UTF-8 filenames properly
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", # New: Specific user-agent

    # Continue/Overwrite
    "continue": "true",                    # Keep as is
    "allow-overwrite": "true",             # Keep as is

    # No Speed Limits
    "max-download-limit": "0",             # Keep as is
    "min-download-limit": "0",             # Keep as is

    # Download location
    "dir": "/tmp/aria2_downloads",         # Keep as is

    # Optional BT Settings (even if not used)
    "bt-max-peers": "0",                   # Keep as is
    "bt-request-peer-speed-limit": "10M",  # Keep as is
    "seed-ratio": "0.0",                   # Keep as is
}

# Apply options
# aria2.set_global_options(options)



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

DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '-1002586886642')
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
    try:
        user = Client(
            "user_session", 
            api_id=API_ID, 
            api_hash=API_HASH, 
            session_string=USER_SESSION_STRING,
            no_updates=True  # Add this to avoid update handling
        )
        SPLIT_SIZE = 4241280205
    except Exception as e:
        logger.error(f"Error initializing user client: {e}")
        user = None
        USER_SESSION_STRING = None
        SPLIT_SIZE = 2093796556
else:
    user = None
    SPLIT_SIZE = 2093796556


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

async def full_userbase():
    # Retrieve all documents from the user_requests collection
    user_docs = collection.find()  # MongoDB find() returns a cursor for all documents in the collection
    
    # Extract user IDs from the documents
    user_ids = [doc['_id'] for doc in user_docs]  # Assuming '_id' is the user ID field
    
    return user_ids

from pyrogram.errors import UserIsBlocked, FloodWait, InputUserDeactivated

from pymongo import ReturnDocument

# Function to remove a user from the database based on their chat_id
async def del_user(chat_id):
    try:
        # Delete the user from the MongoDB collection
        result = collection.find_one_and_delete({"_id": chat_id}, return_document=ReturnDocument.AFTER)
        
        if result:
            print(f"User {chat_id} removed from the database.")
        else:
            print(f"User {chat_id} not found in the database.")
    except Exception as e:
        print(f"Error deleting user {chat_id}: {e}")


from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

@app.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Client, message: Message):
    if message.reply_to_message:
        # Inform the admin that the broadcast will be sent to all users
        await message.reply(
            "Broadcast will be sent to ALL users.\n\n"
            "Broadcast message is being processed."
        )
        
        # Get the broadcast message
        broadcast_msg = message.reply_to_message
        
        # Get the list of all users (from the database)
        query = await full_userbase()  # This function fetches all user IDs from the database
        
        # Perform broadcast
        total = len(query)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜜɪɴɢ....</i>")
        
        for index, chat_id in enumerate(query):
            try:
                # Send message
                await broadcast_msg.copy(chat_id=chat_id)
                successful += 1
            except FloodWait as e:
                # Correctly use e.value instead of e.time
                await asyncio.sleep(e.value)  # Correct way to access the wait time
                try:
                    await broadcast_msg.copy(chat_id=chat_id)
                    successful += 1
                except Exception as inner_e:
                    print(f"Failed to send message to {chat_id}: {inner_e}")  # Log the specific error
                    unsuccessful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                print(f"Unexpected error for {chat_id}: {e}")  # Log unexpected errors
                unsuccessful += 1
            
            # Update loading bar
            progress = (index + 1) / total
            bar_length = 20  # Length of the loading bar
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            await pls_wait.edit(f"<b>Broadcast Progress:</b>\n{bar} {progress:.1%}")

        # Generate status message
        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        await pls_wait.edit(status)
    
    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
    
    return


REPLY_ERROR = """Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ sᴘᴀᴄᴇs."""

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

TOKEN_SYSTEM_ENABLED = os.environ.get('TOKEN_SYSTEM_ENABLED', 'True').lower() == 'true'
import sys
@app.on_message(filters.command("restart"))
async def restart_command(client: Client, message: Message):
    # Only allow the owner to restart the bot
    if message.from_user.id != OWNER_ID:
        await message.reply_text("⚠️ This command is only available to the bot owner.")
        return
    
    await message.reply_text("🔄 Restarting bot...")

    # Restart the bot using system command (works on Linux/Unix systems)
    # If you're on a Windows system, you can use a different method, like calling the script directly.

    os.execv(sys.executable, ['python'] + sys.argv)

async def get_settings():
    """Get bot settings from database"""
    settings_col = db.get_collection("settings")
    settings_doc = settings_col.find_one({"_id": "bot_settings"})

    if not settings_doc:
        # Create default settings if none exist
        default_settings = {
            "_id": "bot_settings",
            "FORCE_SUB_CHANNELS": [FSUB_ID],  # Use your existing FSUB_ID
            "REQUEST_SUB_CHANNELS": [-1002631104533],  # Default approval channel
            "TOKEN_SYSTEM_ENABLED": True
        }
        settings_col.insert_one(default_settings)
        global TOKEN_SYSTEM_ENABLED
        TOKEN_SYSTEM_ENABLED = default_settings["TOKEN_SYSTEM_ENABLED"]
        return default_settings

    # Ensure REQUEST_SUB_CHANNELS exists
    if "REQUEST_SUB_CHANNELS" not in settings_doc or not settings_doc["REQUEST_SUB_CHANNELS"]:
        settings_col.update_one(
            {"_id": "bot_settings"},
            {"$set": {"REQUEST_SUB_CHANNELS": [-1002631104533]}}
        )
        settings_doc["REQUEST_SUB_CHANNELS"] = [-1002631104533]

    # Ensure TOKEN_SYSTEM_ENABLED exists
    if "TOKEN_SYSTEM_ENABLED" not in settings_doc:
        settings_col.update_one(
            {"_id": "bot_settings"},
            {"$set": {"TOKEN_SYSTEM_ENABLED": True}}
        )
        settings_doc["TOKEN_SYSTEM_ENABLED"] = True

    # Update global variable
    
    # global TOKEN_SYSTEM_ENABLED
    TOKEN_SYSTEM_ENABLED = settings_doc.get("TOKEN_SYSTEM_ENABLED", True)

    return settings_doc



async def set_setting(key, value):
    """Update a specific setting in the database"""
    result = db.get_collection("settings").update_one(
        {"_id": "bot_settings"},
        {"$set": {key: value}},
        upsert=True
    )
    return result.modified_count > 0

# Add the callback handlers
@app.on_callback_query(filters.regex("^manage_forcesub$"))
async def manage_forcesub_callback(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴅᴍɪɴ ✖", show_alert=True)
        return
    
    settings = await get_settings()
    normal_channels = settings.get("FORCE_SUB_CHANNELS", [])
    request_channels = settings.get("REQUEST_SUB_CHANNELS", [])
    
    text = "📢 **Fᴏʀᴄᴇ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Sᴇᴛᴛɪɴɢs**\n\n"
    
    if normal_channels:
        text += "🔹 **Normal Join Channels:**\n"
        for ch in normal_channels:
            try:
                chat = await client.get_chat(ch)
                link = f"https://t.me/{chat.username}" if chat.username else await client.export_chat_invite_link(ch)
                text += f"• [{chat.title}]({link})\n"
            except Exception as e:
                text += f"• `{ch}` (❌ Failed to fetch)\n"
    else:
        text += "❌ No normal join channels.\n"
    
    text += "\n"
    
    if request_channels:
        text += "🔸 **Request Join Channels:**\n"
        for ch in request_channels:
            try:
                chat = await client.get_chat(ch)
                link = chat.invite_link or await client.export_chat_invite_link(ch)
                text += f"• [{chat.title}]({link}) (Request Join)\n"
            except Exception as e:
                text += f"• `{ch}` (❌ Failed to fetch)\n"
    else:
        text += "❌ No request join channels.\n"
    
    text += "\n⚠️ **Pʟᴇᴀsᴇ Rᴇsᴛᴀʀᴛ Tʜᴇ Bᴏᴛ Aғᴛᴇʀ Uᴘᴅᴀᴛɪɴɢ Cʜᴀɴɴᴇʟs!**"
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Nᴏʀᴍᴀʟ Cʜᴀɴɴᴇʟ", callback_data="add_normal_channel"),
            InlineKeyboardButton("➕ Rᴇǫᴜᴇsᴛ Cʜᴀɴɴᴇʟ", callback_data="add_request_channel")
        ],
        [
            InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Nᴏʀᴍᴀʟ", callback_data="remove_normal_channel"),
            InlineKeyboardButton("➖ Rᴇᴍᴏᴠᴇ Rᴇǫᴜᴇsᴛ", callback_data="remove_request_channel")
        ],
        [InlineKeyboardButton("◀️ Bᴀᴄᴋ", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("^add_normal_channel$"))
async def add_normal_channel(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴅᴍɪɴ ✖", show_alert=True)
    
    await callback_query.message.edit_text("📥 **Send the Normal Channel Username or ID:**")
    await callback_query.answer()
    
    try:
        response = await client.listen(callback_query.from_user.id, timeout=60)
        channel = response.text.strip()
        
        if channel.replace("-", "").isdigit():
            channel = int(channel)
        
        settings = await get_settings()
        normal_channels = settings.get("FORCE_SUB_CHANNELS", [])
        
        if channel in normal_channels:
            return await client.send_message(callback_query.from_user.id, "⚠️ Channel already in the list.")
        
        normal_channels.append(channel)
        await set_setting("FORCE_SUB_CHANNELS", normal_channels)
        await client.send_message(callback_query.from_user.id, f"✅ **Added `{channel}` to normal channels.**")
    except asyncio.TimeoutError:  # Use asyncio.TimeoutError instead
        await client.send_message(callback_query.from_user.id, "❌ Timeout. No input received.")

@app.on_callback_query(filters.regex("^add_request_channel$"))
async def add_request_channel(client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴅᴍɪɴ ✖", show_alert=True)
    
    await callback_query.message.edit_text("🔐 **Send the Request Join Channel ID (starts with -100):**")
    await callback_query.answer()
    
    try:
        response = await client.listen(callback_query.from_user.id, timeout=60)
        channel = response.text.strip()
        
        if channel.replace("-", "").isdigit():
            channel = int(channel)
        
        settings = await get_settings()
        request_channels = settings.get("REQUEST_SUB_CHANNELS", [])
        
        if channel in request_channels:
            return await client.send_message(callback_query.from_user.id, "⚠️ Already in the request list.")
        
        request_channels.append(channel)
        await set_setting("REQUEST_SUB_CHANNELS", request_channels)
        await client.send_message(callback_query.from_user.id, f"✅ **Added `{channel}` to request join channels.**")
    except asyncio.TimeoutError:
        await client.send_message(callback_query.from_user.id, "❌ Timeout. No input received.")


# 🔧 Channel Remove Handler
@app.on_callback_query(filters.regex("^(remove_normal_channel|remove_request_channel)$"))
async def remove_channel_handler(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        return await callback_query.answer("Nᴏᴛ Aᴅᴍɪɴ ✖", show_alert=True)
    
    setting_type = "FORCE_SUB_CHANNELS" if "normal" in callback_query.data else "REQUEST_SUB_CHANNELS"
    label = "Normal" if "normal" in callback_query.data else "Request"
    
    settings = await get_settings()
    channels = settings.get(setting_type, [])
    
    if not channels:
        return await callback_query.message.edit_text(f"⚠️ No {label} channels to remove.")
    
    buttons = [
        [InlineKeyboardButton(f"❌ {ch}", callback_data=f"confirm_remove_{setting_type}_{i}")]
        for i, ch in enumerate(channels)
    ]
    buttons.append([InlineKeyboardButton("◀️ Back", callback_data="manage_forcesub")])
    
    await callback_query.message.edit_text(
        f"➖ **Select a {label} channel to remove:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex("^confirm_remove_(FORCE_SUB_CHANNELS|REQUEST_SUB_CHANNELS)_\\d+$"))
async def confirm_remove_channel(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        return await callback_query.answer("Nᴏᴛ Aᴅᴍɪɴ ✖", show_alert=True)
    
    parts = callback_query.data.split("_")
    setting_type = "_".join(parts[2:-1])
    index = int(parts[-1])
    
    settings = await get_settings()
    channels = settings.get(setting_type, [])
    
    try:
        removed = channels.pop(index)
        await set_setting(setting_type, channels)
        await callback_query.message.edit_text(f"✅ Removed `{removed}` from channel list.")
    except IndexError:
        await callback_query.message.edit_text("❌ Invalid index.")
    # Show updated menu or confirmation (optional)

# Add a back to main menu handler
@app.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main_menu(client, callback_query: CallbackQuery):
    # Get current token system status
    token_status = "🔴 Disable" if TOKEN_SYSTEM_ENABLED else "🟢 Enable"
    
    # Create your main admin menu here
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Manage Force Sub", callback_data="manage_forcesub")],
        [InlineKeyboardButton("📊 Bot Stats", callback_data="bot_stats")],
        [InlineKeyboardButton(f"{token_status} Tᴏᴋᴇɴ Sʏsᴛᴇᴍ", callback_data="toggle_token_system")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot")]
    ])
    
    await callback_query.message.edit_text(
        "⚙️ **Admin Control Panel**\n\nSelect an option from the menu below:",
        reply_markup=keyboard
    )

async def store_join_request(user_id, channel_id):
    """Store a join request in the database"""
    collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"pending_requests": channel_id}},
        upsert=True
    )

async def has_pending_request(user_id, channel_id):
    """Check if user has a pending join request for a channel"""
    user_data = collection.find_one(
        {"user_id": user_id, "pending_requests": channel_id}
    )
    return user_data is not None

@app.on_chat_join_request()
async def join_reqs(client, message: ChatJoinRequest):
    """Handle join requests for channels that require approval"""
    settings = await get_settings()
    REQUEST_SUB_CHANNELS = settings.get("REQUEST_SUB_CHANNELS", [])
    
    # Only process requests for our channels
    if message.chat.id not in REQUEST_SUB_CHANNELS:
        return
    
    user_id = message.from_user.id
    channel_id = message.chat.id
    
    # Store the join request in the database
    await store_join_request(user_id, channel_id)
    logger.info(f"📝 Stored join request from user {user_id} for channel {channel_id}")


@app.on_chat_join_request()
async def join_reqs(client, message: ChatJoinRequest):
    """Handle join requests for channels that require approval"""
    settings = await get_settings()
    REQUEST_SUB_CHANNELS = settings.get("REQUEST_SUB_CHANNELS", [])
    
    # Only process requests for our channels
    if message.chat.id not in REQUEST_SUB_CHANNELS:
        return
    
    user_id = message.from_user.id
    channel_id = message.chat.id
    
    # Store the join request in the database
    await store_join_request(user_id, channel_id)
    logger.info(f"📝 Stored join request from user {user_id} for channel {channel_id}")

@app.on_message(filters.command("admin") & filters.private)
async def admin_panel(client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in ADMINS:
        await message.reply_text("⚠️ You are not authorized to use admin commands.")
        return
    
    # Get current token system status
    token_status = "🔴 Disable" if TOKEN_SYSTEM_ENABLED else "🟢 Enable"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Manage Force Sub", callback_data="manage_forcesub")],
        [InlineKeyboardButton("📊 Bot Stats", callback_data="bot_stats")],
        [InlineKeyboardButton(f"{token_status} Tᴏᴋᴇɴ Sʏsᴛᴇᴍ", callback_data="toggle_token_system")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot")]
    ])
    
    await message.reply_text(
        "⚙️ **Admin Control Panel**\n\nSelect an option from the menu below:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("^toggle_token_system$"))
async def toggle_token_system(client, callback_query: CallbackQuery):
    global TOKEN_SYSTEM_ENABLED
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("You are not authorized to use this function.", show_alert=True)
        return
    
    global TOKEN_SYSTEM_ENABLED
    # Toggle the token system
    TOKEN_SYSTEM_ENABLED = not TOKEN_SYSTEM_ENABLED
    
    # Update the setting in the database
    await set_setting("TOKEN_SYSTEM_ENABLED", TOKEN_SYSTEM_ENABLED)
    
    status = "enabled" if TOKEN_SYSTEM_ENABLED else "disabled"
    await callback_query.answer(f"Token system {status} successfully!", show_alert=True)
    
    # Update the button text
    token_status = "🔴 Disable" if TOKEN_SYSTEM_ENABLED else "🟢 Enable"
    
    # Recreate the keyboard with updated button text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Manage Force Sub", callback_data="manage_forcesub")],
        [InlineKeyboardButton("📊 Bot Stats", callback_data="bot_stats")],
        [InlineKeyboardButton(f"{token_status} Token System", callback_data="toggle_token_system")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot")]
    ])
    
    await callback_query.message.edit_text(
        "⚙️ **Admin Control Panel**\n\nSelect an option from the menu below:",
        reply_markup=keyboard
    )

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
        f"📊 <b>BOT STATS</b> 📊\n"
        f"💻 <b>System:</b> CPU: {cpu_usage}% | RAM: {ram_usage}% | Disk: {disk_usage}%\n"
        f"⏳ <b>Uptime:</b> {days}d {hours}h {minutes}m {seconds}s\n"
        f"👤 <b>Users:</b> {user_count} | 🔑 Active Tokens: {active_tokens}\n"
        f"📈 <b>Downloads:</b> {download_count} | Total Downloaded: {format_size(total_download_size)}\n"
        f"🔌 <b>DB Connection:</b> {'✅ Connected' if client else '❌ Disconnected'}\n"
        f"📦 <b>DB:</b> {DATABASE_NAME} - {COLLECTION_NAME}\n"
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
    
    user_id = message.from_user.id
    
    # Skip subscription checks for the owner
    if user_id != OWNER_ID:
        settings = await get_settings()
        FORCE_SUB_CHANNELS = settings.get("FORCE_SUB_CHANNELS", [])
        REQUEST_SUB_CHANNELS = settings.get("REQUEST_SUB_CHANNELS", [])
        
        # Initialize variables to track which channels the user needs to join
        force_channels_to_join = []
        request_channels_to_join = []
        
        # Check force sub channels
        for channel in FORCE_SUB_CHANNELS:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    force_channels_to_join.append(channel)
            except Exception as e:
                logger.error(f"Error checking force sub: {e}")
                force_channels_to_join.append(channel)
        
        # Check request channels
        for channel in REQUEST_SUB_CHANNELS:
            try:
                # Skip if user already has a pending request
                if await has_pending_request(user_id, channel):
                    continue
                
                # Check if user is a member
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    request_channels_to_join.append(channel)
            except Exception as e:
                logger.error(f"Error checking request sub: {e}")
                request_channels_to_join.append(channel)
        
        # If user needs to join channels, show them the subscription message
        if force_channels_to_join or request_channels_to_join:
            # User needs to join channels - prepare buttons
            force_text = (
                f"⚠️ Hᴇʏ, {message.from_user.mention} 🚀\n\n"
                "Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ. Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ, ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ.. !\n\n"
                "❗️Fᴀᴄɪɴɢ ᴘʀᴏʙʟᴇᴍs, ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
            )
            buttons = []
            temp_buttons = []
            
            # Add FORCE-JOIN CHANNELS buttons
            for channel in force_channels_to_join:
                try:
                    chat = await client.get_chat(channel)
                    invite_link = await client.export_chat_invite_link(channel)
                    btn = InlineKeyboardButton(f"👾 {chat.title}", url=invite_link)
                    temp_buttons.append(btn)
                    if len(temp_buttons) == 2:
                        buttons.append(temp_buttons)
                        temp_buttons = []
                except Exception as e:
                    logger.error(f"Error creating force join button for {channel}: {e}")
                    continue
            
            # Add REQUEST-JOIN CHANNELS buttons
            for channel in request_channels_to_join:
                try:
                    chat = await client.get_chat(channel)
                    invite_link = await client.create_chat_invite_link(channel, creates_join_request=True)
                    btn = InlineKeyboardButton(f"⚡ {chat.title}", url=invite_link.invite_link)
                    temp_buttons.append(btn)
                    if len(temp_buttons) == 2:
                        buttons.append(temp_buttons)
                        temp_buttons = []
                except Exception as e:
                    logger.error(f"Error creating request join button for {channel}: {e}")
                    continue
            
            # Add leftovers
            if temp_buttons:
                buttons.append(temp_buttons)
            
            # Add Try Again button
            buttons.append([
                InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", url=f"https://t.me/{app.me.username}?start=")
            ])
            
            # Send the message with buttons
            if buttons:
                try:
                    await message.reply_photo(
                        photo=image_url,
                        caption=force_text,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        quote=True
                    )
                    logger.info(f"✅ Sent force subscription message to user {user_id}")
                    return
                except Exception as e:
                    logger.error(f"❌ Error sending force subscription message: {e}")
                    # Fallback to text message
                    try:
                        await message.reply(
                            force_text,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            quote=True
                        )
                        return
                    except Exception as e:
                        logger.error(f"❌ Error sending fallback message: {e}")

    # Continue with the original start command logic if user has joined all channels or is the owner
    if len(message.command) > 1 and len(message.command[1]) == 36 and TOKEN_SYSTEM_ENABLED :
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
            final_msg = (f"<b>Sᴇɴᴅ Tᴇʀᴀʙᴏx Lɪɴᴋ Tᴏ Dᴏᴡɴʟᴏᴀᴅ Vɪᴅᴇᴏ</b>")

            new_btn = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Dɪʀᴇᴄᴛ Vɪᴅᴇᴏ Cʜᴀɴɴᴇʟs 🚀", url="https://t.me/NyxKingXLinks")]
                ])

            # 👑 Bypass shortening for OWNER
            if user_id == OWNER_ID:
                short_url = long_url
            else:
                short_url = shorten_url(long_url)

            if short_url and TOKEN_SYSTEM_ENABLED :
                reply_markup2 = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Vᴇʀɪғʏ Tᴏᴋᴇɴ 🚀", url=short_url)],
                    [join_button, developer_button],
                    [InlineKeyboardButton("Dɪʀᴇᴄᴛ Vɪᴅᴇᴏ Cʜᴀɴɴᴇʟs 🚀", url="https://t.me/NyxKingXLinks")],
                ])

                
                caption = (
                    "🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ.\n\n"
                    "Pʟᴇᴀsᴇ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ Tᴏᴋᴇɴ, ᴡʜɪᴄʜ ᴡɪʟʟ ʙᴇ ᴠᴀʟɪᴅ ғᴏʀ 12Hʀs"
                )

                await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=caption, reply_markup=reply_markup2)
            elif not TOKEN_SYSTEM_ENABLED:
                await client.send_sticker(
                    chat_id=message.chat.id,
                    sticker="CAACAgIAAxkBAAEBN-1oAl31NneuKt91GqgBGm37_YIO5AACZQ0AAulzQEj7mSnMOJpDMTYE"
                )
                await client.send_message(
                    chat_id=message.chat.id,
                    text=final_msg,
                    reply_markup=new_btn,
                )
        else:
            await client.send_photo(chat_id=message.chat.id, photo=image_url, caption=final_msg, reply_markup=reply_markup)


# Find the update_status_message function (around line 1033)
async def update_status_message(status_message, text, reply_markup=None):
    try:
        # Add this check to see if the message content is different
        if hasattr(status_message, 'text') and status_message.text == text:
            # Content is the same, no need to update
            return
            
        await status_message.edit_text(text, reply_markup=reply_markup)
    except MessageNotModified:
        # Specifically catch the MessageNotModified error and ignore it
        pass
    except Exception as e:
        logger.error(f"Failed to update status message: {e}")




# Add this callback handler to handle cancel button clicks
@app.on_callback_query(filters.regex(r'^cancel_(.+)$'))
async def cancel_download_callback(client, callback_query):
    # Extract the download GID from the callback data
    download_gid = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    # Check if the download exists and belongs to the user who clicked cancel
    if (download_gid in app.active_downloads and 
            app.active_downloads[download_gid]['user_id'] == user_id):
        
        # Mark the download as cancelled
        app.active_downloads[download_gid]['cancelled'] = True
        
        await callback_query.answer("Cancelling download... Please wait.")
    else:
        # Either download doesn't exist or user is not authorized
        await callback_query.answer("Cannot cancel this download.", show_alert=True)

async def find_between(string, start, end):
    start_index = string.find(start) + len(start)
    end_index = string.find(end, start_index)
    return string[start_index:end_index]

import aiohttp
import urllib.parse

async def find_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except IndexError:
        return None

async def fetch_download_link_async(url):
    encoded_url = urllib.parse.quote(url)
    api_url = f"https://terabox-pika.vercel.app/?url={encoded_url}"

    async with aiohttp.ClientSession(cookies=my_cookie) as my_session:
        my_session.headers.update(my_headers)

        # First fallback: fetch the general link
        try:
            async with my_session.get(api_url) as response:
                response.raise_for_status()
                response_data = await response.json()

            link = response_data.get("link")
            dlink = response_data.get("dlink")

            # Test direct_link by checking if it returns error 31362
            if dlink:
                async with my_session.head(dlink) as check_response:
                    if check_response.status == 200:
                        return dlink
                    else:
                        print("Direct link fallback failed, using regular link if present.")
            
            if link:
                return link

        except Exception as e:
            print(f"API fallback failed: {e}")

        # Final fallback: Manual page scraping
        try:
            async with my_session.get(url) as response:
                response.raise_for_status()
                response_data = await response.text()

            js_token = await find_between(response_data, 'fn%28%22', '%22%29')
            log_id = await find_between(response_data, 'dp-logid=', '&')

            if not js_token or not log_id:
                print("Required tokens not found.")
                return None

            request_url = str(response.url)
            surl = request_url.split('surl=')[1]

            params = {
                'app_id': '250528',
                'web': '1',
                'channel': 'dubox',
                'clienttype': '0',
                'jsToken': js_token,
                'dplogid': log_id,
                'page': '1',
                'num': '20',
                'order': 'time',
                'desc': '1',
                'site_referer': request_url,
                'shorturl': surl,
                'root': '1'
            }

            async with my_session.get('https://www.1024tera.com/share/list', params=params) as response2:
                response_data2 = await response2.json()
                if 'list' not in response_data2:
                    print("No list found.")
                    return None

                if response_data2['list'][0]['isdir'] == "1":
                    params.update({
                        'dir': response_data2['list'][0]['path'],
                        'order': 'asc',
                        'by': 'name',
                        'dplogid': log_id
                    })
                    params.pop('desc')
                    params.pop('root')

                    async with my_session.get('https://www.1024tera.com/share/list', params=params) as response3:
                        response_data3 = await response3.json()
                        if 'list' not in response_data3:
                            return None
                        return response_data3['list']

                return response_data2['list']

        except Exception as e:
            print(f"Final fallback failed: {e}")
            return None



# To call the function and test the code:
# asyncio.run(fetch_download_link_async('your_url_here'))

async def format_message(link):
    """
    Format the link data into a readable message.
    """
    # Example format, adjust based on the structure of `link`
    title = link.get('title', 'No Title')  # Assuming each link has a 'title'
    dlink = link.get('dlink', '')  # The actual download link
    size = link.get('size', 'Unknown size')  # Assuming the size is available

    return f"🔗 <b>{title}</b>\n📝 Size: {size}\n[Download Here]({dlink})"


import re
def extract_links(text):
    pattern = r'(https?://[^\s]+)'
    return re.findall(pattern, text)

def truncate_filename(filename, max_length=40):
    """
    Truncate filename if it's too long and replace 'getnewlink.com' with 'NyxKingX'.
    """
    # Replace 'getnewlink.com' with 'NyxKingX'
    if 'getnewlink.com' in filename:
        filename = filename.replace('getnewlink.com', '@NyxKingX')
    
    # Truncate if too long
    if len(filename) <= max_length:
        return filename
    
    # Keep the file extension
    name, ext = os.path.splitext(filename)
    truncated = name[:max_length-5] + "..." + ext
    return truncated



@app.on_message(filters.text)
async def handle_message(client: Client, message: Message):
    if message.text.startswith('/'):
        return

    if not message.from_user:
        return
    
    links = extract_links(message.text.lower())

    valid_links = [link for link in links if any(domain in link for domain in VALID_DOMAINS)]
    if not valid_links:
        return

    user_id = message.from_user.id

    # 👑 Bypass all checks for the OWNER
    if user_id != OWNER_ID:
        settings = await get_settings()
        image_url = "https://i.ibb.co/dsXGtrGt/anime-girl-lollipop-2k-wallpaper-uhdpaper-com-375-5-d.jpg"
        FORCE_SUB_CHANNELS = settings.get("FORCE_SUB_CHANNELS", [])
        REQUEST_SUB_CHANNELS = settings.get("REQUEST_SUB_CHANNELS", [])
        
        # Initialize variables to track which channels the user needs to join
        force_channels_to_join = []
        request_channels_to_join = []
        
        # Check force sub channels
        for channel in FORCE_SUB_CHANNELS:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    force_channels_to_join.append(channel)
            except Exception as e:
                logger.error(f"Error checking force sub: {e}")
                force_channels_to_join.append(channel)
        
        # Check request channels
        for channel in REQUEST_SUB_CHANNELS:
            try:
                # Skip if user already has a pending request
                if await has_pending_request(user_id, channel):
                    continue
                
                # Check if user is a member
                member = await client.get_chat_member(channel, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    request_channels_to_join.append(channel)
            except Exception as e:
                logger.error(f"Error checking request sub: {e}")
                request_channels_to_join.append(channel)
        
        # If user needs to join channels, show them the subscription message
        if force_channels_to_join or request_channels_to_join:
            # User needs to join channels - prepare buttons
            force_text = (
                f"⚠️ Hᴇʏ, {message.from_user.mention} 🚀\n\n"
                "Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ. Pʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ, ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ.. !\n\n"
                "❗️Fᴀᴄɪɴɢ ᴘʀᴏʙʟᴇᴍs, ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ."
            )
            buttons = []
            temp_buttons = []
            
            # Add FORCE-JOIN CHANNELS buttons
            for channel in force_channels_to_join:
                try:
                    chat = await client.get_chat(channel)
                    invite_link = await client.export_chat_invite_link(channel)
                    btn = InlineKeyboardButton(f"👾 {chat.title}", url=invite_link)
                    temp_buttons.append(btn)
                    if len(temp_buttons) == 2:
                        buttons.append(temp_buttons)
                        temp_buttons = []
                except Exception as e:
                    logger.error(f"Error creating force join button for {channel}: {e}")
                    continue
            
            # Add REQUEST-JOIN CHANNELS buttons
            for channel in request_channels_to_join:
                try:
                    chat = await client.get_chat(channel)
                    invite_link = await client.create_chat_invite_link(channel, creates_join_request=True)
                    btn = InlineKeyboardButton(f"⚡ {chat.title}", url=invite_link.invite_link)
                    temp_buttons.append(btn)
                    if len(temp_buttons) == 2:
                        buttons.append(temp_buttons)
                        temp_buttons = []
                except Exception as e:
                    logger.error(f"Error creating request join button for {channel}: {e}")
                    continue
            
            # Add leftovers
            if temp_buttons:
                buttons.append(temp_buttons)
            
            # Add Try Again button
            buttons.append([
                InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", url=f"https://t.me/{app.me.username}?start=")
            ])
            
            # Send the message with buttons
            if buttons:
                try:
                    await message.reply_photo(
                        photo=image_url,
                        caption=force_text,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        quote=True
                    )
                    logger.info(f"✅ Sent force subscription message to user {user_id}")
                    return
                except Exception as e:
                    logger.error(f"❌ Error sending force subscription message: {e}")
                    # Fallback to text message
                    try:
                        await message.reply(
                            force_text,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            quote=True
                        )
                        return
                    except Exception as e:
                        logger.error(f"❌ Error sending fallback message: {e}")
            return

        # Token validation
        if TOKEN_SYSTEM_ENABLED and not has_valid_token(user_id):
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
        await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ Tᴇʀᴀʙᴏx ʟɪɴᴋ.")
        return
    

    sticker_msg = await message.reply_sticker("CAACAgIAAxkBAAEBOPtoBJnc2s0i96Z6aFCJW-ZVqFPeyAACFh4AAuzxOUkNYHq7o3u0ODYE")
    await asyncio.sleep(1)
    await sticker_msg.delete()
    status_message = await message.reply_text(
        f"<b>Pʀᴏᴄᴇssɪɴɢ Yᴏᴜʀ Lɪɴᴋ Pʟᴇᴀsᴇ Wᴀɪᴛ...</b>",
    )
    
    start_time = time.time()  # Start time to measure how long the process takes
    link_data = await fetch_download_link_async(message.text)

    print("Link Data:", link_data)

    if not link_data:
        await message.reply_text(f"⚠️ Error: {link_data}")
        return
    
    if isinstance(link_data, str):
        direct_link = link_data
    else:
        if isinstance(link_data, list):
            first_item = link_data[0]
            direct_link = first_item.get('dlink')
        else:
            await message.reply_text("⚠️ Unexpected data format received.")
            return
    if not direct_link:
        await message.reply_text("⚠️ Error: Direct link not found.")
        return
        

    
    end_time = time.time()
    time_taken = end_time - start_time

    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    # link_message = "\n\n".join([await format_message(link) for link in link_data])
    # download_message = (
    #     f"🔗 <b>Link Bypassed!</b>\n\n{link_message}\n\n"
    #     f"<b>Time Taken</b>: {time_taken:.2f} seconds"
    # )
    # await message.reply_text(download_message)

    # direct_url = link_data  # Assuming the first item has the 'dlink' field

    # encoded_url = urllib.parse.quote(final_url)

    download = aria2.add_uris(
        [direct_link],
        options={
            'continue': 'true',
            'split': '128',  
            'max-connection-per-server': '16',
            'min-split-size': '1M',  # Added this line
            'optimize-concurrent-downloads': 'true', # Added this line
            'disk-cache': '256M', # Added this line
        }
    )


    start_time = datetime.now()

    if not hasattr(app, 'active_downloads'):
        app.active_downloads = {}

    app.active_downloads[download.gid] = {
        'download': download,
        'status_message': status_message,
        'user_id': user_id,
        'cancelled': False
    }

    while not download.is_complete:
        if app.active_downloads.get(download.gid, {}).get('cancelled', False):
            try:
                download.remove(force=True, files=True)
                await status_message.edit_text("✅ Dᴏᴡɴʟᴏᴀᴅ ᴄᴀɴᴄᴇʟʟᴇᴅ...")
            except Exception as e:
                logger.error(f"Error cancelling download: {e}")
                await status_message.edit_text("❌ Failed to cancel download.")

            if download.gid in app.active_downloads:
                del app.active_downloads[download.gid]
            return
        await asyncio.sleep(2)
        download.update()
        progress = download.progress

        elapsed_time = datetime.now() - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)
        total_bars = 10
        filled_bars = int(progress // (100 / total_bars))
        empty_bars = total_bars - filled_bars
        progress_bar = "➤" * filled_bars + "➖" * empty_bars
        truncated_name = truncate_filename(download.name)

        eta = download.eta if download.eta else "Calculating..."

        if progress == 100:
            current_status = "Cᴏᴍᴘʟᴇᴛᴇᴅ ✅"
        elif download.download_speed == 0:
            current_status = "Wᴀɪᴛɪɴɢ... ⏳"
        else:
            current_status = "Dᴏᴡɴʟᴏᴀᴅɪɴɢ... ⏬"

        speed = download.download_speed
        if speed > 5_000_000:  # >5MB/s
            speed_icon = "⚡"
        elif speed > 500_000:  # >500KB/s
            speed_icon = "🚀"
        else:
            speed_icon = "🐢"

        status_text = (        
            f"<b>━━━「 Tᴇʀᴀʙᴏx Dᴏᴡɴʟᴏᴀᴅᴇʀ 」━━━  </b>\n\n"
            f"╭─➤ <b>Fɪʟᴇ:</b> {truncated_name}\n"
            f"├─➤ <b>Pʀᴏɢʀᴇss:</b> {progress:.2f}%\n"
            f"├─➤ <b>Pʀᴏᴄᴇssᴇᴅ:</b> {format_size(download.completed_length)} / {format_size(download.total_length)}\n"
            f"├─➤ <b>Sᴛᴀᴛᴜs: {current_status}</b>\n"
            f"├─➤ <b>Sᴘᴇᴇᴅ:</b> {speed_icon} {format_size(speed)}/s\n"
            f"├─➤ <b>Eᴛᴀ:</b> {eta}\n"
            f"╰─➤ <b>Rᴇǫᴜᴇsᴛᴇᴅ Bʏ:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | <code>{user_id}</code>\n"
            )
        while True:
            try:
                # first_dlink = link_data[0].get("dlink", "https://t.me/jffmain")
                await update_status_message(
                    status_message,
                    status_text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Cᴀɴᴄᴇʟ 🚫", callback_data=f"cancel_{download.gid}"),
                         InlineKeyboardButton("🔗 Dɪʀᴇᴄᴛ Lɪɴᴋ", url=direct_link)],
                        [InlineKeyboardButton("🔥 Dɪʀᴇᴄᴛ Vɪᴅᴇᴏ Cʜᴀɴɴᴇʟs 🚀", url="https://t.me/NyxKingXlinks")]
                    ])
                )
                break
            except FloodWait as e:
                logger.error(f"Flood wait detected! Sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)

    if download.gid in app.active_downloads:
        del app.active_downloads[download.gid]

    file_path = download.files[0].path
    caption = (
        f"✨ {download.name}\n"
        f"⚡ <b>Vɪᴅᴇᴏ Bʏ:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>\n"
    )
    caption_btn = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("NʏxKɪɴɢX 🔥", url="https://t.me/NyxKingx"),
             InlineKeyboardButton("⚡ Cʜᴀɴɴᴇʟs",url="https://t.me/jffmain") ]  # Add button with callback data
        ]
    )

    last_update_time = time.time()
    UPDATE_INTERVAL = 3

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
            f"╭─➤ <b>Fɪʟᴇ:</b> <code>{download.name}</code>\n"
            f"├─➤ <b>Pʀᴏɢʀᴇss:</b> [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
            f"├─➤ <b>Pʀᴏɢʀᴇssᴇᴅ:</b> {format_size(current)} / {format_size(total)}\n"
            f"├─➤ <b>Sᴛᴀᴛᴜs:</b> Uᴘʟᴏᴀᴅɪɴɢ ᴛᴏ Tᴇʟᴇɢʀᴀᴍ...\n"
            f"├─➤ <b>Sᴘᴇᴇᴅ:</b> {format_size(current / elapsed_time.seconds if elapsed_time.seconds > 0 else 0)}/s\n"
            f"├─➤<b>ᴛɪᴍᴇ:</b> {elapsed_minutes}m {elapsed_seconds}s ᴇʟᴀᴘsᴇᴅ\n"
            f"╰─➤ <b>Uꜱᴇʀ:</b> <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | <code>{user_id}</code>\n"
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
                    'ffmpeg', '-y', '-ss', str(i * duration_per_part),
                    '-i', input_path, '-t', str(duration_per_part),
                    '-c', 'copy', '-map', '0',
                    '-metadata:s:v', 'rotate=0',  # Preserve original rotation
                    '-avoid_negative_ts', 'make_zero',
                    '-s', '1280x720',
                    '-aspect', '16:9',
                    '-threads', '10',  # Use more CPU threads

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
        part_caption = caption

        upload_as_video = True
        duration, width, height = 0, 0, 0

        if str(file_path).upper().endswith(("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPEG", "WEBM", "MKV")):
   
            try:
                metadata = ffmpeg.probe(file_path)["streams"]
                for meta in metadata:
                    if not height:
                
                        height = int(meta.get("height", 0))
                    if not width:
                        width = int(meta.get("width", 0))
                    if not duration:
                        duration = int(int(meta.get("duration_ts", 0)) / 1000)
            except Exception as e:
                logger.error(f"Error getting video metadata: {e}")
                upload_as_video = False

        else:
            upload_as_video = False
    
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

                    width, height = await get_video_info(part)
          
                    if USER_SESSION_STRING:
                        sent = await user.send_video(
                            DUMP_CHAT_ID, part, 
                            caption=part_caption,
                            reply_markup=caption_btn,
                            progress=upload_progress,
                            file_name=os.path.basename(part),
                            supports_streaming=True,
                            width=width,
                            height=height,
                            duration=duration,
                            disable_notification=True,
                            request_timeout=7200
                        )
                        await app.copy_message(
                            message.chat.id, DUMP_CHAT_ID, sent.id
                        )
                    else:
                        sent = await client.send_video(
                            DUMP_CHAT_ID, part,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            progress=upload_progress,
                            width=width,
                            height=height,
                            duration=duration,
                        )
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            width=width,
                            height=height,
                            duration=duration,
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

            width, height = await get_video_dimensions(file_path)           
            
            if USER_SESSION_STRING:
                try:
                    sent = await user.send_video(
                        DUMP_CHAT_ID, file_path,
                        caption=part_caption,
                        reply_markup=caption_btn,
                        progress=upload_progress,
                        width=width,
                        height=height,
                        duration=duration,
                    )
                    try:
                        await app.copy_message(
                            message.chat.id, DUMP_CHAT_ID, sent.id
                        )
                    except Exception as e:
                        logger.error(f"Error copying message: {e}")

                        try:
                            await app.send_video(
                                message.chat.id, sent.video.file_id,
                                caption=part_caption,
                                reply_markup=caption_btn,
                                width=width,
                                height=height,
                                duration=duration,
                            )
                        except Exception as e2:
                            logger.error(f"Error sending video: {e2}")
                            await app.send_video(
                                message.chat.id, file_path,
                                caption=part_caption,
                                reply_markup=caption_btn,
                                width=width,
                                height=height,
                                duration=duration,
                            )
                except Exception as e:
                    logger.error(f"Error sending video: {e}")
                    await app.send_video(
                        message.chat.id, file_path,
                        caption=part_caption,
                        reply_markup=caption_btn,
                        progress=upload_progress,
                        width=width,
                        height=height,
                        duration=duration,
                    )
            else:
                try:
                    sent = await client.send_video(
                        DUMP_CHAT_ID, file_path,
                        caption=part_caption,
                        reply_markup=caption_btn,
                        progress=upload_progress,
                        width=width,
                        height=height,
                        duration=duration,
                    )
                    try:
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            width=width,
                            height=height,
                            duration=duration,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send video using file_id: {e}")
                        await client.send_video(
                            message.chat.id, part,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            width=width,
                            height=height,
                            duration=duration,
                        )
                except Exception as e:
                    logger.error(f"Failed to send video: {e}")
                    await client.send_video(
                        message.chat.id, file_path,
                        caption=part_caption,
                        reply_markup=caption_btn,
                        progress=upload_progress,
                        width=width,
                        height=height,
                        duration=duration,
                    )

        if os.path.exists(file_path):
            os.remove(file_path)

        await message.reply_sticker("CAACAgUAAxkBAAEBOQVoBLWRUSRCieoGNbvQ5cJ1U8qtWgACKg0AAprJqVcDgujJs5TjwTYE")
        # await message.reply_text("✅ Uᴘʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ! Eɴᴊᴏʏ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ. 😎")

    start_time = datetime.now()
    await handle_upload()

    try:
        await status_message.delete()
        await message.delete()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        

# Add these imports
from aiohttp import web
# Add this to your imports at the top of the file
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, MessageDeleteForbidden


# Add this function to create a simple web server
# async def web_server():
#     # Define a simple health check endpoint
#     async def health_check(request):
#         return web.Response(text="Bot is running!")
    
#     # Create the web app
#     app = web.Application()
#     app.router.add_get("/", health_check)
    
#     # Start the web server
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "0.0.0.0", 8080)  # Use port 8080 or the PORT env var
#     await site.start()
#     logger.info("Web server started on port 8080")

# Modify your main code to start the web server
def run_user():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_user_client())

import struct

async def start_user_client():
    if user:
        try:
            await user.start()
            logger.info("User client started.")
        except struct.error as e:
            logger.error(f"Invalid session string: {e}")
            logger.info("Bot will continue without user client and split files in 2GB chunks")
            global USER_SESSION_STRING
            USER_SESSION_STRING = None
            global SPLIT_SIZE
            SPLIT_SIZE = 2093796556


def run_user():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_user_client())

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({
        "status": "success",
        "message": "NyxDesire By NʏxKɪɴɢX",
        "bot": "NyxDesireX",
        "theme": "Luxury | Hacker | Telegram Album Bot"
    })

async def web_server():
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("Web server started on port 8080")


async def check_dump_channel_access():
    try:
        # Try with bot client first
        chat = await app.get_chat(DUMP_CHAT_ID)
        bot_member = await app.get_chat_member(DUMP_CHAT_ID, app.me.id)
        logger.info(f"Bot access to dump channel: {chat.title}, permissions: {bot_member.privileges}")
        
        # Try with user client if available
        if user and USER_SESSION_STRING:
            try:
                user_chat = await user.get_chat(DUMP_CHAT_ID)
                user_member = await user.get_chat_member(DUMP_CHAT_ID, user.me.id)
                logger.info(f"User client access to dump channel: {user_chat.title}, status: {user_member.status}")
            except Exception as e:
                logger.error(f"User client cannot access dump channel: {e}")
                
        return True
    except Exception as e:
        logger.error(f"Error checking dump channel access: {e}")
        return False
    
async def main():
    # Start the web server
    await web_server()
    logger.info("Web server started")
    
    # Start the bot
    await app.start()
    logger.info("Bot client started")
    
    # Start user client if available
    if user:
        try:
            await user.start()
            logger.info("User client started successfully")
        except Exception as e:
            logger.error(f"Failed to start user client: {e}")
            global USER_SESSION_STRING
            USER_SESSION_STRING = None
            global SPLIT_SIZE
            SPLIT_SIZE = 2093796556
    
    # Now check dump channel access AFTER clients are started
    await check_dump_channel_access()
    
    # Send startup notification to bot owner
    try:
        await app.send_message(
            OWNER_ID,
            f"✅ **Bᴏᴛ Sᴛᴀʀᴛᴇᴅ Sᴜᴄᴄᴇssfᴜʟʏ!**\n\n"
            f"🕒 **Tɪᴍᴇ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🖥️ **Sᴇʀᴠᴇʀ:** {platform.node()}\n"
            f"💾 **Uѕᴇʀ Sᴇssɪᴏɴ:** {'✅ Aᴄᴛɪᴠᴇ' if USER_SESSION_STRING else '❌ Nᴏᴛ cᴏɴғɪɢᴜʀᴇᴅ'}\n"
            f"🔄 **Mᴀx Uᴘʟᴏᴀᴅ Sɪᴢᴇ:** {format_size(SPLIT_SIZE)}\n\n"
            f"Bᴏᴛ ɪs nᴏᴡ ʀᴇᴀᴅʏ tᴏ prᴏᴄᴇss Tᴇʀᴀbᴏx lɪɴᴋs!"
        )
        logger.info(f"Startup notification sent to owner: {OWNER_ID}")
    except Exception as e:
        logger.error(f"Failed to send startup notification to owner: {e}")
    
    # Keep the program running
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


