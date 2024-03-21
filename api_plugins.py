import logging
import plugins
from plugins import *
from bridge.bridge import Bridge
from bridge.context import ContextType
from .utils import Utils
from bridge.reply import ReplyType
from plugins.event import EventContext, EventAction
import urllib.parse


@plugins.register(
    name="apitools",
    desire_priority=200,
    hidden=True,
    desc="基于网络接口的插件",
    version="0.2",
    author="qiupo",
)
class ApiTools(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.apiKey = "b932144bab6bb6827457707e59455136"
        self.rbKey = "fc4579fece2c9773255a5dbc13c6b229"
        self.utils = Utils(self.apiKey, self.rbKey)
        logging.info("[apitools] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return
        query: str = e_context["context"].content
        logging.info("content => " + query)
        content = ""
        song_url = ""
        song_name = ""
        if query.startswith(f"点歌") or query.startswith(f"找歌"):
            msg = query.replace("点歌", "")
            msg = query.replace("找歌", "")
            msg = msg.strip()
            url, name, ar = self.utils.search_song(msg)
            song_name = "{} - {}".format(name, ar)
            if self.utils.is_valid_url(url):
                content = "为你找到：{} - {}".format(name, ar)
                song_url = url
            else:
                content = "找不到歌曲😮‍💨"
                logging.info("点歌 reply --> {}, url:{}".format(msg, url))
        elif query.startswith(f"推荐"):
            chat = Bridge().get_bot("chat")

            reply = chat.reply(query + " 以歌名 - 歌手的格式回复", e_context["context"])
            logging.info("music receive => query:{}, reply:{}".format(query, reply))

            url, name, ar = self.utils.search_song(reply.content)
            song_name = "{} - {}".format(name, ar)
            if self.utils.is_valid_url(url):
                content = "为你找到：{} - {} ".format(name, ar)
                song_url = url
            else:
                content = reply.content + "\n----------\n找不到相关歌曲😮‍💨"
                logging.info("点歌 reply --> {}, url:{}".format(reply.content, url))
        elif (
            self.utils.has_str(query, "知乎热榜")
            or self.utils.has_str(query, "微博热搜")
            or self.utils.has_str(query, "百度热点")
            or self.utils.has_str(query, "历史上的今天")
            or self.utils.has_str(query, "bili热搜")
            or self.utils.has_str(query, "bili全站日榜")
            or self.utils.has_str(query, "少数派头条")
        ):
            logging.info("search rb --> {}".format(self.utils.rb_types["知乎热榜"]))
            if self.utils.has_str(query, "知乎热榜"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["知乎热榜"]
                )
            elif self.utils.has_str(query, "微博热搜"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["微博热搜"]
                )
            elif self.utils.has_str(query, "百度热点"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["百度热点"]
                )
            elif self.utils.has_str(query, "历史上的今天"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["历史上的今天"]
                )
            elif self.utils.has_str(query, "哔哩哔哩热搜"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["哔哩哔哩热搜"]
                )
            elif self.utils.has_str(query, "哔哩哔哩全站日榜"):
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["哔哩哔哩全站日榜"]
                )
            else:
                title, subtitle, update_time, data = self.utils.search_rb(
                    self.utils.rb_types["少数派头条"]
                )
            logging.info(
                "search rb --> {}{}{}{}".format(data.__len__, title, subtitle, update_time)
            )
            if data.__len__ == 0:
                content = "暂无相关数据"
            else:
                content = "{}{}{}\n{}".format(
                    title,
                    subtitle,
                    update_time,
                    "\n".join(
                        [
                            "{}. {}\n{}\n".format(
                                index + 1,
                                item["title"],
                                (
                                    urllib.parse.quote(
                                        item["mobilUrl"],
                                        safe=";/?:@&=+$,",
                                        encoding="utf-8",
                                    )
                                    if item["mobilUrl"] is not None
                                    else urllib.parse.quote(
                                        item["url"],
                                        safe=";/?:@&=+$,",
                                        encoding="utf-8",
                                    )
                                ),
                            )
                            for index, item in enumerate(data)
                        ]
                    ),
                )
        else:
            return
        logging.info("song_url:{}".format(song_url))
        self.utils._send_info(e_context, content, ReplyType.TEXT)

        if self.utils.is_valid_url(song_url):
            self.utils.save_mp3_tempfile(song_url, e_context, song_name)
        e_context.action = EventAction.BREAK_PASS
        return

    def get_help_text(self, verbose=False, **kwargs):
        help_text = "推荐音乐\n"
        help_text += " 推荐一首粤语经典歌曲"
        help_text += "点歌/找歌\n"
        help_text += " 找歌 可惜我是水瓶座 杨千嬅"
        help_text += "搜索热榜\n"
        help_text += "知乎热榜\n"
        help_text += "微博热搜\n"
        help_text += "百度热点\n"
        help_text += "历史上的今天\n"
        help_text += "bili热搜\n"
        help_text += "bili全站日榜\n"
        help_text += "少数派头条\n"
        return help_text
