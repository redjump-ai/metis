"""Platform detection module."""
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class PlatformInfo:
    name: str
    requires_login: bool
    referer: Optional[str] = None


PLATFORMS = {
    "wechat": PlatformInfo(
        name="wechat",
        requires_login=False,
        referer="https://mp.weixin.qq.com/",
    ),
    "xiaohongshu": PlatformInfo(
        name="xiaohongshu",
        requires_login=False,
        referer="https://www.xiaohongshu.com/",
    ),
    "zhihu": PlatformInfo(
        name="zhihu",
        requires_login=False,
        referer="https://www.zhihu.com/",
    ),
    "douyin": PlatformInfo(
        name="douyin",
        requires_login=False,
        referer="https://www.douyin.com/",
    ),
    "bilibili": PlatformInfo(
        name="bilibili",
        requires_login=False,
        referer="https://www.bilibili.com/",
    ),
    "taobao": PlatformInfo(
        name="taobao",
        requires_login=True,
        referer="https://www.taobao.com/",
    ),
    "jd": PlatformInfo(
        name="jd",
        requires_login=True,
        referer="https://www.jd.com/",
    ),
    "weibo": PlatformInfo(
        name="weibo",
        requires_login=False,
        referer="https://weibo.com/",
    ),
    "toutiao": PlatformInfo(
        name="toutiao",
        requires_login=False,
        referer="https://www.toutiao.com/",
    ),
    # X (formerly Twitter)
    "twitter": PlatformInfo(
        name="twitter",
        requires_login=False,
        referer="https://twitter.com/",
    ),
}


def detect_platform(url: str) -> PlatformInfo:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if "mp.weixin.qq.com" in host or "weixin.qq.com" in host:
        return PLATFORMS["wechat"]
    if "xiaohongshu.com" in host or "xhslink.com" in host:
        return PLATFORMS["xiaohongshu"]
    if "zhihu.com" in host:
        return PLATFORMS["zhihu"]
    if "douyin.com" in host:
        return PLATFORMS["douyin"]
    if "bilibili.com" in host:
        return PLATFORMS["bilibili"]
    if "taobao.com" in host:
        return PLATFORMS["taobao"]
    if "jd.com" in host or "jd.hk" in host:
        return PLATFORMS["jd"]
    if "weibo.com" in host or "weibo.cn" in host:
        return PLATFORMS["weibo"]
    if "toutiao.com" in host:
        return PLATFORMS["toutiao"]
    if "twitter.com" in host or "x.com" in host:
        # Both x.com and twitter.com are now mapped to "twitter" platform
        return PLATFORMS["twitter"]

    return PlatformInfo(name="unknown", requires_login=False)
