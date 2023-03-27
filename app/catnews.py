import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import Depends
from requests import Session

from app import crud, models
from app.database import get_db
from app.schemas import FeedCreate

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_API")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="", intents=intents)


@bot.command(name="sub")
async def sub(ctx, url: str, db: Session = Depends(get_db)):
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)
    feed = FeedCreate()
    feed.url = url
    # TODO: 更精细的异常处理
    try:
        subscribed_feed = crud.subscribe_to_feed(feed, current_user, db)
        if subscribed_feed:
            await ctx.send(f"Subscribed to {url}")
        else:
            await ctx.send(f"Error subscribing to {url} for empty")
    except Exception as e:
        logging.error(f"Error subscribing to {url}: {e}")
        await ctx.send(f"Error subscribing to {url}: {str(e)}")


@bot.command(name="list")
async def list_subs(ctx, db: Session = Depends(get_db)):
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)

    subscriptions = crud.list_subscribed_feeds(current_user, db)
    if subscriptions:
        message = "Your subscriptions:\n"
        for subscription in subscriptions:
            message += f"- {subscription['title']} ({subscription['url']})\n"
    else:
        message = "You have no subscriptions."

    await ctx.send(message)


@bot.command(name="news")
async def get_news(ctx, db: Session = Depends(get_db)):
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)
    # TODO: 对接AI？
    # TODO: discord显示卡片有点烦人？

    try:
        articles: [models.Article] = crud.get_feed_articles(current_user, db, skip=0, limit=20)
        if articles:
            message = "Latest articles:\n"
            for article in articles:
                message += f"- {article.title} ({article.url})\n"
        else:
            message = "No articles found."
    except Exception as e:
        message = "Error fetching articles."
        logging.error(e)

    await ctx.send(message)


@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} has connected to Discord!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
