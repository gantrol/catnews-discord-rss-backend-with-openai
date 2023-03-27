import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from app import crud, models
from app.database import get_db
from app.schemas import FeedCreate

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_API")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.command(name="sub")
async def sub(ctx, url: str):
    if not url:
        await ctx.send("Check again. Usage: sub <url>")
        return

    # TODO: 更精细的异常处理
    def func(db, current_user):
        try:
            feed = FeedCreate(url=url)
            subscribed_feed = crud.subscribe_to_feed(feed, current_user, db)
            if subscribed_feed:
                message = f"Subscribed to {url}"
            else:
                message = f"Error subscribing to {url} for empty"
        except Exception as e:
            logging.error(f"Error subscribing to {url}: {e}")
            message = f"Error subscribing to {url}: {str(e)}"
        return message

    message = login_check_helper(ctx, func)
    await ctx.send(message)


@bot.command(name="list")
async def list_subs(ctx):
    def func(db, current_user):
        subscriptions = crud.list_subscribed_feeds(current_user, db)
        if subscriptions:
            message = "Your subscriptions:\n"
            for subscription in subscriptions:
                message += f"- {subscription.title} ({subscription.url})\n"
        else:
            message = "You have no subscriptions."
        return message

    message = login_check_helper(ctx, func)
    await ctx.send(message)


@bot.command(name="news")
async def get_news(ctx):
    # TODO: 对接AI？
    # TODO: discord显示卡片有点烦人？
    # TODO: check discord.ext.commands.errors.CommandInvokeError: Command raised an exception: HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
    #    In content: Must be 2000 or fewer in length.
    def func(db, current_user):
        try:
            articles: [models.Article] = crud.get_feed_articles(current_user, db, skip=0, limit=10)
            if articles:
                message = "Latest articles:\n"
                for article in articles:
                    message += f"- {article.title} ({article.url})\n"
            else:
                message = "No articles found."
        except Exception as e:
            message = "Error fetching articles."
            logging.error(e)
        return message

    message = login_check_helper(ctx, func)
    await ctx.send(message)


def login_check_helper(ctx, func):
    db = next(get_db())
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)
    if current_user:
        message = func(db, current_user)
    else:
        message = "Please signup with discord first. https://discord-rss-backend-production.up.railway.app/auth/discord"
    return message


@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} has connected to Discord!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
