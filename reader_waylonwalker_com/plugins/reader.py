"""Reader load plugin."""
import itertools
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

import feedparser
import frontmatter
import more_itertools
import pydantic
from bs4 import BeautifulSoup
from markata import background
from markata.hookspec import hook_impl, register_attr
from rich.progress import BarColumn, Progress
from yaml.parser import ParserError


class Feed(pydantic.BaseModel):
    url: str
    author: Optional[str]
    feed: Optional[Any] = None


class ReaderConfig(pydantic.BaseModel):
    feeds: Optional[List[Feed]]


class Config(pydantic.BaseModel):
    reader: Optional[List[Feed]]
    # reader: ReaderConfig = ReaderConfig()


@hook_impl
@register_attr("post_models")
def config_model(markata) -> None:
    markata.config_models.append(Config)


@hook_impl
@register_attr("articles", "posts")
def load(markata) -> None:
    Progress(
        BarColumn(bar_width=None),
        transient=True,
        console=markata.console,
    )
    for feed in markata.config.reader:
        feed.feed = feedparser.parse(feed.url)

    if "articles" not in markata.__dict__:
        markata.articles = []
    for feed in markata.config.reader:
        for post in feed.feed["entries"]:
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
                # output_html=output_html,
                title=post.get("title", "untitled")
                + " - "
                + post.get("author", feed.author),
                content=post.get("summary", ""),
                # file=file,
                slug=post.get("link"),
                image=image,
                # edit_link=edit_link,
            )
            markata.articles.append(article)
