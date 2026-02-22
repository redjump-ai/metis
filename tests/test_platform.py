"""Tests for platform detection module."""
import pytest
from metis.fetchers.platform import detect_platform, PLATFORMS


class TestDetectPlatform:
    """Tests for detect_platform function."""

    def test_detect_wechat(self):
        """Test WeChat detection."""
        result = detect_platform("https://mp.weixin.qq.com/s/xxxxx")
        assert result.name == "wechat"

    def test_detect_x_twitter(self):
        """Test X/Twitter detection."""
        assert detect_platform("https://x.com/user/status/123").name == "twitter"
        assert detect_platform("https://twitter.com/user/status/123").name == "twitter"

    def test_detect_zhihu(self):
        """Test Zhihu detection."""
        result = detect_platform("https://www.zhihu.com/question/123456")
        assert result.name == "zhihu"

    def test_detect_xiaohongshu(self):
        """Test Xiaohongshu detection."""
        result = detect_platform("https://www.xiaohongshu.com/discovery/item/123")
        assert result.name == "xiaohongshu"

    def test_detect_douyin(self):
        """Test Douyin detection."""
        result = detect_platform("https://www.douyin.com/video/123")
        assert result.name == "douyin"

    def test_detect_bilibili(self):
        """Test Bilibili detection."""
        result = detect_platform("https://www.bilibili.com/video/BV123456")
        assert result.name == "bilibili"

    def test_detect_unknown(self):
        """Test unknown platform."""
        result = detect_platform("https://example.com/article")
        assert result.name == "unknown"


class TestPlatformInfo:
    """Tests for PlatformInfo."""

    def test_wechat_info(self):
        """Test WeChat platform info."""
        info = PLATFORMS["wechat"]
        assert info.name == "wechat"
        assert info.referer == "https://mp.weixin.qq.com/"

    def test_twitter_info(self):
        """Test Twitter platform info."""
        info = PLATFORMS["twitter"]
        assert info.name == "twitter"
        assert info.referer == "https://twitter.com/"
