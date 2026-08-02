# -*- coding: utf-8 -*-
"""生成分享用图片：og 横图、微信方形缩略图、以及主屏图标。

用法：python3 src/make_share.py
产物：share.png (1200x630)、share-square.png (640x640)、apple-touch-icon.png (180x180)
依赖：Chrome（渲染 HTML）、Pillow（画图标）
"""
import os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
INK = (21, 17, 12)


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


def icon(out, size=180):
    """主屏图标：墨色圆角方块 + 四个白点，与应用内的 mark 一致"""
    from PIL import Image, ImageDraw
    ss, s = 4, size * 4                       # 4 倍超采样再缩小，边缘更干净
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .225), fill=INK + (255,))
    pad, gap = int(s * .27), int(s * .055)
    cell = (s - pad * 2 - gap) // 2
    for row in range(2):
        for col in range(2):
            x = pad + col * (cell + gap)
            y = pad + row * (cell + gap)
            d.rounded_rectangle([x, y, x + cell, y + cell], radius=int(cell * .22), fill=(255, 255, 255, 255))
    im.resize((size, size), Image.LANCZOS).save(out)
    print('  %s  %dx%d  %d KB' % (os.path.basename(out), size, size, os.path.getsize(out) / 1024))


if __name__ == '__main__':
    html = open(os.path.join(HERE, 'share.html'), encoding='utf-8').read().replace('__FONTS__', fonts_css())
    fd, tmp = tempfile.mkstemp(suffix='.html')
    os.write(fd, html.encode('utf-8')); os.close(fd)
    try:
        shoot(tmp, os.path.join(ROOT, 'share.jpg'), 1200, 630)
        shoot(tmp, os.path.join(ROOT, 'share-square.jpg'), 640, 640)
    finally:
        os.unlink(tmp)
    icon(os.path.join(ROOT, 'apple-touch-icon.png'), 180)
    icon(os.path.join(ROOT, 'favicon.png'), 32)      # 不支持 SVG favicon 的内置浏览器用它
