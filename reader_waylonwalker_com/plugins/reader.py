"""Reader load plugin."""

from typing import Any, List, Optional

import feedparser
import pydantic
from bs4 import BeautifulSoup

from markata.hookspec import hook_impl, register_attr


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


@hook_impl
@register_attr("articles", "posts")
def load(markata) -> None:
    for feed in markata.config.reader:
        feed.feed = feedparser.parse(feed.url)

    if "articles" not in markata.__dict__:
        markata.articles = []
    for feed in markata.config.reader:
        for post in feed.feed["entries"][0 : feed.limit]:
            if post.get("title") == "":
                post["title"] = post.get("link")
            if "<" in post.get("summary"):
                post["summary"] = BeautifulSoup(
                    post.get("summary"), "html.parser"
                ).get_text()

            image = post.get("media_thumbnail", [{}])[0].get(
                "url",
            )
            if image is None:
                image = f"https://shots.wayl.one/shot/?url={post.get('link')}&height=450&width=800&scaled_width=800&scaled_height=450&selectors="

            article = markata.Post(
                markata=markata,
                path="None",
                date=post.get("published"),
                title=post.get("title", "untitled")
                + " - "
                + post.get("author", feed.author),
                content=post.get("summary", ""),
                article_html=post.get("summary", ""),
                slug=post.get("link"),
                link=post.get("link"),
                image=image,
                tags=feed.tags,
            )
            markata.articles.append(article)
    markata.posts = markata.articles
