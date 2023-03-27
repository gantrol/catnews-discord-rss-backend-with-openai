import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from app import crud, models
from app.database import get_db
from app.schemas import FeedCreate, FeedRemove

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_API")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

COMMAND_PREFIX = "/"

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.command(name="sub", help=f"Subscribes by url. Usage: {COMMAND_PREFIX}sub <url>")
async def sub(ctx, url: str):
    # TODO: 更精细的异常处理
    async def func(db, current_user):
        try:
            feed = FeedCreate(url=url)
            subscribed_feed = crud.subscribe_to_feed(feed, current_user, db)
            if subscribed_feed:
                message = f"Subscribed to {subscribed_feed.url}"
            else:
                message = f"Error subscribing to {url} for empty"
        except Exception as e:
            logging.error(f"Error subscribing to {url}: {e}")
            message = f"Error subscribing to {url}: {str(e)}"
        await ctx.send(message)

    await login_check_helper(ctx, func)


@bot.command(name="unsub", help=f"Unsubscribes by url. Usage: {COMMAND_PREFIX}unsub <url>")
async def unsub(ctx, url: str):
    async def func(db, current_user):
        try:
            feed = FeedRemove(url=url)
            unsubscribed_feed = crud.unsubscribe_from_feed(feed, current_user, db)
            if unsubscribed_feed:
                message = f"Unsubscribed to {unsubscribed_feed.url}"
            else:
                message = f"Error unsubscribing to {url} for empty"
        except Exception as e:
            logging.error(f"Error unsubscribing to {url}: {e}")
            message = f"Error unsubscribing to {url}: {str(e)}"
        await ctx.send(message)

    await login_check_helper(ctx, func)


@bot.command(name="list", help=f"list all subscriptions. Usage: {COMMAND_PREFIX}list")
async def list_subs(ctx):
    async def func(db, current_user):
        subscriptions = crud.list_subscribed_feeds(current_user, db)
        if subscriptions:
            message = "Your subscriptions:\n"
            for subscription in subscriptions:
                message += f"- {subscription.title} ({subscription.url})\n"
        else:
            message = "You have no subscriptions."
        await ctx.send(message)

    await login_check_helper(ctx, func)


@bot.command(name="news", help="get news by page number. Usage: /news or /news <page_number>")
async def get_news(ctx, page=1):
    # TODO: 对接AI？
    # TODO: discord显示卡片有点烦人？
    # TODO: check discord.ext.commands.errors.CommandInvokeError: Command raised an exception: HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
    #    In content: Must be 2000 or fewer in length.
    limit = 3
    skip = limit * (page - 1)

    async def func(db, current_user):
        try:
            articles: [models.Article] = crud.get_feed_articles(current_user, db, skip=skip, limit=limit)
            if articles:
                for article in articles:
                    await ctx.send(f"- {article.title} ({article.url})")
                await ctx.send(f"Page {page} finished")
            else:
                message = "No articles found."
                await ctx.send(message)
        except Exception as e:
            message = "Error fetching articles."
            logging.error(e)
            await ctx.send(message)

    await login_check_helper(ctx, func)


@bot.command(name="usage", help="Displays the usage information for all commands")
async def usage(ctx):
    usage_message = "**Bot Usage:**\n\n"
    for command in bot.commands:
        if command.help is not None:
            usage_message += f"`{bot.command_prefix}{command.name}` - {command.help}\n"
    await ctx.send(usage_message)


async def login_check_helper(ctx, func):
    db = next(get_db())
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)
    if current_user:
        message = await func(db, current_user)
    else:
        message = "Please signup with discord first. https://discord-rss-backend-production.up.railway.app/auth/discord"
    return message


@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} has connected to Discord!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
