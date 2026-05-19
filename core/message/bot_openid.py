"""Bot OpenID 缓存 — 记录各 appid 的机器人 member_openid, 持久化到 JSON"""

import json
import os

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_FILE = os.path.join(_BASE, 'data', 'bot_openids.json')

# {appid: openid} 每个机器人仅一个 openid
_cache: dict[str, str] = {}
# {appid: '<@openid>'} 预格式化标签, 热路径零分配
_tag: dict[str, str] = {}

# 启动时加载
if os.path.isfile(_FILE):
    try:
        with open(_FILE, encoding='utf-8') as _f:
            for _k, _v in json.load(_f).items():
                if isinstance(_v, str) and _v:
                    _cache[_k] = _v
                    _tag[_k] = f'<@{_v}>'
    except Exception:
        pass


def add(appid, openid):
    """记录 bot openid (仅首次发现时写盘)"""
    if _cache.get(appid) == openid:
        return
    _cache[appid] = openid
    _tag[appid] = f'<@{openid}>'
    try:
        os.makedirs(os.path.dirname(_FILE), exist_ok=True)
        with open(_FILE, 'w', encoding='utf-8') as f:
            json.dump(_cache, f, ensure_ascii=False)
    except Exception:
        pass


def strip_self_at(appid, content):
    """移除 content 中本机器人的所有 <@openid> (可能被艾特多次)"""
    t = _tag.get(appid)
    if not t:
        return content
    return content.replace(t, '').strip()
