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
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from pyrogram import Client, filters, idle

from pymongo import MongoClient
import time
import threading
import uuid
import urllib.parse
from urllib.parse import urlparse
import requests
import os 
import asyncio
import logging


logger = logging.getLogger(__name__)

import asyncio

async def get_video_dimensions(video_path):
    try:
        # Running ffprobe in an async subprocess
        process = await asyncio.create_subprocess_exec(
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', video_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Await the process to get output
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(f"Error from ffprobe: {stderr.decode()}")
            return 1280, 720  # Default resolution if ffprobe fails

        # Parsing the width and height from the output
        width, height = map(int, stdout.decode().strip().split('x'))
        return width, height

    except Exception as e:
        print(f"Error getting video dimensions: {e}")
        return 1280, 720
