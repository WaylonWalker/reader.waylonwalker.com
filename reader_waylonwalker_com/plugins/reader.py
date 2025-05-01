"""Reader load plugin."""

import datetime
from typing import Any, List, Optional

from bs4 import BeautifulSoup
import dateutil.parser
import feedparser
import pydantic

from markata.hookspec import hook_impl, register_attr
from markata import background


class Feed(pydantic.BaseModel):
    url: str
    author: Optional[str]
    feed: Optional[Any] = None
    tags: Optional[List[str]]
    limit: Optional[int] = 20


class ReaderConfig(pydantic.BaseModel):
    feeds: Optional[List[Feed]]


class Config(pydantic.BaseModel):
    reader: Optional[List[Feed]]


@hook_impl
@register_attr("post_models")
def config_model(markata) -> None:
    markata.config_models.append(Config)


def parse_date(date_str: str) -> datetime.datetime:
    """Parse a date string into a datetime object."""
    if not date_str:
        return None
    try:
        dt = dateutil.parser.parse(date_str)
        return dt
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Failed to parse {date_str}: {e}")
        return None


@background.task
def get_feed(markata, feed):
    markata.console.log(f"Loading feed: {feed.url}")
    feed.feed = feedparser.parse(feed.url)


@hook_impl
@register_attr("articles", "posts")
def load(markata) -> None:
    # for feed in markata.config.reader:
    #     markata.console.log(f"Loading feed: {feed.url}")
    # feed.feed = feedparser.parse(feed.url)
    futures = [get_feed(markata, feed) for feed in markata.config.reader]
    for future in futures:
        future.result()

    markata.console.log(f"Loaded {len(markata.articles)} articles")

    if "articles" not in markata.__dict__:
        markata.articles = []
    for feed in markata.config.reader:
        markata.console.log(f"Creating posts for: {feed.url}")
        markata.console.log(f"feed has {len(feed.feed['entries'])} entries")

        for post in feed.feed["entries"][0 : feed.limit]:
            if post.get("title") == "":
                post["title"] = post.get("link")
            if "<" in post.get("summary", ""):
                post["summary"] = BeautifulSoup(
                    post.get("summary"), "html.parser"
                ).get_text()

            image = post.get("media_thumbnail", [{}])[0].get(
                "url",
            )
            if image is None:
                image = f"https://shots.wayl.one/shot/?url={post.get('link')}&height=450&width=800&scaled_width=800&scaled_height=450&selectors="

            # Get the published date, trying multiple fields
            date_time = None
            for date_field in ["published", "updated", "created"]:
                date_str = post.get(date_field)
                if date_str:
                    date_time = parse_date(date_str)
                    if date_time:
                        break

            if date_time:
                raw_date = date_time.isoformat()
            else:
                raw_date = None
                markata.console.log("No date found in feed entry")

            article = markata.Post(
                markata=markata,
                path="None",
                date=raw_date,
                datetime=raw_date,
                title=post.get("title", "untitled")
                + " - "
                + post.get("author", feed.author),
                content=post.get("summary", ""),
                article_html=post.get("summary", ""),
                slug=post.get("link"),
                link=post.get("link"),
                image=image,
                tags=feed.tags,
                skip=False,
            )
            markata.articles.append(article)
        print(f"Created {len(feed.feed['entries'])} posts for {feed.url}")
    print(f"Created {len(markata.articles)} posts")
    markata.posts = markata.articles
