from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
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

OWNER_ID = 7560922302
ADMINS = [OWNER_ID]  # Add more admin IDs as needed

logger = logging.getLogger(__name__)

# Add this right after your imports and before any other code

# Global variables for premium account detection
IS_PREMIUM_ACCOUNT = False

# Initialize premium detection early
def detect_premium_from_cookies():
    """Early premium detection based on cookies"""
    global IS_PREMIUM_ACCOUNT
    
    cookie_string = os.getenv("MY_COOKIE", "")
    if not cookie_string:
        IS_PREMIUM_ACCOUNT = False
        return
    
    try:
        # Parse cookies quickly
        cookies = {}
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        
        # Quick premium detection
        premium_indicators = [
            'TSID' in cookies,
            'csrfToken' in cookies,
            len(cookies.get('browserid', '')) > 50,
            'ndut_fmt' in cookies
        ]
        
        IS_PREMIUM_ACCOUNT = sum(premium_indicators) >= 3
        
        if IS_PREMIUM_ACCOUNT:
            logger.info("🚀 PREMIUM COOKIES DETECTED!")
        else:
            logger.info("📝 Standard cookies detected")
            
    except Exception as e:
        logger.error(f"Error in early premium detection: {e}")
        IS_PREMIUM_ACCOUNT = False

# Call early detection
detect_premium_from_cookies()


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


import os

cookie_string = os.getenv(
    "MY_COOKIE",
    "browserid=avLKUlrztrL0C84414VnnfWxLrQ1vJblh4m8WCMxL7TZWIMpPdno52qQb27fk957PE6sUd5VZJ1ATlUe; TSID=DLpCxYPseu0EL2J5S2Hf36yFszAufv2G; ndus=Yd6IpupteHuieos8muZScO1E7xfuRT_csD6LBOF3; csrfToken=mKahcZKmznpDIODk5qQvF1YS; lang=en; __bid_n=1964760716d8bd55e14207; ndut_fmt=B7951F1AB0B1ECA11BDACDA093585A5F0F88DE80879A2413BE32F25A6B71C658"
)
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

# Premium optimized aria2 options
# Enhanced aria2 options based on account type
def get_aria2_options():
    """Get aria2 options based on account type"""
    if IS_PREMIUM_ACCOUNT:
        return {
            # Premium settings for maximum speed
            "split": "64",
            "max-connection-per-server": "64",
            "min-split-size": "1M",
            "max-concurrent-downloads": "10",
            "max-tries": "100",
            "retry-wait": "1",
            "timeout": "60",
            "connect-timeout": "30",
            "disk-cache": "128M",
            "file-allocation": "prealloc",
            "continue": "true",
            "allow-overwrite": "true",
            "max-overall-download-limit": "0",
            "max-download-limit": "0",
            "piece-length": "1M",
            "stream-piece-selector": "inorder",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.terabox.com/",
            "check-certificate": "false",
            "reuse-uri": "true"
        }
    else:
        return {
            # Standard settings for free accounts
            "max-tries": "50",
            "retry-wait": "3",
            "continue": "true",
            "allow-overwrite": "true",
            "min-split-size": "4M",
            "split": "16",
            "max-connection-per-server": "16",
            "max-overall-download-limit": "0",
            "max-download-limit": "0",
            "disk-cache": "32M"
        }

# Get the appropriate options
options = get_aria2_options()

# Log the configuration being used
if IS_PREMIUM_ACCOUNT:
    logger.info("🚀 Using PREMIUM download configuration")
else:
    logger.info("📝 Using STANDARD download configuration")


# Enhanced headers for premium downloads
premium_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Referer": "https://www.terabox.com/",
    "Origin": "https://www.terabox.com"
}

# Use premium headers if premium account
if IS_PREMIUM_ACCOUNT:
    my_headers.update(premium_headers)
    logger.info("🚀 Using premium headers")



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

DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '-1002664225966')
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

import speedtest

async def validate_premium_cookies_simple(cookies):
    """
    Simple and reliable premium cookie validation
    """
    result = {
        'is_premium': False,
        'account_type': 'free',
        'method': 'cookie_analysis',
        'confidence': 'medium',
        'indicators_found': []
    }
    
    try:
        # Convert cookies dict to string for analysis
        cookie_str = str(cookies).lower()
        
        # Premium indicators in your cookies
        premium_indicators = {
            'tsid_present': 'tsid' in cookies,  # TSID often indicates logged-in premium user
            'csrf_token': 'csrftoken' in cookies,  # CSRF token suggests authenticated session
            'browser_id_format': len(cookies.get('browserid', '')) > 50,  # Long browser ID
            'ndut_fmt_present': 'ndut_fmt' in cookies,  # Format token
            'bid_present': '__bid_n' in cookies  # Bid number
        }
        
        # Check each indicator
        found_indicators = []
        for indicator, condition in premium_indicators.items():
            if condition:
                found_indicators.append(indicator)
        
        result['indicators_found'] = found_indicators
        
        # If we have multiple indicators, likely premium
        if len(found_indicators) >= 3:
            result['is_premium'] = True
            result['account_type'] = 'premium'
            result['confidence'] = 'high'
        elif len(found_indicators) >= 2:
            result['is_premium'] = True
            result['account_type'] = 'premium'
            result['confidence'] = 'medium'
        
        # Additional checks for premium patterns
        if cookies.get('TSID') and len(cookies.get('TSID', '')) > 20:
            result['is_premium'] = True
            result['account_type'] = 'premium'
            found_indicators.append('long_tsid')
        
        logger.info(f"Cookie analysis: Found {len(found_indicators)} premium indicators: {found_indicators}")
        
    except Exception as e:
        logger.error(f"Error in premium cookie validation: {e}")
        result['error'] = str(e)
    
    return result

async def test_cookie_functionality(cookies):
    """
    Test if cookies work by making a simple request
    """
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(
            cookies=cookies, 
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            session.headers.update(my_headers)
            
            # Test with a simple TeraBox page
            test_url = "https://www.terabox.com/main?category=all"
            async with session.get(test_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if we're logged in (look for user-specific content)
                    login_indicators = [
                        'logout' in content.lower(),
                        'profile' in content.lower(),
                        'dashboard' in content.lower(),
                        'my files' in content.lower(),
                        'upload' in content.lower()
                    ]
                    
                    if any(login_indicators):
                        logger.info("✅ Cookies are working - user appears to be logged in")
                        return True
                    else:
                        logger.warning("⚠️ Cookies may not be working - no login indicators found")
                        return False
                else:
                    logger.error(f"❌ Cookie test failed - HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Cookie functionality test failed: {e}")
        return False

# Enhanced initialization function
async def initialize_premium_cookies():
    """Initialize and validate premium cookies"""
    global my_cookie, IS_PREMIUM_ACCOUNT
    
    cookie_string = os.getenv("MY_COOKIE", "")
    
    if not cookie_string:
        logger.warning("MY_COOKIE not set!")
        my_cookie = {}
        IS_PREMIUM_ACCOUNT = False
        return
    
    try:
        # Parse cookies
        my_cookie = {}
        for item in cookie_string.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                my_cookie[key.strip()] = value.strip()
        
        if not my_cookie:
            logger.error("No valid cookies found")
            IS_PREMIUM_ACCOUNT = False
            return
        
        logger.info(f"Loaded {len(my_cookie)} cookies")
        
        # Test cookie functionality
        cookies_work = await test_cookie_functionality(my_cookie)
        
        if cookies_work:
            logger.info("✅ Cookies are functional")
            
            # Check for premium status
            premium_status = await validate_premium_cookies_simple(my_cookie)
            
            if premium_status['is_premium']:
                logger.info("🚀 PREMIUM COOKIES DETECTED!")
                logger.info(f"Confidence: {premium_status['confidence']}")
                logger.info(f"Indicators: {premium_status['indicators_found']}")
                IS_PREMIUM_ACCOUNT = True
            else:
                logger.info("📝 Standard cookies detected")
                IS_PREMIUM_ACCOUNT = False
        else:
            logger.warning("⚠️ Cookies may be expired or invalid")
            IS_PREMIUM_ACCOUNT = False
            
    except Exception as e:
        logger.error(f"Error initializing cookies: {e}")
        my_cookie = {}
        IS_PREMIUM_ACCOUNT = False

# Add command to test cookies
@app.on_message(filters.command("testcookies") & filters.user(ADMINS))
async def test_cookies_command(client: Client, message: Message):
    """Test current cookies and show status"""
    
    if not my_cookie:
        await message.reply_text("❌ No cookies configured!")
        return
    
    status_msg = await message.reply_text("🔍 Testing cookies...")
    
    try:
        # Test functionality
        cookies_work = await test_cookie_functionality(my_cookie)
        
        # Check premium status
        premium_status = await validate_premium_cookies_simple(my_cookie)
        
        status_text = "🍪 **Cookie Test Results**\n\n"
        
        # Functionality test
        if cookies_work:
            status_text += "✅ **Functionality:** Working\n"
        else:
            status_text += "❌ **Functionality:** Not working\n"
        
        # Premium status
        if premium_status['is_premium']:
            status_text += "🚀 **Account Type:** Premium\n"
            status_text += f"🎯 **Confidence:** {premium_status['confidence']}\n"
            status_text += f"📊 **Indicators:** {len(premium_status['indicators_found'])}\n"
            status_text += f"🔍 **Found:** {', '.join(premium_status['indicators_found'])}\n"
        else:
            status_text += "📝 **Account Type:** Free/Standard\n"
        
        # Cookie info
        status_text += f"\n📋 **Cookie Count:** {len(my_cookie)}\n"
        status_text += f"🕒 **Tested:** {datetime.now().strftime('%H:%M:%S')}\n"
        
        # Expected benefits
        if premium_status['is_premium']:
            status_text += "\n🎁 **Expected Benefits:**\n"
            status_text += "• Higher download speeds\n"
            status_text += "• No download limits\n"
            status_text += "• Priority server access\n"
            status_text += "• Multiple concurrent downloads\n"
        
        await status_msg.edit_text(status_text)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error testing cookies: {str(e)}")


@app.on_message(filters.command("speedtest"))
async def speedtest_command(client: Client, message: Message):
    msg = await message.reply_text("⏳ Running speedtest... Please wait.")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        server = st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        ping = st.results.ping
        isp = st.config['client']['isp']
        country = st.config['client']['country']
        sponsor = server['sponsor']
        server_name = server['name']
        server_country = server['country']
        host = server['host']
        distance = server['d']
        timestamp = st.results.timestamp
        share_url = st.results.share()

        def human_readable_speed(size):
            if size < 1e6:
                return f"{size/1e3:.2f} Kbps"
            elif size < 1e9:
                return f"{size/1e6:.2f} Mbps"
            else:
                return f"{size/1e9:.2f} Gbps"

        result_text = (
            "⚡️ <b>Speedtest Results</b> ⚡️\n\n"
            f"🏓 <b>Ping:</b> <code>{ping:.2f} ms</code>\n"
            f"⬇️ <b>Download:</b> <code>{human_readable_speed(download_speed)}</code>\n"
            f"⬆️ <b>Upload:</b> <code>{human_readable_speed(upload_speed)}</code>\n"
            f"🌐 <b>ISP:</b> <code>{isp}</code>\n"
            f"🌍 <b>Country:</b> <code>{country}</code>\n"
            f"🏢 <b>Server:</b> <code>{sponsor} ({server_name}, {server_country})</code>\n"
            f"🔗 <b>Host:</b> <code>{host}</code>\n"
            f"📏 <b>Distance:</b> <code>{distance:.2f} km</code>\n"
            f"🕒 <b>Timestamp:</b> <code>{timestamp}</code>\n"
            f"🖼️ <a href='{share_url}'>Result Image</a>"
        )
        await msg.edit_text(result_text, disable_web_page_preview=False)
    except Exception as e:
        await msg.edit_text(f"❌ Speedtest failed: <code>{e}</code>")

@app.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Client, message: Message):
    if message.reply_to_message:
        # Inform the admin that the broadcast will be sent to all users
        await message.reply(
            "📢 Bʀᴏᴀᴅᴄᴀsᴛ ᴡɪʟʟ ʙᴇ sᴇɴᴛ ᴛᴏ ALL ᴜsᴇʀs.\n\n"
            "⚙️ Bʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ɪs ʙᴇɪɴɢ ᴘʀᴏᴄᴇssᴇᴅ."
        )
        
        # Get the broadcast message
        broadcast_msg = message.reply_to_message
        
        # Get the list of all users from the database
        try:
            # Use a more reliable method to get user IDs - specifically looking for user_id field
            user_ids = []
            cursor = collection.find({}, {"user_id": 1})
            for doc in cursor:
                if "user_id" in doc and doc["user_id"] and isinstance(doc["user_id"], int):
                    user_ids.append(doc["user_id"])
            
            if not user_ids:
                await message.reply("❌ Nᴏ ᴠᴀʟɪᴅ ᴜsᴇʀs ғᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ.")
                return
                
            # Perform broadcast
            total = len(user_ids)
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            
            pls_wait = await message.reply("<i>⚙️ Bʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...</i>")
            
            for index, chat_id in enumerate(user_ids):
                try:
                    # Ensure chat_id is an integer
                    if not isinstance(chat_id, int):
                        logger.warning(f"Skipping invalid chat_id: {chat_id} (not an integer)")
                        unsuccessful += 1
                        continue
                        
                    # Send message with a small delay to avoid hitting rate limits
                    await asyncio.sleep(0.1)
                    await broadcast_msg.copy(chat_id=chat_id)
                    successful += 1
                except FloodWait as e:
                    # Handle FloodWait correctly
                    logger.warning(f"FloodWait of {e.value} seconds encountered")
                    await asyncio.sleep(e.value + 1)  # Add 1 second buffer
                    try:
                        await broadcast_msg.copy(chat_id=chat_id)
                        successful += 1
                    except Exception as inner_e:
                        logger.error(f"Failed to send message to {chat_id} after FloodWait: {inner_e}")
                        unsuccessful += 1
                except UserIsBlocked:
                    logger.info(f"User {chat_id} has blocked the bot")
                    await del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    logger.info(f"User {chat_id} account is deactivated")
                    await del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    logger.error(f"Unexpected error for {chat_id}: {e}")
                    unsuccessful += 1
                
                # Update loading bar every 5 users or for the last user
                if index % 5 == 0 or index == total - 1:
                    progress = (index + 1) / total
                    bar_length = 20  # Length of the loading bar
                    filled_length = int(bar_length * progress)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    
                    try:
                        await pls_wait.edit_text(
                            f"<b>📢 Bʀᴏᴀᴅᴄᴀsᴛ Pʀᴏɢʀᴇss:</b>\n\n"
                            f"<code>{bar}</code> {progress:.1%}\n\n"
                            f"✅ Successful: <code>{successful}</code>\n"
                            f"❌ Failed: <code>{unsuccessful}</code>\n"
                            f"🚫 Blocked: <code>{blocked}</code>\n"
                            f"🗑️ Deleted: <code>{deleted}</code>\n"
                            f"⏳ Processing: <code>{index+1}/{total}</code>"
                        )
                    except MessageNotModified:
                        # Ignore "message not modified" errors
                        pass
                    except Exception as e:
                        logger.error(f"Error updating progress message: {e}")

            # Generate final status message
            status = (
                f"<b>📢 Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                f"<b>📊 Sᴛᴀᴛɪsᴛɪᴄs:</b>\n"
                f"• Total Users: <code>{total}</code>\n"
                f"• Successful: <code>{successful}</code>\n"
                f"• Blocked Users: <code>{blocked}</code>\n"
                f"• Deleted Accounts: <code>{deleted}</code>\n"
                f"• Unsuccessful: <code>{unsuccessful}</code>\n\n"
                f"✅ Success Rate: <code>{(successful/total)*100:.1f}%</code>"
            )
            
            try:
                await pls_wait.edit_text(status)
            except Exception as e:
                logger.error(f"Failed to send final status: {e}")
                await message.reply(status)
                
        except Exception as e:
            logger.error(f"Broadcast failed: {e}", exc_info=True)
            await message.reply(f"❌ Bʀᴏᴀᴅᴄᴀsᴛ ғᴀɪʟᴇᴅ: {str(e)}")
    
    else:
        # If no message is replied to
        msg = await message.reply(
            "⚠️ <b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ</b>\n\n"
            "<code>/broadcast</code> (as reply to message)"
        )
        await asyncio.sleep(8)
        await msg.delete()
    
    return


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
            "REQUEST_SUB_CHANNELS": [-1002630824315],  # Default approval channel
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
            {"$set": {"REQUEST_SUB_CHANNELS": [-1002630824315]}}
        )
        settings_doc["REQUEST_SUB_CHANNELS"] = [-1002630824315]

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


@app.on_callback_query(filters.regex("^restart_bot$"))
async def restart_bot_callback(client, callback_query: CallbackQuery):
    # Check if the user is an admin
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.", show_alert=True)
        return
    
    # Inform the user that the bot is restarting
    await callback_query.answer("Bᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...", show_alert=True)
    
    # Cool restart message with animation effect
    restart_message = (
        "╭─━━━━━━━━━━━━━━━━━━━━─╮\n"
        "┃    🔄 Rᴇsᴛᴀʀᴛɪɴɢ Bᴏᴛ    ┃\n"
        "╰─━━━━━━━━━━━━━━━━━━━━─╯\n\n"
        "⚙️ <b>Sʏsᴛᴇᴍ ɪs ʀᴇʙᴏᴏᴛɪɴɢ...</b>\n\n"
        "• Sᴀᴠɪɴɢ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴs\n"
        "• Cʟᴏsɪɴɢ ᴄᴏɴɴᴇᴄᴛɪᴏɴs\n"
        "• Rᴇsᴛᴀʀᴛɪɴɢ sᴇʀᴠɪᴄᴇs\n\n"
        "🕒 Tʜᴇ ʙᴏᴛ ᴡɪʟʟ ʙᴇ ʙᴀᴄᴋ ᴏɴʟɪɴᴇ sʜᴏʀᴛʟʏ.\n"
        "🚀 Iɴɪᴛɪᴀᴛᴇᴅ ʙʏ: <a href='tg://user?id={}'>{}</a>"
    ).format(
        callback_query.from_user.id,
        callback_query.from_user.first_name
    )
    
    # Show animation effect by updating the message multiple times
    loading_message = await callback_query.message.edit_text(
        "╭─━━━━━━━━━━━━━━━━━━━━─╮\n"
        "┃    🔄 Rᴇsᴛᴀʀᴛɪɴɢ Bᴏᴛ    ┃\n"
        "╰─━━━━━━━━━━━━━━━━━━━━─╯\n\n"
        "⏳ Pʀᴇᴘᴀʀɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ..."
    )
    
    # Simulate a loading animation
    loading_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for i in range(3):  # Just a few iterations to avoid delays
        for char in loading_chars:
            try:
                await loading_message.edit_text(
                    "╭─━━━━━━━━━━━━━━━━━━━━─╮\n"
                    f"┃    {char} Rᴇsᴛᴀʀᴛɪɴɢ Bᴏᴛ {char}    ┃\n"
                    "╰─━━━━━━━━━━━━━━━━━━━━─╯\n\n"
                    f"⏳ Pʀᴇᴘᴀʀɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ... {i+1}/3"
                )
                await asyncio.sleep(0.2)
            except Exception:
                # Ignore errors during animation
                pass
    
    # Final message before restart
    await callback_query.message.edit_text(restart_message)
    
    # Log the restart event
    logger.info(f"Bᴏᴛ ʀᴇsᴛᴀʀᴛ ɪɴɪᴛɪᴀᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴ: {callback_query.from_user.id}")
    
    # Give a moment for the message to be displayed before restarting
    await asyncio.sleep(2)
    
    # Restart the bot using the same method as in the /restart command
    os.execv(sys.executable, ['python'] + sys.argv)


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
        [InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="restart_bot")]
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
        [InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="restart_bot")]
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
        [InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ʙᴏᴛ", callback_data="restart_bot")]
    ])
    
    await callback_query.message.edit_text(
        "⚙️ **Admin Control Panel**\n\nSelect an option from the menu below:",
        reply_markup=keyboard
    )

@app.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    global download_count, total_download_size
    # Only allow the owner and admins to access stats
    if message.from_user.id not in ADMINS:
        await message.reply_text("⚠️ This command is only available to bot administrators.")
        return
    
    stats_doc = db.get_collection("stats").find_one({"_id": "download_stats"})
    if stats_doc:
        download_count = stats_doc.get("count", download_count)
        total_download_size = stats_doc.get("total_size", total_download_size)
    
    # Send a processing message first to improve UX
    processing_msg = await message.reply_text("🤖 <b>Gᴀᴛʜᴇʀɪɴɢ sᴛᴀᴛɪsᴛɪᴄs...</b>")
    
    try:
        # Get system stats with error handling
        try:
            cpu_usage = psutil.cpu_percent(interval=1)  # More accurate with interval
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            ram_used = format_size(ram.used)
            ram_total = format_size(ram.total)
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_used = format_size(disk.used)
            disk_total = format_size(disk.total)
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            cpu_usage = ram_usage = disk_usage = "Error"
            ram_used = ram_total = disk_used = disk_total = "N/A"
        
        # Get MongoDB stats with error handling
        try:
            user_count = collection.count_documents({})
            active_tokens = collection.count_documents({"token_status": "active"})
            inactive_tokens = collection.count_documents({"token_status": "inactive"})
            
            # Get additional stats
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_users_today = collection.count_documents({"created_at": {"$gte": today}})
            
            # Get download stats from the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            recent_downloads = collection.count_documents({"last_download": {"$gte": yesterday}})
        except Exception as e:
            logger.error(f"Error getting MongoDB stats: {e}")
            user_count = active_tokens = inactive_tokens = new_users_today = recent_downloads = "Error"
        
        # Calculate uptime
        uptime = datetime.now() - start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Get bot settings
        settings = await get_settings()
        force_channels = len(settings.get("FORCE_SUB_CHANNELS", []))
        request_channels = len(settings.get("REQUEST_SUB_CHANNELS", []))
        
        # Format the stats message with more details and better organization
        stats_text = (
            f"📊 <b>Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs</b> 📊\n\n"
            f"<b>💻 Sʏsᴛᴇᴍ Rᴇsᴏᴜʀᴄᴇs:</b>\n"
            f"  • CPU: {cpu_usage}%\n"
            f"  • RAM: {ram_usage}% ({ram_used}/{ram_total})\n"
            f"  • Disk: {disk_usage}% ({disk_used}/{disk_total})\n\n"
            
            f"<b>⏳ Uᴘᴛɪᴍᴇ:</b>\n"
            f"  • {days}d {hours}h {minutes}m {seconds}s\n\n"
            
            f"<b>👥 Usᴇʀ Sᴛᴀᴛɪsᴛɪᴄs:</b>\n"
            f"  • Total Users: {user_count}\n"
            f"  • New Today: {new_users_today}\n"
            f"  • Active Tokens: {active_tokens}\n"
            f"  • Inactive Tokens: {inactive_tokens}\n\n"
            
            f"<b>📈 Aᴄᴛɪᴠɪᴛʏ:</b>\n"
            f"  • Downloads: {download_count}\n"
            f"  • Recent (24h): {recent_downloads}\n"
            f"  • Total Downloaded: {format_size(total_download_size)}\n\n"
            
            f"<b>🔧 Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴ:</b>\n"
            f"  • Force Sub Channels: {force_channels}\n"
            f"  • Request Channels: {request_channels}\n"
            f"  • Token System: {'✅ Enabled' if TOKEN_SYSTEM_ENABLED else '❌ Disabled'}\n"
            f"  • DB Connection: {'✅ Connected' if client else '❌ Disconnected'}\n"
            f"  • Database: {DATABASE_NAME} - {COLLECTION_NAME}\n\n"
            
            f"<b>🚀 Pᴏᴡᴇʀᴇᴅ ʙʏ:</b> <a href='https://t.me/NyxKingS'>NʏxKɪɴɢ❤️🚀</a>"
        )

        # Create inline keyboard for admin actions
        # keyboard = InlineKeyboardMarkup([
        #     [InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ Sᴛᴀᴛs", callback_data="refresh_stats")],
        #     [InlineKeyboardButton("⚙️ Aᴅᴍɪɴ Pᴀɴᴇʟ", callback_data="admin_panel")]
        # ])

        # Edit the processing message with the stats
        await processing_msg.edit_text(stats_text,  disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error generating stats: {e}", exc_info=True)
        await processing_msg.edit_text(f"❌ Error generating stats: {str(e)}")

# 
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/+8NE_GtI0UQZiZjc1")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/NyxKingS")
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
                    [InlineKeyboardButton("ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/+8NE_GtI0UQZiZjc1")]
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
                    [InlineKeyboardButton("ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/+8NE_GtI0UQZiZjc1")],
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



@app.on_message(filters.command("testspeed"))
async def test_download_speed(client: Client, message: Message):
    """Test download speed with current configuration"""
    
    test_msg = await message.reply_text("🧪 Testing download configuration...")
    
    try:
        # Show current configuration
        config_info = (
            f"🔧 **Current Configuration:**\n\n"
            f"💎 **Account:** {'🚀 PREMIUM' if IS_PREMIUM_ACCOUNT else '📝 STANDARD'}\n"
            f"🔗 **Connections:** {options.get('max-connection-per-server', '16')}\n"
            f"✂️ **Splits:** {options.get('split', '16')}\n"
            f"💾 **Cache:** {options.get('disk-cache', '32M')}\n"
            f"⚡ **Min Split:** {options.get('min-split-size', '4M')}\n\n"
            f"Ready for high-speed downloads! 🚀"
        )
        
        await test_msg.edit_text(config_info)
        
    except Exception as e:
        await test_msg.edit_text(f"❌ Test failed: {str(e)}")


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

import aiohttp
import json
import logging
from datetime import datetime

async def check_cookie_premium_status(cookies, headers=None):
    """
    Check if TeraBox cookies belong to a premium or free account
    
    Args:
        cookies (dict): Cookie dictionary
        headers (dict): Optional headers to use with request
    
    Returns:
        dict: {
            'is_premium': bool,
            'account_type': str,
            'quota_info': dict,
            'error': str or None
        }
    """
    
    if headers is None:
        headers = my_headers.copy()
    
    result = {
        'is_premium': False,
        'account_type': 'free',
        'quota_info': {},
        'error': None,
        'checked_at': datetime.now()
    }
    
    try:
        # Create session with proper error handling
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(
            cookies=cookies, 
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            session.headers.update(headers)
            
            # Method 1: Check user info endpoint
            try:
                user_info_url = "https://www.terabox.com/api/user/info"
                async with session.get(user_info_url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            # Check for premium indicators in user info
                            if 'result' in data and data['result']:
                                user_data = data['result']
                                
                                # Common premium indicators
                                premium_indicators = [
                                    user_data.get('is_vip', False),
                                    user_data.get('is_premium', False),
                                    user_data.get('vip_type', 0) > 0,
                                    user_data.get('member_type', 0) > 0,
                                ]
                                
                                # Check account type string
                                account_type_str = str(user_data.get('account_type', '')).lower()
                                if 'premium' in account_type_str or 'vip' in account_type_str:
                                    premium_indicators.append(True)
                                
                                if any(premium_indicators):
                                    result['is_premium'] = True
                                    result['account_type'] = 'premium'
                                
                                # Extract quota information
                                result['quota_info'] = {
                                    'total_space': user_data.get('quota', 0),
                                    'used_space': user_data.get('used', 0),
                                    'vip_type': user_data.get('vip_type', 0),
                                    'member_type': user_data.get('member_type', 0)
                                }
                                
                                logger.info(f"User info check: Premium={result['is_premium']}")
                                return result
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Failed to parse user info response: {e}")
                    else:
                        logger.warning(f"User info endpoint returned status: {response.status}")
            except aiohttp.ClientError as e:
                logger.warning(f"Failed to check user info endpoint: {e}")
            
            # Method 2: Check quota endpoint
            try:
                quota_url = "https://www.terabox.com/api/quota"
                async with session.get(quota_url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            if 'result' in data and data['result']:
                                quota_data = data['result']
                                
                                # Check quota limits (premium usually has higher limits)
                                total_quota = quota_data.get('total', 0)
                                
                                # TeraBox free accounts typically have 1TB (1099511627776 bytes)
                                # Premium accounts have much higher limits
                                if total_quota > 1099511627776:  # More than 1TB
                                    result['is_premium'] = True
                                    result['account_type'] = 'premium'
                                
                                result['quota_info'].update({
                                    'total_space': total_quota,
                                    'used_space': quota_data.get('used', 0),
                                    'free_space': quota_data.get('free', 0)
                                })
                                
                                logger.info(f"Quota check: Premium={result['is_premium']}")
                                return result
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Failed to parse quota response: {e}")
                    else:
                        logger.warning(f"Quota endpoint returned status: {response.status}")
            except aiohttp.ClientError as e:
                logger.warning(f"Failed to check quota endpoint: {e}")
            
            # Method 3: Cookie analysis (fallback method)
            if not result['is_premium']:
                cookie_analysis = analyze_cookies_for_premium(cookies)
                result.update(cookie_analysis)
                logger.info(f"Cookie analysis: Premium={result['is_premium']} (confidence: {cookie_analysis.get('confidence', 'low')})")
                
    except aiohttp.ClientTimeout:
        result['error'] = "Request timeout while checking premium status"
        logger.error("Timeout while checking cookie premium status")
    except aiohttp.ClientError as e:
        result['error'] = f"Network error: {str(e)}"
        logger.error(f"Network error while checking premium status: {e}")
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error while checking premium status: {e}")
    
    return result


def analyze_cookies_for_premium(cookies):
    """
    Analyze cookies for premium indicators (fallback method)
    
    Args:
        cookies (dict): Cookie dictionary
    
    Returns:
        dict: Premium status based on cookie analysis
    """
    result = {
        'is_premium': False,
        'account_type': 'free',
        'confidence': 'low'  # Low confidence since this is cookie-based guessing
    }
    
    # Convert cookies to string for analysis
    cookie_string = str(cookies).lower()
    
    # Premium indicators in cookies
    premium_keywords = [
        'vip', 'premium', 'pro', 'plus', 'member',
        'subscription', 'paid', 'upgrade'
    ]
    
    # Check for premium keywords
    premium_found = any(keyword in cookie_string for keyword in premium_keywords)
    
    # Check for specific cookie values that might indicate premium
    premium_cookies = [
        cookies.get('member_type', '0') != '0',
        cookies.get('vip_type', '0') != '0',
        cookies.get('is_vip', 'false').lower() == 'true',
        cookies.get('account_type', '').lower() in ['premium', 'vip', 'pro']
    ]
    
    if premium_found or any(premium_cookies):
        result['is_premium'] = True
        result['account_type'] = 'premium'
        result['confidence'] = 'medium'
    
    return result

async def validate_and_check_cookies(cookie_string):
    """
    Validate cookies and check premium status
    
    Args:
        cookie_string (str): Raw cookie string
    
    Returns:
        dict: Validation and premium check results
    """
    result = {
        'valid': False,
        'premium_status': None,
        'error': None
    }
    
    try:
        # Parse cookies
        if not cookie_string:
            result['error'] = "Empty cookie string"
            return result
        
        # Safe cookie parsing with better error handling
        cookies = {}
        try:
            cookie_items = [item.strip() for item in cookie_string.split(";") if item.strip()]
            for item in cookie_items:
                if "=" in item:
                    key, value = item.split("=", 1)
                    cookies[key.strip()] = value.strip()
        except (ValueError, AttributeError) as e:
            result['error'] = f"Cookie parsing error: {str(e)}"
            return result
        
        if not cookies:
            result['error'] = "No valid cookies found"
            return result
        
        result['valid'] = True
        
        # Check premium status
        try:
            premium_status = await check_cookie_premium_status(cookies)
            result['premium_status'] = premium_status
        except Exception as e:
            result['error'] = f"Premium status check failed: {str(e)}"
            logger.error(f"Premium status check error: {e}")
        
        # Log results
        if result['premium_status'] and result['premium_status']['is_premium']:
            logger.info("✅ Premium cookies detected!")
            logger.info(f"Account type: {result['premium_status']['account_type']}")
            if result['premium_status']['quota_info']:
                total_gb = result['premium_status']['quota_info'].get('total_space', 0) / (1024**3)
                used_gb = result['premium_status']['quota_info'].get('used_space', 0) / (1024**3)
                logger.info(f"Storage: {used_gb:.2f}GB / {total_gb:.2f}GB")
        else:
            logger.info("ℹ️ Free account cookies detected")
            if result['premium_status'] and result['premium_status']['error']:
                logger.warning(f"Premium check error: {result['premium_status']['error']}")
        
    except Exception as e:
        result['error'] = f"Cookie validation error: {str(e)}"
        logger.error(f"Error validating cookies: {e}")
    
    return result


async def initialize_cookies():
    """Initialize and validate cookies with premium checking"""
    global my_cookie, IS_PREMIUM_ACCOUNT
    
    cookie_string = os.getenv("MY_COOKIE", "browserid=avLKUlrztrL0C84414VnnfWxLrQ1vJblh4m8WCMxL7TZWIMpPdno52qQb27fk957PE6sUd5VZJ1ATlUe; TSID=DLpCxYPseu0EL2J5S2Hf36yFszAufv2G; ndus=Yd6IpupteHuieos8muZScO1E7xfuRT_csD6LBOF3; csrfToken=mKahcZKmznpDIODk5qQvF1YS; lang=en; __bid_n=1964760716d8bd55e14207; ndut_fmt=B7951F1AB0B1ECA11BDACDA093585A5F0F88DE80879A2413BE32F25A6B71C658")
    
    if not cookie_string:
        logger.warning("MY_COOKIE not set!")
        my_cookie = {}
        IS_PREMIUM_ACCOUNT = False
        return
    
    try:
        # Safe cookie parsing
        my_cookie = {}
        cookie_items = [item.strip() for item in cookie_string.split(";") if item.strip()]
        for item in cookie_items:
            if "=" in item:
                key, value = item.split("=", 1)
                my_cookie[key.strip()] = value.strip()
        
        if not my_cookie:
            logger.error("No valid cookies found in MY_COOKIE")
            IS_PREMIUM_ACCOUNT = False
            return
        
        # Validate and check premium status
        validation_result = await validate_and_check_cookies(cookie_string)
        
        if validation_result['valid']:
            premium_status = validation_result['premium_status']
            if premium_status and premium_status['is_premium']:
                logger.info("🚀 Premium cookies loaded - expecting enhanced download speeds!")
                IS_PREMIUM_ACCOUNT = True
            else:
                logger.info("📝 Free account cookies loaded")
                IS_PREMIUM_ACCOUNT = False
                
            if validation_result['error']:
                logger.warning(f"Cookie validation warning: {validation_result['error']}")
                
        else:
            logger.error(f"Cookie validation failed: {validation_result['error']}")
            IS_PREMIUM_ACCOUNT = False
            
    except Exception as e:
        logger.error(f"Error initializing cookies: {e}")
        my_cookie = {}
        IS_PREMIUM_ACCOUNT = False


# Command to check cookie status
@app.on_message(filters.command("cookiestatus") & filters.user(ADMINS))
async def check_cookie_status(client: Client, message: Message):
    """Admin command to check current cookie premium status"""
    
    if not my_cookie:
        await message.reply_text("❌ No cookies configured!")
        return
    
    status_msg = await message.reply_text("🔍 Checking cookie premium status...")
    
    try:
        premium_status = await check_cookie_premium_status(my_cookie)
        
        status_text = "🍪 **Cookie Status Report**\n\n"
        
        if premium_status['is_premium']:
            status_text += "✅ **Premium Account Detected!**\n"
            status_text += f"📊 **Account Type:** {premium_status['account_type'].title()}\n"
        else:
            status_text += "📝 **Free Account**\n"
        
        if premium_status['quota_info']:
            quota = premium_status['quota_info']
            total_gb = quota.get('total_space', 0) / (1024**3)
            used_gb = quota.get('used_space', 0) / (1024**3)
            
            status_text += f"\n💾 **Storage Info:**\n"
            status_text += f"• Total: {total_gb:.2f} GB\n"
            status_text += f"• Used: {used_gb:.2f} GB\n"
            status_text += f"• Free: {(total_gb - used_gb):.2f} GB\n"
        
        if premium_status['error']:
            status_text += f"\n⚠️ **Warning:** {premium_status['error']}\n"
        
        status_text += f"\n🕒 **Checked:** {premium_status['checked_at'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        await status_msg.edit_text(status_text)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error checking cookie status: {str(e)}")


async def fetch_download_link_async(url):
    """
    Enhanced TeraBox link fetcher optimized for premium accounts
    Attempts multiple methods to get the fastest download links
    """
    encoded_url = urllib.parse.quote(url)
    
    # Enhanced session configuration for premium
    connector_config = {
        'ssl': False,
        'limit': 100,
        'limit_per_host': 50,
        'ttl_dns_cache': 300,
        'use_dns_cache': True,
    }
    
    timeout_config = aiohttp.ClientTimeout(
        total=60,
        connect=15,
        sock_read=30
    )
    
    async with aiohttp.ClientSession(
        cookies=my_cookie,
        timeout=timeout_config,
        connector=aiohttp.TCPConnector(**connector_config)
    ) as my_session:
        
        # Enhanced headers for premium access
        premium_headers = my_headers.copy()
        if IS_PREMIUM_ACCOUNT:
            premium_headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Priority': 'u=1, i',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
        
        my_session.headers.update(premium_headers)
        
        # Method 1: Premium API endpoint (fastest for premium users)
        if IS_PREMIUM_ACCOUNT:
            try:
                logger.info("🚀 Attempting premium API method...")
                premium_result = await fetch_premium_api_method(my_session, url)
                if premium_result:
                    logger.info("✅ Premium API method successful!")
                    return await optimize_download_links(premium_result)
            except Exception as e:
                logger.warning(f"Premium API method failed: {e}")
        
        # Method 2: Enhanced standard method with optimizations
        try:
            logger.info("📡 Attempting enhanced standard method...")
            
            # Create tasks properly
            tasks = []
            
            # Primary request
            tasks.append(asyncio.create_task(fetch_with_method(my_session, url, "primary")))
            
            # Alternative endpoints for premium users
            if IS_PREMIUM_ACCOUNT:
                alt_urls = [
                    url.replace('terabox.com', '1024tera.com'),
                    url.replace('terabox.com', 'teraboxapp.com'),
                    url.replace('terabox.com', 'nephobox.com')
                ]
                
                for alt_url in alt_urls:
                    if alt_url != url:  # Avoid duplicate URLs
                        tasks.append(asyncio.create_task(fetch_with_method(my_session, alt_url, "alternative")))
            
            # Fixed concurrent execution
            try:
                # Wait for first successful result
                done, pending = await asyncio.wait(
                    tasks, 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=45
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
                # Process completed tasks
                for task in done:
                    try:
                        result = await task
                        if result:
                            logger.info("✅ Enhanced method successful!")
                            return await optimize_download_links(result)
                    except Exception as e:
                        logger.debug(f"Task failed: {e}")
                        continue
                        
            except asyncio.TimeoutError:
                logger.warning("⏰ Enhanced method timed out")
                # Cancel all tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
            except Exception as e:
                logger.error(f"Enhanced method failed: {e}")
                # Cancel all tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                        
        except Exception as e:
            logger.error(f"Enhanced method setup failed: {e}")
        
        # Method 3: Fallback with original implementation
        try:
            logger.info("🔄 Attempting fallback method...")
            return await fetch_fallback_method(my_session, url)
        except Exception as e:
            logger.error(f"Fallback method failed: {e}")
            return None

async def fetch_with_method(session, url, method_name):
    """
    Fetch with specific method and timeout
    """
    try:
        async with session.get(url, timeout=25) as response:
            if response.status == 200:
                response_data = await response.text()
                
                # Extract tokens
                js_token = await find_between(response_data, 'fn%28%22', '%22%29')
                log_id = await find_between(response_data, 'dp-logid=', '&')
                
                if not js_token or not log_id:
                    return None
                
                surl = extract_surl_from_url(str(response.url))
                if not surl:
                    return None
                
                # Build API request
                api_url = 'https://www.1024tera.com/share/list'
                
                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '30' if IS_PREMIUM_ACCOUNT else '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': str(response.url),
                    'shorturl': surl,
                    'root': '1'
                }
                
                async with session.get(api_url, params=params, timeout=25) as list_response:
                    if list_response.status == 200:
                        data = await list_response.json()
                        if 'list' in data and data['list']:
                            return await process_file_list(session, data['list'], params, log_id)
                
        return None
        
    except Exception as e:
        logger.debug(f"Method {method_name} failed: {e}")
        return None

async def process_file_list(session, file_list, params, log_id):
    """
    Process file list and handle directories
    """
    try:
        first_item = file_list[0]
        
        # Handle directory
        if first_item.get('isdir') == "1":
            dir_params = params.copy()
            dir_params.update({
                'dir': first_item['path'],
                'order': 'asc',
                'by': 'name',
                'dplogid': log_id
            })
            dir_params.pop('desc', None)
            dir_params.pop('root', None)
            
            api_url = 'https://www.1024tera.com/share/list'
            async with session.get(api_url, params=dir_params, timeout=30) as dir_response:
                if dir_response.status == 200:
                    dir_data = await dir_response.json()
                    if 'list' in dir_data and dir_data['list']:
                        logger.info(f"📁 Directory processed with {len(dir_data['list'])} files")
                        return dir_data['list']
        
        logger.info(f"📄 Direct file list with {len(file_list)} files")
        return file_list
        
    except Exception as e:
        logger.error(f"Error processing file list: {e}")
        return file_list

async def fetch_fallback_method(session, url):
    """
    Fallback method using the original implementation
    """
    try:
        logger.info("🔄 Using original fallback method...")
        
        # Get the main page
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            response_data = await response.text()

        # Extract required tokens
        js_token = await find_between(response_data, 'fn%28%22', '%22%29')
        log_id = await find_between(response_data, 'dp-logid=', '&')

        if not js_token or not log_id:
            logger.error("Required tokens not found in fallback method.")
            return None

        request_url = str(response.url)
        surl = None
        
        # Try different methods to extract surl
        if 'surl=' in request_url:
            surl = request_url.split('surl=')[1].split('&')[0]
        elif '/s/' in request_url:
            surl = request_url.split('/s/')[1].split('?')[0]
        
        if not surl:
            logger.error("Could not extract surl parameter from URL in fallback")
            return None

        # Build API parameters
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

        # Make API request
        async with session.get('https://www.1024tera.com/share/list', params=params, timeout=30) as response2:
            response_data2 = await response2.json()
            if 'list' not in response_data2:
                logger.error("No list found in fallback response.")
                return None

            # Handle directory if needed
            if response_data2['list'][0]['isdir'] == "1":
                params.update({
                    'dir': response_data2['list'][0]['path'],
                    'order': 'asc',
                    'by': 'name',
                    'dplogid': log_id
                })
                params.pop('desc')
                params.pop('root')

                async with session.get('https://www.1024tera.com/share/list', params=params, timeout=30) as response3:
                    response_data3 = await response3.json()
                    if 'list' not in response_data3:
                        logger.error("No list found in nested directory response.")
                        return None
                    logger.info("Using file list from fallback method (nested directory)")
                    return response_data3['list']

            logger.info("Using file list from fallback method")
            return response_data2['list']

    except Exception as e:
        import traceback
        error_details = repr(e) if str(e) == "" else str(e)
        logger.error(f"Fallback method failed: {error_details}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
        return None


async def fetch_premium_api_method(session, url):
    """
    Premium-specific API method for faster link fetching
    """
    try:
        # Extract share info from URL
        surl = extract_surl_from_url(url)
        if not surl:
            return None
        
        # Premium API endpoints
        api_endpoints = [
            "https://www.terabox.com/api/share/list",
            "https://www.1024tera.com/api/share/list", 
            "https://premium.terabox.com/api/share/list"
        ]
        
        for api_url in api_endpoints:
            try:
                # Get page first for tokens
                async with session.get(url, timeout=20) as response:
                    if response.status != 200:
                        continue
                        
                    response_data = await response.text()
                    
                # Extract required tokens
                js_token = await find_between(response_data, 'fn%28%22', '%22%29')
                log_id = await find_between(response_data, 'dp-logid=', '&')
                
                if not js_token or not log_id:
                    continue
                
                # Premium API parameters
                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '50',  # More items for premium
                    'order': 'time',
                    'desc': '1',
                    'site_referer': str(response.url),
                    'shorturl': surl,
                    'root': '1',
                    'premium': '1' if IS_PREMIUM_ACCOUNT else '0'
                }
                
                # Make API request
                async with session.get(api_url, params=params, timeout=30) as api_response:
                    if api_response.status == 200:
                        try:
                            data = await api_response.json()
                            if 'list' in data and data['list']:
                                logger.info(f"🚀 Premium API success with {len(data['list'])} files")
                                return await process_file_list(session, data['list'], params, log_id)
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.debug(f"Premium API endpoint {api_url} failed: {e}")
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Premium API method error: {e}")
        return None


async def fetch_download_link_async(url):
    """
    Enhanced TeraBox link fetcher optimized for premium accounts
    Attempts multiple methods to get the fastest download links
    """
    encoded_url = urllib.parse.quote(url)
    
    # Enhanced session configuration for premium
    connector_config = {
        'ssl': False,
        'limit': 100,
        'limit_per_host': 50,
        'ttl_dns_cache': 300,
        'use_dns_cache': True,
    }
    
    timeout_config = aiohttp.ClientTimeout(
        total=60,
        connect=15,
        sock_read=30
    )
    
    async with aiohttp.ClientSession(
        cookies=my_cookie,
        timeout=timeout_config,
        connector=aiohttp.TCPConnector(**connector_config)
    ) as my_session:
        
        # Enhanced headers for premium access
        premium_headers = my_headers.copy()
        if IS_PREMIUM_ACCOUNT:
            premium_headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Priority': 'u=1, i',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            })
        
        my_session.headers.update(premium_headers)
        
        # Method 1: Premium API endpoint (fastest for premium users)
        if IS_PREMIUM_ACCOUNT:
            try:
                logger.info("🚀 Attempting premium API method...")
                premium_result = await fetch_premium_api_method(my_session, url)
                if premium_result:
                    logger.info("✅ Premium API method successful!")
                    return await optimize_download_links(premium_result)
            except Exception as e:
                logger.warning(f"Premium API method failed: {e}")
        
        # Method 2: Enhanced standard method with optimizations
        try:
            logger.info("📡 Attempting enhanced standard method...")
            
            # Create tasks properly
            tasks = []
            
            # Primary request
            tasks.append(asyncio.create_task(fetch_with_method(my_session, url, "primary")))
            
            # Alternative endpoints for premium users
            if IS_PREMIUM_ACCOUNT:
                alt_urls = [
                    url.replace('terabox.com', '1024tera.com'),
                    url.replace('terabox.com', 'teraboxapp.com'),
                    url.replace('terabox.com', 'nephobox.com')
                ]
                
                for alt_url in alt_urls:
                    tasks.append(asyncio.create_task(fetch_with_method(my_session, alt_url, "alternative")))
            
            # Fixed concurrent execution
            try:
                # Wait for first successful result
                done, pending = await asyncio.wait(
                    tasks, 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=45
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
                # Process completed tasks
                for task in done:
                    try:
                        result = await task
                        if result:
                            logger.info("✅ Enhanced method successful!")
                            return await optimize_download_links(result)
                    except Exception as e:
                        logger.debug(f"Task failed: {e}")
                        continue
                        
            except asyncio.TimeoutError:
                logger.warning("⏰ Enhanced method timed out")
                # Cancel all tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
            except Exception as e:
                logger.error(f"Enhanced method failed: {e}")
                # Cancel all tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass
                        
        except Exception as e:
            logger.error(f"Enhanced method setup failed: {e}")
        
        # Method 3: Fallback with original implementation
        try:
            logger.info("🔄 Attempting fallback method...")
            return await fetch_fallback_method(my_session, url)
        except Exception as e:
            logger.error(f"All methods failed: {e}")
            return None

async def fetch_with_method(session, url, method_name):
    """
    Fetch with specific method and timeout
    """
    try:
        async with session.get(url, timeout=25) as response:
            if response.status == 200:
                response_data = await response.text()
                
                # Extract tokens
                js_token = await find_between(response_data, 'fn%28%22', '%22%29')
                log_id = await find_between(response_data, 'dp-logid=', '&')
                
                if not js_token or not log_id:
                    return None
                
                surl = extract_surl_from_url(str(response.url))
                if not surl:
                    return None
                
                # Build API request
                api_url = 'https://www.1024tera.com/share/list'
                
                params = {
                    'app_id': '250528',
                    'web': '1',
                    'channel': 'dubox',
                    'clienttype': '0',
                    'jsToken': js_token,
                    'dplogid': log_id,
                    'page': '1',
                    'num': '30' if IS_PREMIUM_ACCOUNT else '20',
                    'order': 'time',
                    'desc': '1',
                    'site_referer': str(response.url),
                    'shorturl': surl,
                    'root': '1'
                }
                
                async with session.get(api_url, params=params, timeout=25) as list_response:
                    if list_response.status == 200:
                        data = await list_response.json()
                        if 'list' in data and data['list']:
                            return await process_file_list(session, data['list'], params, log_id)
                
        return None
        
    except Exception as e:
        logger.debug(f"Method {method_name} failed: {e}")
        return None

async def process_file_list(session, file_list, params, log_id):
    """
    Process file list and handle directories
    """
    try:
        first_item = file_list[0]
        
        # Handle directory
        if first_item.get('isdir') == "1":
            dir_params = params.copy()
            dir_params.update({
                'dir': first_item['path'],
                'order': 'asc',
                'by': 'name',
                'dplogid': log_id
            })
            dir_params.pop('desc', None)
            dir_params.pop('root', None)
            
            api_url = 'https://www.1024tera.com/share/list'
            async with session.get(api_url, params=dir_params, timeout=30) as dir_response:
                if dir_response.status == 200:
                    dir_data = await dir_response.json()
                    if 'list' in dir_data and dir_data['list']:
                        logger.info(f"📁 Directory processed with {len(dir_data['list'])} files")
                        return dir_data['list']
        
        logger.info(f"📄 Direct file list with {len(file_list)} files")
        return file_list
        
    except Exception as e:
        logger.error(f"Error processing file list: {e}")
        return file_list

def extract_surl_from_url(url):
    """
    Enhanced surl extraction with multiple patterns
    """
    try:
        # Method 1: URL parameter
        if 'surl=' in url:
            return url.split('surl=')[1].split('&')[0]
        
        # Method 2: Path-based
        if '/s/' in url:
            return url.split('/s/')[1].split('?')[0].split('/')[0]
        
        # Method 3: Alternative patterns
        patterns = [
            r'/s/([^/?]+)',
            r'surl=([^&]+)',
            r'/share/link\?surl=([^&]+)',
            r'#surl=([^&]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting surl: {e}")
        return None

async def optimize_download_links(file_list):
    """
    Optimize download links for premium accounts
    """
    if not file_list or not IS_PREMIUM_ACCOUNT:
        return file_list
    
    try:
        optimized_list = []
        
        for file_item in file_list:
            if 'dlink' in file_item:
                original_link = file_item['dlink']
                
                # Try to get premium CDN links
                optimized_link = await get_premium_cdn_link(original_link)
                
                if optimized_link != original_link:
                    file_item['dlink'] = optimized_link
                    file_item['optimized'] = True
                    logger.info(f"🚀 Optimized link for: {file_item.get('server_filename', 'file')}")
                
            optimized_list.append(file_item)
        
        return optimized_list
        
    except Exception as e:
        logger.error(f"Error optimizing download links: {e}")
        return file_list


async def get_premium_cdn_link(original_link):
    """
    Get premium CDN link for faster downloads
    """
    try:
        parsed_url = urllib.parse.urlparse(original_link)
        
        # Premium CDN servers (try in order of preference)
        premium_cdns = [
            "premium-dl.terabox.com",
            "fast-dl.terabox.com", 
            "cdn-premium.terabox.com",
            "dl-premium.1024tera.com",
            "speed.terabox.com",
            "turbo.terabox.com",
            "express.1024tera.com"
        ]
        
        # Test each CDN for availability and speed
        fastest_link = original_link
        fastest_response_time = float('inf')
        
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(
            cookies=my_cookie,
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            session.headers.update(my_headers)
            
            for cdn in premium_cdns:
                try:
                    # Replace hostname with CDN
                    test_url = original_link.replace(parsed_url.netloc, cdn)
                    
                    # Test with HEAD request for speed
                    start_time = time.time()
                    async with session.head(test_url, timeout=8) as response:
                        if response.status in [200, 206, 302, 301]:
                            response_time = time.time() - start_time
                            
                            if response_time < fastest_response_time:
                                fastest_response_time = response_time
                                fastest_link = test_url
                                logger.info(f"🚀 Found faster CDN: {cdn} ({response_time:.2f}s)")
                            
                            # If we find a very fast CDN, use it immediately
                            if response_time < 0.5:
                                logger.info(f"⚡ Using ultra-fast CDN: {cdn}")
                                return test_url
                                
                except Exception as e:
                    logger.debug(f"CDN test failed for {cdn}: {e}")
                    continue
        
        # If we found a faster CDN, return it
        if fastest_link != original_link:
            logger.info(f"✅ Optimized CDN selected with {fastest_response_time:.2f}s response time")
        
        return fastest_link
        
    except Exception as e:
        logger.error(f"Error optimizing CDN link: {e}")
        return original_link

async def test_download_speed(url, test_duration=5):
    """
    Test download speed for a given URL
    """
    try:
        timeout = aiohttp.ClientTimeout(total=test_duration + 5)
        
        async with aiohttp.ClientSession(
            cookies=my_cookie,
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            session.headers.update(my_headers)
            session.headers['Range'] = 'bytes=0-5242880'  # Test with 5MB
            
            start_time = time.time()
            bytes_downloaded = 0
            
            async with session.get(url) as response:
                if response.status in [200, 206]:
                    async for chunk in response.content.iter_chunked(8192):
                        bytes_downloaded += len(chunk)
                        
                        # Stop after test duration
                        if time.time() - start_time >= test_duration:
                            break
            
            elapsed_time = time.time() - start_time
            speed = bytes_downloaded / elapsed_time if elapsed_time > 0 else 0
            
            return speed
            
    except Exception as e:
        logger.debug(f"Speed test failed: {e}")
        return 0

async def get_best_download_server(file_list):
    """
    Find the best download server for premium accounts
    """
    if not file_list or not IS_PREMIUM_ACCOUNT:
        return file_list
    
    try:
        optimized_files = []
        
        for file_item in file_list:
            if 'dlink' not in file_item:
                optimized_files.append(file_item)
                continue
            
            original_link = file_item['dlink']
            
            # Test multiple server variations
            server_variations = [
                original_link,
                original_link.replace('d.docs.live.net', 'premium.docs.live.net'),
                original_link.replace('public.', 'premium.'),
                original_link.replace('api.', 'premium-api.'),
                await get_premium_cdn_link(original_link)
            ]
            
            # Remove duplicates
            server_variations = list(set(server_variations))
            
            best_link = original_link
            best_speed = 0
            
            # Test each server variation
            for server_url in server_variations:
                try:
                    speed = await test_download_speed(server_url, test_duration=3)
                    if speed > best_speed:
                        best_speed = speed
                        best_link = server_url
                        logger.info(f"🚀 Better server found: {format_size(speed)}/s")
                        
                except Exception as e:
                    logger.debug(f"Server test failed: {e}")
                    continue
            
            # Update file item with best link
            if best_link != original_link:
                file_item['dlink'] = best_link
                file_item['optimized_speed'] = best_speed
                logger.info(f"✅ Optimized server for {file_item.get('server_filename', 'file')}")
            
            optimized_files.append(file_item)
        
        return optimized_files
        
    except Exception as e:
        logger.error(f"Error finding best download server: {e}")
        return file_list

# Add global variable for premium account status
IS_PREMIUM_ACCOUNT = False

# Enhanced initialization function
async def initialize_premium_system():
    """
    Initialize premium system with enhanced detection
    """
    global IS_PREMIUM_ACCOUNT
    
    try:
        # Test cookie functionality
        if my_cookie:
            # Simple premium detection based on cookie analysis
            premium_indicators = [
                'TSID' in my_cookie,
                'csrfToken' in my_cookie,
                len(my_cookie.get('browserid', '')) > 50,
                'ndut_fmt' in my_cookie
            ]
            
            if sum(premium_indicators) >= 3:
                IS_PREMIUM_ACCOUNT = True
                logger.info("🚀 PREMIUM ACCOUNT DETECTED!")
                logger.info(f"Premium indicators found: {sum(premium_indicators)}/4")
            else:
                IS_PREMIUM_ACCOUNT = False
                logger.info("📝 Standard account detected")
        else:
            IS_PREMIUM_ACCOUNT = False
            logger.warning("No cookies configured")
            
    except Exception as e:
        logger.error(f"Error initializing premium system: {e}")
        IS_PREMIUM_ACCOUNT = False




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


async def download_thumbnail(url, save_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(save_path, "wb") as f:
                    f.write(await resp.read())
                return save_path
    return None

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

    thumb_url = None
    if isinstance(link_data, list) and link_data:
        thumbs = link_data[0].get("thumbs", {})

        thumb_url = thumbs.get("url3") or thumbs.get("url2") or thumbs.get("url1") or thumbs.get("icon")

    

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
        options=options
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
        emojis = ["💀", "👾", "🤖", "🧠", "🚀", "⚡", "🔥"]
        progress_bar = "".join(random.choices(emojis, k=filled_bars)) + "▫️" * empty_bars
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
            f"📛 <code><b>{truncated_name}</b></code>\n"
            f"🎲 <code><b>{progress:.2f}%</b></code>\n"
            f"🐾 <code> <b>{format_size(download.completed_length)}</b> / {format_size(download.total_length)}</code>\n"
            f"{speed_icon} <b>{format_size(speed)}/s</b> | ⏳ ETA: <b>{eta}</b>\n"
            f" <i>{current_status}</i>\n"
            f"👤 <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
            )
        while True:
            try:
                # first_dlink = link_data[0].get("dlink", "https://t.me/jffmain")
                await update_status_message(
                    status_message,
                    status_text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Cᴀɴᴄᴇʟ 🚫", callback_data=f"cancel_{download.gid}"),
                         InlineKeyboardButton("🔗 Dɪʀᴇᴄᴛ Lɪɴᴋ", url=direct_link)]
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
            [InlineKeyboardButton("⚡ Cʜᴀɴɴᴇʟ",url="https://t.me/+8NE_GtI0UQZiZjc1")]  # Add button with callback data
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
        global download_count, total_download_size
        file_size = os.path.getsize(file_path)
        part_caption = caption

        upload_as_video = True
        duration, width, height = 0, 0, 0

        thumb_path = None

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
                    thumb_path = None
                    if thumb_url:
                        thumb_path = f"/tmp/terabox_thumb_{user_id}.jpg"
                        await download_thumbnail(thumb_url, thumb_path)
          
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
                            thumb=thumb_path if thumb_path else None,
                            disable_notification=True,
                            has_spoiler=True,
                            request_timeout=3600
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
                            thumb=thumb_path if thumb_path else None,
                            duration=duration,
                            has_spoiler=True,
                        )
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            width=width,
                            height=height,
                            duration=duration,
                            has_spoiler=True,
                            thumb=thumb_path if thumb_path else None,
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
                        thumb=thumb_path if thumb_path else None,
                        has_spoiler=True,
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
                                thumb=thumb_path if thumb_path else None,
                                has_spoiler=True,
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
                                has_spoiler=True,
                                thumb=thumb_path if thumb_path else None,
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
                        has_spoiler=True,
                        thumb=thumb_path if thumb_path else None,
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
                        has_spoiler=True,
                        thumb=thumb_path if thumb_path else None,
                    )
                    try:
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption,
                            reply_markup=caption_btn,
                            width=width,
                            height=height,
                            duration=duration,
                            has_spoiler=True,
                            thumb=thumb_path if thumb_path else None,
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
                            has_spoiler=True,
                            thumb=thumb_path if thumb_path else None,
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
                        has_spoiler=True,
                        thumb=thumb_path if thumb_path else None,
                    )

        if os.path.exists(file_path):
            os.remove(file_path)

        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

        await message.reply_sticker("CAACAgUAAxkBAAEBOQVoBLWRUSRCieoGNbvQ5cJ1U8qtWgACKg0AAprJqVcDgujJs5TjwTYE")
        # await message.reply_text("✅ Uᴘʟᴏᴀᴅ ᴄᴏᴍᴘʟᴇᴛᴇᴅ! Eɴᴊᴏʏ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛ. 😎")
        download_count += 1
        total_download_size += file_size

        db.get_collection("stats").update_one(  
           {"_id": "download_stats"},
           {
               "$inc": {"count": 1, "total_size": file_size},
               "$push": {"recent_downloads": datetime.now()}
            },
            upsert=True
        )
        collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"downloads": 1, "total_downloaded": file_size},
                "$set": {"last_download": datetime.now()}
            }
        )
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
        # logger.info(f"Bot access to dump channel: {chat.title}, permissions: {bot_member.privileges}")
        
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
    global download_count, total_download_size
    await initialize_premium_system()
    stats_doc = db.get_collection("stats").find_one({"_id": "download_stats"})
    if stats_doc:
        download_count = stats_doc.get("count", 0)
        total_download_size = stats_doc.get("total_size", 0)
    # Start the web server
    await web_server()
    logger.info("Web server started")
    
    # Start the bot
    await app.start()
    logger.info("Bot client started")
    await initialize_premium_cookies()
    
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
        premium_status = "🚀 PREMIUM" if IS_PREMIUM_ACCOUNT else "📝 STANDARD"
        await app.send_message(
            OWNER_ID,
            f"✅ **Bᴏᴛ Sᴛᴀʀᴛᴇᴅ Sᴜᴄᴄᴇssfᴜʟʏ!**\n\n"
            f"🕒 **Tɪᴍᴇ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🖥️ **Sᴇʀᴠᴇʀ:** {platform.node()}\n"
            f"🍪 **Aᴄᴄᴏᴜɴᴛ Tʏᴘᴇ:** {premium_status}\n"
            f"💾 **Uѕᴇʀ Sᴇssɪᴏɴ:** {'✅ Aᴄᴛɪᴠᴇ' if USER_SESSION_STRING else '❌ Nᴏᴛ cᴏɴғɪɢᴜʀᴇᴅ'}\n"
            f"🔄 **Mᴀx Uᴘʟᴏᴀᴅ Sɪᴢᴇ:** {format_size(SPLIT_SIZE)}\n\n"
            f"Bᴏᴛ ɪs nᴏᴡ ʀᴇᴀᴅʏ tᴏ prᴏᴄᴇss Tᴇʀᴀbᴏx lɪɴᴋs!"
        )
        logger.info(f"Startup notification sent to owner: {OWNER_ID}")
    except Exception as e:
        logger.error(f"Failed to send startup notification to owner: {e}")
    
    # Keep the program running
    await idle()



@app.on_message(filters.command("info"))
async def user_info_command(client: Client, message: Message):
    """Command to get information about a user"""
    # Check if admin is requesting info about another user
    is_admin = message.from_user.id in ADMINS
    target_user_id = None
    
    # If admin is requesting info about another user via reply
    if message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = message.reply_to_message.from_user.id
    # If user ID is provided in command
    elif len(message.command) > 1:
        try:
            target_user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ.")
            return
    # If admin and no ID provided, ask for user ID
    elif is_admin:
        # Create a message to ask for user ID
        ask_msg = await message.reply_text(
            "🔍 ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʜᴇᴄᴋ:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_info")]
            ])
        )
        
        # Store this in a global dictionary to track waiting states
        if not hasattr(app, 'waiting_for_input'):
            app.waiting_for_input = {}
        
        app.waiting_for_input[message.from_user.id] = {
            'type': 'info_user_id',
            'message_id': ask_msg.id,
            'chat_id': message.chat.id,
            'timestamp': time.time()
        }
        
        # We'll return here and handle the response in a separate handler
        return
    else:
        # User is requesting their own info
        target_user_id = message.from_user.id
    
    # Continue with displaying user info...
    await display_user_info(client, message, target_user_id)

# Add a handler for text messages that could be responses to our prompts
@app.on_message(filters.text & filters.private)
async def handle_text_input(client: Client, message: Message):
    # Check if this user is waiting for input
    if hasattr(app, 'waiting_for_input') and message.from_user.id in app.waiting_for_input:
        input_data = app.waiting_for_input[message.from_user.id]
        
        # Check if the input is still valid (not expired)
        if time.time() - input_data['timestamp'] > 60:  # 60 seconds timeout
            del app.waiting_for_input[message.from_user.id]
            try:
                await client.delete_messages(input_data['chat_id'], input_data['message_id'])
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
            await message.reply_text("⏱️ ᴛɪᴍᴇᴏᴜᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.")
            return
        
        # Handle different types of expected input
        if input_data['type'] == 'info_user_id':
            # Try to parse the user ID
            try:
                target_user_id = int(message.text.strip())
                
                # Clean up
                del app.waiting_for_input[message.from_user.id]
                try:
                    await client.delete_messages(input_data['chat_id'], input_data['message_id'])
                except Exception as e:
                    logger.error(f"Error deleting message: {e}")
                
                # Display user info
                await display_user_info(client, message, target_user_id)
            except ValueError:
                await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ɪᴅ.")
                return
        
        # Don't process this message further
        return

# Add a callback handler for the cancel button
@app.on_callback_query(filters.regex("^cancel_info$"))
async def cancel_info_request(client, callback_query):
    user_id = callback_query.from_user.id
    
    if hasattr(app, 'waiting_for_input') and user_id in app.waiting_for_input:
        del app.waiting_for_input[user_id]
    
    await callback_query.message.delete()
    await callback_query.answer("ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")

# Separate function to display user info
async def display_user_info(client, message, target_user_id):
    """Display information about a user"""
    is_admin = message.from_user.id in ADMINS
    
    # Get user data from database
    user_data = collection.find_one({"user_id": target_user_id})
    
    if not user_data and not is_admin:
        # If no data found for self-lookup, create basic entry
        user_data = {
            "user_id": target_user_id,
            "created_at": datetime.now(),
            "token_status": "inactive",
            "downloads": 0,
            "total_download_size": 0
        }
        collection.insert_one(user_data)
    elif not user_data and is_admin:
        await message.reply_text(f"❌ ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ ғᴏʀ ᴜsᴇʀ ɪᴅ: `{target_user_id}`")
        return
    
    # Get user info from Telegram
    try:
        user = await client.get_users(target_user_id)
        username = f"@{user.username}" if user.username else "ɴᴏɴᴇ"
        full_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        username = "ᴜɴᴋɴᴏᴡɴ"
        full_name = "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
    
    # Format user information
    created_at = user_data.get("created_at", "ᴜɴᴋɴᴏᴡɴ")
    if isinstance(created_at, datetime):
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    token_status = user_data.get("token_status", "inactive")
    token_expiry = user_data.get("token_expiry")
    if token_expiry and isinstance(token_expiry, datetime):
        if token_expiry > datetime.now():
            token_expiry_str = f"ᴇxᴘɪʀᴇs: {token_expiry.strftime('%Y-%m-%d %H:%M:%S')}"
            time_left = token_expiry - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            token_expiry_str += f" ({time_left.days}ᴅ {hours}ʜ {minutes}ᴍ ʟᴇғᴛ)"
        else:
            token_expiry_str = "ᴇxᴘɪʀᴇᴅ"
    else:
        token_expiry_str = "ɴ/ᴀ"
    
    downloads = user_data.get("downloads", 0)
    total_download_size = format_size(user_data.get("total_download_size", 0))
    last_download = user_data.get("last_download")
    if last_download and isinstance(last_download, datetime):
        last_download = last_download.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_download = "ɴᴇᴠᴇʀ"
    
    pending_requests = user_data.get("pending_requests", [])
    pending_count = len(pending_requests) if pending_requests else 0
    
    # Create info message with small caps
    info_text = (
        f"📊 <b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b> 📊\n\n"
        f"<b>🆔 ᴜsᴇʀ ɪᴅ:</b> <code>{target_user_id}</code>\n"
        f"<b>👤 ɴᴀᴍᴇ:</b> {full_name}\n"
        f"<b>🔖 ᴜsᴇʀɴᴀᴍᴇ:</b> {username}\n"
        f"<b>📅 ᴊᴏɪɴᴇᴅ:</b> {created_at}\n\n"
        
        f"<b>🔑 ᴛᴏᴋᴇɴ sᴛᴀᴛᴜs:</b> {'✅ ᴀᴄᴛɪᴠᴇ' if token_status == 'active' else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}\n"
        f"<b>⏳ ᴛᴏᴋᴇɴ ᴇxᴘɪʀʏ:</b> {token_expiry_str}\n\n"
        
        f"<b>📈 ᴀᴄᴛɪᴠɪᴛʏ:</b>\n"
        f"<b>• ᴅᴏᴡɴʟᴏᴀᴅs:</b> {downloads}\n"
        f"<b>• ᴛᴏᴛᴀʟ sɪᴢᴇ:</b> {total_download_size}\n"
        f"<b>• ʟᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ:</b> {last_download}\n"
        f"<b>• ᴘᴇɴᴅɪɴɢ ʀᴇǫᴜᴇsᴛs:</b> {pending_count}\n"
    )
    
    # Add admin options if admin is viewing another user
    if is_admin and target_user_id != message.from_user.id:
        keyboard = [
            [InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data=f"refresh_info_{target_user_id}")],
            [
                InlineKeyboardButton("🔑 ᴀᴄᴛɪᴠᴀᴛᴇ ᴛᴏᴋᴇɴ", callback_data=f"activate_token_{target_user_id}"),
                InlineKeyboardButton("🚫 ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇ ᴛᴏᴋᴇɴ", callback_data=f"deactivate_token_{target_user_id}")
            ],
            [InlineKeyboardButton("❌ ᴅᴇʟᴇᴛᴇ ᴜsᴇʀ", callback_data=f"delete_user_{target_user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = None
    
    await message.reply_text(info_text, reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"^refresh_info_(\d+)$"))
async def refresh_info_callback(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    # Create a message object with the necessary attributes
    message = callback_query.message
    message.command = ["info", str(user_id)]
    message.from_user = callback_query.from_user
    
    # Call the display_user_info function directly
    await display_user_info(client, message, user_id)
    
    # Delete the original message to avoid clutter
    await callback_query.message.delete()

@app.on_callback_query(filters.regex(r"^activate_token_(\d+)$"))
async def activate_user_token(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    # Generate and activate token
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(hours=12)
    
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"token": token, "token_status": "active", "token_expiry": expiry}},
        upsert=True
    )
    
    await callback_query.answer("ᴛᴏᴋᴇɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!", show_alert=True)
    
    # Refresh the info display
    message = callback_query.message
    message.command = ["info", str(user_id)]
    message.from_user = callback_query.from_user
    await display_user_info(client, message, user_id)
    await callback_query.message.delete()

@app.on_callback_query(filters.regex(r"^deactivate_token_(\d+)$"))
async def deactivate_user_token(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"token_status": "inactive"}}
    )
    
    await callback_query.answer("ᴛᴏᴋᴇɴ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!", show_alert=True)
    
    # Refresh the info display
    message = callback_query.message
    message.command = ["info", str(user_id)]
    message.from_user = callback_query.from_user
    await display_user_info(client, message, user_id)
    await callback_query.message.delete()

@app.on_callback_query(filters.regex(r"^delete_user_(\d+)$"))
async def delete_user_data(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    # Confirm deletion with a new keyboard
    confirm_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ʏᴇs, ᴅᴇʟᴇᴛᴇ", callback_data=f"confirm_delete_{user_id}"),
            InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"cancel_delete_{user_id}")
        ]
    ])
    
    await callback_query.message.edit_text(
        f"⚠️ ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴅᴀᴛᴀ ғᴏʀ ᴜsᴇʀ ɪᴅ: `{user_id}`?\n\n"
        "ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.",
        reply_markup=confirm_keyboard
    )

@app.on_callback_query(filters.regex(r"^confirm_delete_(\d+)$"))
async def confirm_delete_user(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    # Delete user data
    result = collection.delete_one({"user_id": user_id})
    
    if result.deleted_count > 0:
        await callback_query.message.edit_text(f"✅ ᴜsᴇʀ ᴅᴀᴛᴀ ғᴏʀ ɪᴅ: `{user_id}` ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ.")
    else:
        await callback_query.message.edit_text(f"❌ ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ ғᴏʀ ᴜsᴇʀ ɪᴅ: `{user_id}`.")

@app.on_callback_query(filters.regex(r"^cancel_delete_(\d+)$"))
async def cancel_delete_user(client, callback_query):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True)
    
    user_id = int(callback_query.data.split("_")[2])
    
    # Go back to user info display
    message = callback_query.message
    message.command = ["info", str(user_id)]
    message.from_user = callback_query.from_user
    await display_user_info(client, message, user_id)
    await callback_query.message.delete()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


