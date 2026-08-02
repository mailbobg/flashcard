# -*- coding: utf-8 -*-
"""生成分享用图片：og 横图、微信方形缩略图、以及主屏图标。

用法：python3 src/make_share.py
产物：share.png (1200x630)、share-square.png (640x640)、apple-touch-icon.png (180x180)
依赖：Chrome（渲染 HTML）、Pillow（画图标）
"""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
sys.path.insert(0, HERE)
from build import logo_svg                     # noqa: E402  标志的唯一来源


def fonts_css():
    """从 tpl.html 里取出内嵌的 Figtree @font-face，分享图复用同一套字形"""
    tpl = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
    faces = re.findall(r'@font-face\{.*?\}', tpl, re.S)
    assert faces, 'tpl.html 里没找到 @font-face'
    return '\n'.join(faces)


def shoot(html_path, out, w, h):
    """Chrome 截图出 PNG，再转成 JPEG。分享图是渐变底，JPEG 体积只有 PNG 的三成，
    而抓取器（尤其微信）对慢响应会直接放弃，体积就是成败关键。"""
    from PIL import Image
    png = out + '.tmp.png'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', '--default-background-color=FFFFFFFF',
                    '--window-size=%d,%d' % (w, h), '--screenshot=' + png,
                    'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    Image.open(png).convert('RGB').save(out, 'JPEG', quality=86, optimize=True, progressive=True)
    os.unlink(png)
    print('  %s  %dx%d  %d KB' % (os.path.basename(out), w, h, os.path.getsize(out) / 1024))


ICON_HTML = ('<style>html,body{margin:0;width:{S}px;height:{S}px;background:{BG};overflow:hidden}'
             'body{display:flex;align-items:center;justify-content:center}'
             'svg{flex:0 0 auto;width:{L}px;height:{L}px;display:block}</style>{SVG}')


def icon(out, size, bg, fill=86):
    """从 src/logo.svg 渲染图标。bg 传 'transparent' 则出透明底。
    iOS 主屏图标不支持透明（会被合成到黑底），所以要给实底。
    尺寸用绝对像素——百分比在 flex 容器里对无固有尺寸的 SVG 解析不可靠。"""
    html = (ICON_HTML.replace('{S}', str(size)).replace('{BG}', bg)
            .replace('{L}', str(round(size * fill / 100))).replace('{SVG}', logo_svg()))
    fd, tmp = tempfile.mkstemp(suffix='.html')
    os.write(fd, html.encode('utf-8')); os.close(fd)
    try:
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=1',
                        '--default-background-color=' + ('00000000' if bg == 'transparent' else 'FFFFFFFF'),
                        '--window-size=%d,%d' % (size, size), '--screenshot=' + out,
                        'file://' + tmp], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.unlink(tmp)
    print('  %s  %dx%d  %d KB' % (os.path.basename(out), size, size, os.path.getsize(out) / 1024))


if __name__ == '__main__':
    html = (open(os.path.join(HERE, 'share.html'), encoding='utf-8').read()
            .replace('__FONTS__', fonts_css()).replace('__LOGO__', logo_svg()))
    fd, tmp = tempfile.mkstemp(suffix='.html')
    os.write(fd, html.encode('utf-8')); os.close(fd)
    try:
        shoot(tmp, os.path.join(ROOT, 'share.jpg'), 1200, 630)
        shoot(tmp, os.path.join(ROOT, 'share-square.jpg'), 640, 640)
    finally:
        os.unlink(tmp)
    icon(os.path.join(ROOT, 'apple-touch-icon.png'), 180, '#F8F4ED', fill=78)
    icon(os.path.join(ROOT, 'favicon.png'), 32, 'transparent', fill=100)
