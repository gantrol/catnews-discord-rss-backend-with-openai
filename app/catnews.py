import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from app import crud, models, schemas
from app.database import get_db
from app.schemas import FeedCreate, FeedRemove
from app.utils.aiapi import generate_tags, generate_summary
from app.utils.message import extract_url_from_message

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_API")


COMMAND_PREFIX = "/"

COMMAND_PREFIX2 = "!"
bot = commands.Bot(command_prefix="!")


@bot.slash_command(name="sub", description=f"Subscribes by url. Usage: `{COMMAND_PREFIX}sub <url>`")
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
        await ctx.respond(message)

    await login_check_helper(ctx, func)


@bot.slash_command(name="unsub", description=f"Unsubscribes by url. Usage: `{COMMAND_PREFIX}unsub <url>`")
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
        await ctx.respond(message)

    await login_check_helper(ctx, func)


@bot.slash_command(name="list", description=f"list all subscriptions. Usage: `{COMMAND_PREFIX}list`")
async def list_subs(ctx):
    async def func(db, current_user):
        subscriptions = crud.list_subscribed_feeds(current_user, db)
        if subscriptions:
            message = "Your subscriptions:\n"
            for subscription in subscriptions:
                message += f"- {subscription.title} ({subscription.url})\n"
        else:
            message = "You have no subscriptions."
        await ctx.respond(message)

    await login_check_helper(ctx, func)


@bot.slash_command(name="news", description="get news by page number. Usage: `/news` or `/news <page_number>`")
async def get_news(ctx, page: int = 1):
    """

    :param ctx:
    :param page: the page numbers of news
    :return:
    """
    # TODO: 对接AI？
    # TODO: discord显示卡片有点烦人？
    # TODO: check discord.ext.commands.errors.CommandInvokeError: Command raised an exception: HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
    #    In content: Must be 2000 or fewer in length.
    try:
        page = int(page)
    except Exception:
        page = 1
    limit = 3
    skip = limit * (page - 1)

    async def func(db, current_user):
        try:
            articles: [models.Article] = crud.get_feed_articles(current_user, db, skip=skip, limit=limit)
            if articles:
                for article in articles:
                    await ctx.send(f"- {article.title}: {article.url}")
                await ctx.respond(f"Page {page} finished")
            else:
                message = "No articles found."
                await ctx.respond(message)
        except Exception as e:
            message = "Error fetching articles."
            logging.error(e)
            await ctx.respond(message)

    await login_check_helper(ctx, func)


@bot.slash_command(name="cat",
             description=f"get tags and summary of an article. Usage: `{COMMAND_PREFIX2}cat` and reply to a message containing the article URL.")
async def get_tags_and_summary(ctx, url):
    ref_message = url

    # TODO: extract check url logic for sub and unsub
    url = extract_url_from_message(ref_message)

    if not url:
        await ctx.respond("No URL found in the referenced message.")
        return

    async def func(db, current_user):
        try:
            # TODO: check current_user private
            article: models.Article = crud.get_article_by_url(db, url=url)
            if article:
                tags = crud.get_tags_by_article_id(db, article_id=article.id)
                summary_obj = crud.get_summary_by_article_id(db, article_id=article.id)
                if not tags:
                    tags = generate_tags(article.content)
                    crud.associate_tags_with_article(db, article, tags)
                if not summary_obj:
                    summary = generate_summary(article.content)
                    summary_create = schemas.SummaryCreate(content=summary)
                    summary_obj = crud.create_summary(db, summary_create, article_id=article.id)
                await ctx.respond(f"Title: {article.title}\n\nTags: {', '.join(tags)}\n\nSummary: {summary_obj.content}")
            else:
                message = "Article should be fetch by `news` command first."
                await ctx.respond(message)
        except Exception as e:
            message = "Error fetching tags and summary."
            logging.error(e)
            await ctx.respond(message)

    await login_check_helper(ctx, func)


async def login_check_helper(ctx, func) -> None:
    db = next(get_db())
    user_id = str(ctx.author.id)
    current_user = crud.get_user_by_discord_id(user_id, db)
    if current_user:
        await func(db, current_user)
    else:
        message = "Please signup with discord first. https://discord-rss-backend-production.up.railway.app/auth/discord"
        await ctx.respond(message)
    # return message


@bot.event
async def on_ready():
    logging.info(f"{bot.user.name} has connected to Discord!")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
