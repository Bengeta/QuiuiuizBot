import nest_asyncio
import asyncio
from database_manager import prepare_db
from bot import start_bot

nest_asyncio.apply()

async def main():
   await prepare_db()
   await start_bot()

if __name__ == "__main__":
    asyncio.run(main())