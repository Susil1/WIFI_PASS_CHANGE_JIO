import asyncio

from bot.app import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        pass