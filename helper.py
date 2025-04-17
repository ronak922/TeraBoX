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

async def get_video_dimensions(video_path):
    try:
        # Check if the file exists first
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None, None
            
        # Try different ffprobe commands based on platform
        if os.name == 'nt':  # Windows
            # Try with full path if ffprobe is installed with FFmpeg
            ffprobe_paths = [
                'ffprobe',
                r'C:\ffmpeg\bin\ffprobe.exe',
                os.path.join(os.environ.get('PROGRAMFILES', r'C:\Program Files'), r'ffmpeg\bin\ffprobe.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'), r'ffmpeg\bin\ffprobe.exe')
            ]
            
            for ffprobe_path in ffprobe_paths:
                try:
                    cmd = [
                        ffprobe_path, '-v', 'error', 
                        '-select_streams', 'v:0', 
                        '-show_entries', 'stream=width,height', 
                        '-of', 'csv=p=0', 
                        video_path
                    ]
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    if stdout:
                        dimensions = stdout.decode().strip().split(',')
                        if len(dimensions) == 2:
                            return int(dimensions[0]), int(dimensions[1])
                    # If we get here, this path didn't work
                except Exception as e:
                    logger.debug(f"Tried ffprobe path {ffprobe_path}: {e}")
                    continue
        else:  # Linux/Mac
            cmd = [
                'ffprobe', '-v', 'error', 
                '-select_streams', 'v:0', 
                '-show_entries', 'stream=width,height', 
                '-of', 'csv=p=0', 
                video_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if stdout:
                dimensions = stdout.decode().strip().split(',')
                if len(dimensions) == 2:
                    return int(dimensions[0]), int(dimensions[1])
                    
        # If we get here, we couldn't get dimensions with ffprobe
        # Let's use a fallback method - default dimensions
        logger.warning(f"Could not get video dimensions with ffprobe, using default values")
        return 1280, 720  # Standard HD dimensions as fallback
        
    except Exception as e:
        logger.error(f"Error getting video dimensions: {e}")
        return 1280, 720  # Return default dimensions on error
