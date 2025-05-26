"""Reader load plugin."""

import datetime
from typing import Any, List, Optional

from bs4 import BeautifulSoup
import dateutil.parser
import feedparser
import pydantic

from markata.hookspec import hook_impl, register_attr
from markata import background
from markata.plugins.feeds import FeedConfig


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
    # markata.console.log(f"Loading feed: {feed.url}")
    start_time = datetime.datetime.now()
    feed.feed = feedparser.parse(feed.url)
    end_time = datetime.datetime.now()
    markata.console.log(f"Loaded feed: {feed.url} in {end_time - start_time}")


@hook_impl
@register_attr("articles", "posts")
def load(markata) -> None:
    futures = [get_feed(markata, feed) for feed in markata.config.reader]
    for future in futures:
        future.result()

    markata.console.log("Loaded articles")

    markata.config.feeds.append(
        FeedConfig(
            title="Blogroll",
            slug="blogroll",
            description="Blogroll - a collection of awesome people I follow online",
            name="blogroll",
            filter="'blogroll' in tags",
        )
    )

    if "articles" not in markata.__dict__:
        markata.articles = []
    for feed in markata.config.reader:
        markata.console.log(f"Creating posts for: {feed.url}")
        markata.console.log(f"feed has {len(feed.feed['entries'])} entries")
        markata.config.feeds.append(
            FeedConfig(
                title=f"{feed.author}'s posts",
                slug=f"{feed.author.replace(' ', '-').lower()}-posts",
                description=f"{feed.author}'s posts from {feed.url}",
                name=f"{feed.author.replace(' ', '_').lower()}_posts",
                filter=f"'{feed.author.replace(' ', '_').lower()}' in tags",
                sort="date",
                reverse=True,
            )
        )

        from urllib.parse import urlparse

        base_url = urlparse(feed.url).scheme + "://" + urlparse(feed.url).netloc
        image = f"https://shots.wayl.one/shot/?url={base_url}&height=600&width=1200&scaled_width=600&scaled_height=300"

        article = markata.Post(
            markata=markata,
            path="None",
            date=datetime.datetime.now(),
            datetime=datetime.datetime.now(),
            title=feed.author,
            content=f"{feed.author}'s posts from {feed.url}",
            slug=feed.author.replace(" ", "-").lower(),
            link=f"/{feed.author.replace(' ', '-').lower()}-posts",
            image=image,
            tags=["blogroll"],
            skip=False,
        )

        markata.articles.append(article)

        for i, post in enumerate(feed.feed["entries"]):
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

            if i <= feed.limit:
                tags = "main"
            else:
                tags = "hidden"

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
                tags=[*feed.tags, feed.author.replace(" ", "_").lower(), tags],
                skip=False,
            )
            markata.articles.append(article)
        print(f"Created {len(feed.feed['entries'])} posts for {feed.url}")
    print(f"Created {len(markata.articles)} posts")
    markata.posts = markata.articles
