import asyncio
from pyrogram import Client

async def main():
    print("Generating new session string...")
    
    # Get API credentials
    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API HASH: ")
    
    # Create a temporary client
    async with Client(
        "my_account",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    ) as app:
        # Get the session string
        session_string = await app.export_session_string()
        print("\nYour session string is:")
        print(session_string)
        print("\nKeep this string secure and use it in your USER_SESSION_STRING environment variable.")

if __name__ == "__main__":
    asyncio.run(main())
