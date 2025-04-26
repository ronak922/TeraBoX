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


async def get_video_metadata(video_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-of', 'json',
            video_path
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if stdout:
            import json
            info = json.loads(stdout.decode())
            stream = info.get('streams', [{}])[0]
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
            duration = float(stream.get('duration', 0))
            return width, height, int(duration)
    except Exception as e:
        logger.error(f"Error getting video metadata: {e}")
    return None, None, None

import asyncio
import ffmpeg

async def screenshot(file_path, duration):
    try:
        thumb_path = f"{file_path}_thumb.jpg"
        
        # Use ffmpeg to capture a screenshot at the middle of the video
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', file_path,
            '-ss', str(duration // 2),  # Capture at half the video's duration
            '-vframes', '1',            # Capture one frame
            '-q:v', '2',                # Quality level (lower is better)
            thumb_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Check if there was an error
        if process.returncode != 0:
            print(f"FFmpeg error: {stderr.decode()}")
            return None
        return thumb_path
    except Exception as e:
        print(f"Error generating screenshot: {e}")
        return None


async def generate_thumbnail(video_path, output_thumb_path):
    try:
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-ss', '00:00:01.000', '-vframes', '1',
            output_thumb_path
        ]
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()
        return output_thumb_path if os.path.exists(output_thumb_path) else None
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return None
    

async def get_video_info(video_path):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if stdout:
            info = stdout.decode().strip().split('\n')
            width, height, duration = map(float, info)
            return int(width), int(height), int(duration)
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
    return None, None, None

