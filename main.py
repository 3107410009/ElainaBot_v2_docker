#!/usr/bin/env python
"""ElainaBot 入口"""

import asyncio
import contextlib
import json
import os
import pathlib
import shutil
import ssl
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.dont_write_bytecode = True

# 全局跳过 SSL 证书验证
_orig_ctx = ssl.create_default_context


def _no_verify(*a, **kw):
    c = _orig_ctx(*a, **kw)
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    return c


ssl.create_default_context = _no_verify

# 加载 .env
_env = os.path.join(_ROOT, '.env')
if os.path.isfile(_env):
    with contextlib.suppress(ImportError):
        from dotenv import load_dotenv

        load_dotenv(_env, override=False)


def main():
    # 清理废弃文件/目录
    with contextlib.suppress(Exception):
        for r in json.loads(pathlib.Path(_ROOT, 'web', 'deprecated_files.json').read_text('utf-8')):
            t = pathlib.Path(_ROOT, r)
            if r.endswith('/'):
                shutil.rmtree(t, ignore_errors=True)
            else:
                t.unlink(missing_ok=True)
                shutil.rmtree(t.parent / '__pycache__', ignore_errors=True)

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    from core.application import Application
    with contextlib.suppress(KeyboardInterrupt):
        restart = asyncio.run(Application().start())
    if restart:
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == '__main__':
    main()
