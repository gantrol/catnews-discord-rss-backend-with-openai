import logging
import os
import discord
from discord import Message
from discord.ext import commands
from dotenv import load_dotenv

from app import crud, models, schemas
from app.database import get_db
from app.schemas import FeedCreate, FeedRemove
from app.utils.aiapi import generate_tags_and_summary
from app.utils.message import extract_url_from_message

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_API")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

COMMAND_PREFIX = "/"

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.command(name="sub", help=f"Subscribes by url. Usage: `{COMMAND_PREFIX}sub <url>`")
async def sub(ctx, url: str):
    # TODO: 更精细的异常处理
    """

    :param ctx:
    :param url: the url you want to subscribe
    :return:
    """

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


@bot.command(name="unsub", help=f"Unsubscribes by url. Usage: `{COMMAND_PREFIX}unsub <url>`")
async def unsub(ctx, url: str):
    """

    :param ctx:
    :param url: the url you want to subscribe
    :return:
    """

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


@bot.command(name="list", help=f"list all subscriptions. Usage: `{COMMAND_PREFIX}list`")
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


@bot.command(name="news", help="get news by page number. Usage: `/news` or `/news <page_number>`")
async def get_news(ctx, page=1):
    """

    :param ctx:
    :param page: the page numbers of news
    :return:
    """
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
                    await ctx.send(f"- {article.title}: {article.url}")
                await ctx.send(f"Page {page} finished")
            else:
                message = "No articles found."
                await ctx.send(message)
        except Exception as e:
            message = "Error fetching articles."
            logging.error(e)
            await ctx.send(message)

    await login_check_helper(ctx, func)


@bot.command(name="cat",
             help="get tags and summary of an article. Usage: `/cat` and reply to a message containing the article URL.")
async def get_tags_and_summary(ctx: commands.Context):
    ref_message = ctx.message.reference.resolved

    if not ref_message:
        await ctx.send("Please reply to a message containing the article URL.")
        return

    url = extract_url_from_message(ref_message)

    if not url:
        await ctx.send("No URL found in the referenced message.")
        return

    async def func(db, current_user):
        try:
            # TODO: check current_user private
            article: models.Article = crud.get_article_by_url(db, url=url)
            if article:
                tags, summary = generate_tags_and_summary(article.content)

                crud.associate_tags_with_article(db, article, tags)

                summary_obj = crud.get_summary_by_article_id(db, article_id=article.id)
                if not summary_obj:
                    summary_create = schemas.SummaryCreate(content=summary)
                    summary_obj = crud.create_summary(db, summary_create, article_id=article.id)

                await ctx.send(f"Title: {article.title}\n\nTags: {', '.join(tags)}\n\nSummary: {summary_obj.content}")
            else:
                message = "Article not found."
                await ctx.send(message)
        except Exception as e:
            message = "Error fetching tags and summary."
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
