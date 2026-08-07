# -*- coding: utf-8 -*-
"""把 src/parsed.json + src/phon.py 合成 src/data.json，再注入 src/tpl.html 生成 index.html。

用法：python3 src/build.py
产物：项目根目录的 index.html（单文件，含内嵌字体与全部词条，可离线打开）
"""
import json, os, re, sys

# 站点根地址。og:image / og:url 必须是绝对地址，换域名只改这一行（末尾保留斜杠）
BASE = 'https://flash.imyway.cn/'

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from phon import PHON                       # noqa: E402
from phon_phy import PHON_PHY               # noqa: E402
from trans import TRANS                     # noqa: E402
from extra import EXTRA                     # noqa: E402
from lessons import LESSONS                 # noqa: E402
from frames_phy import FRAMES_PHY           # noqa: E402
try:
    from trans_phy import TRANS_PHY          # noqa: E402  Task 10 才填
except ImportError:
    TRANS_PHY = {}

_dup = set(PHON) & set(PHON_PHY)
if _dup:
    raise SystemExit('phon_phy.py 重复定义了 phon.py 已有的词: %s' % sorted(_dup))
PHON = {**PHON, **PHON_PHY}                 # 物理独有词补进来，同名词沿用 phon.py 的
STRICT_PHON = True                           # phon_phy.py 已填满，缺词一律视为错误


def logo_svg():
    """src/logo.svg 是标志的唯一来源，页头 mark、favicon、分享图都从这里取"""
    return open(os.path.join(HERE, 'logo.svg'), encoding='utf-8').read().strip()


def logo_data_uri():
    """内联成 data URI 作 favicon —— 单文件离线打开时也有图标"""
    from urllib.parse import quote
    return 'data:image/svg+xml,' + quote(logo_svg(), safe="/:=<>' ")


def enrich(it, book):
    """给一个词条补上 id、音标、音节切分与助记。PHON 是唯一来源。

    PHON 尚未覆盖的词先给占位音节，让构建能跑通；check_phon 会报缺口，
    STRICT_PHON 打开后则直接失败。
    """
    if it['w'] in PHON:
        syl, tip = PHON[it['w']]
    else:
        syl, tip = ' / '.join('%s=?' % p for p in it['w'].split()), ''
    # "ob=ˌɒb|ser=zə" → [[{t:'ob',p:'ˌɒb'},…]]，词与词之间用 " / " 分隔
    sw = [[{'t': x.split('=')[0], 'p': x.split('=')[1]} for x in p.split('|')]
          for p in syl.split(' / ')]
    ipa = '/' + ' '.join(''.join(y['p'] for y in p) for p in sw) + '/'
    return {**it, 'id': '%s:%s' % (book, it['w']), 'ipa': ipa, 'syl': sw, 'tip': tip}


SCI = {'id': 'sci', 'cn': '科学', 'credit': 'IGCSE 自然科学英语核心词汇表'}
PHY = {'id': 'phy', 'cn': '物理', 'credit': 'Cambridge IGCSE Physics 0625 核心词汇表'}


def build_sci():
    """现有词表：优先吃 parsed.json，没有就用 data.json 缓存里的 sci 书"""
    src = os.path.join(HERE, 'parsed.json')
    if not os.path.exists(src):
        cached = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
        bk = next(b for b in cached['books'] if b['id'] == 'sci')
        have = {w['w'] for s in bk['sections'] for w in s['words']}
        missing = [enrich(it, 'sci') for it in EXTRA['words'] if it['w'] not in have]
        if missing:
            bk['sections'].append({'id': len(bk['sections']) + 1,
                                   'cn': EXTRA['cn'], 'en': EXTRA['en'], 'words': missing})
        return bk

    d = json.load(open(src, encoding='utf-8'))
    secs, sid = [], 0
    for s in d['sections']:
        if not s['items']:
            continue
        body = re.match(r'^[一二三四五六七八九]、(.+)$', s['title']).group(1)
        m = re.search(r'(?<=[一-鿿])(?=[A-Za-z])', body)     # 中英文标题分界
        cn, en = (body[:m.start()].strip(), body[m.start():].strip()) if m else (body, '')
        sid += 1
        secs.append({'id': sid, 'cn': cn, 'en': en,
                     'words': [enrich(it, 'sci') for it in s['items']]})
    sid += 1                                   # 衔接课程带来的补充词汇单列一章
    secs.append({'id': sid, 'cn': EXTRA['cn'], 'en': EXTRA['en'],
                 'words': [enrich(it, 'sci') for it in EXTRA['words']]})
    return {**SCI, 'sections': secs, 'frames': d['frames']}


def build_phy():
    """物理词表：parsed_phy.json 是唯一来源，它已入库，不依赖 PDF"""
    d = json.load(open(os.path.join(HERE, 'parsed_phy.json'), encoding='utf-8'))
    secs = [{'id': i + 1, 'cn': s['cn'], 'en': s['en'],
             'words': [enrich(it, 'phy') for it in s['items']]}
            for i, s in enumerate(d['sections'])]
    return {**PHY, 'sections': secs, 'frames': FRAMES_PHY}


def build_data():
    # {**SCI, **book} 让缓存分支也一定带上最新的 cn / credit
    data = {'books': [{**SCI, **build_sci()}, build_phy()]}
    json.dump(data, open(os.path.join(HERE, 'data.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    return data


def attach_lessons(data):
    """课时里引用的词必须在词库中查得到，否则「开始学这些词」会点空。

    vocab 的词可写成 "sci:diffusion" 跨书引用；不带前缀就按课时自己的 book 解析。
    """
    have = {w['id'] for bk in data['books'] for s in bk['sections'] for w in s['words']}
    ids = {b['id'] for b in data['books']}
    for les in LESSONS:
        if les.get('book') not in ids:
            raise SystemExit('第 %s 节的 book 字段应为 %s，实为 %r'
                             % (les['id'], sorted(ids), les.get('book')))
        miss = []
        for v in les['vocab']:
            wid = v[0] if ':' in v[0] else '%s:%s' % (les['book'], v[0])
            if wid not in have:
                miss.append(wid)
        if miss:
            raise SystemExit('第 %s 节引用了词库中不存在的词: %s' % (les['id'], miss))
    data['lessons'] = LESSONS
    return len(LESSONS)


def attach_trans(book, TR):
    """把例句的翻译思路挂到指定的书上。独立于 build_data——直接吃缓存时也要生效。"""
    n, seen = 0, set()
    for s in book['sections']:
        for w in s['words']:
            if w['w'] in TR:
                w['tr'] = TR[w['w']]; n += 1; seen.add(w['w'])
            else:
                w.pop('tr', None)                  # 标注被删掉时同步清掉
    unknown = set(TR) - seen
    if unknown:
        raise SystemExit('%s 的 trans 里有词表中不存在的词条: %s'
                         % (book['id'], sorted(unknown)))
    missing = [w['w'] for s in book['sections'] for w in s['words'] if 'tr' not in w]
    if missing:
        print('  ⚠ %s 尚缺翻译思路 %d 条: %s%s'
              % (book['id'], len(missing), ', '.join(missing[:6]),
                 ' …' if len(missing) > 6 else ''))
    for w, t in TR.items():                        # 结构自检
        for k in ('pat', 'flow', 'core', 'final', 'tip'):
            if k not in t:
                raise SystemExit('%s 缺字段 %s' % (w, k))
        if any(len(x) != 3 for x in t['flow']):
            raise SystemExit('%s 的 flow 每项要写成 [英文, 中文, 成分]' % w)
    # final 各段拼起来必须与原书译文完全一致，防止标注时漏字或改写
    for s in book['sections']:
        for w in s['words']:
            if 'tr' not in w:
                continue
            joined = ''.join(seg[0] for seg in w['tr']['final'])
            if re.sub(r'\s+', '', joined) != re.sub(r'\s+', '', w['exzh']):
                raise SystemExit('%s 的 final 拼接与译文不符:\n  %s\n  %s'
                                 % (w['id'], joined, w['exzh']))
    return n


def check(data):
    """音节拼写拼回原词必须一致，否则说明 PHON 写错了"""
    # distance–time graph 用的是 en dash（U+2013），不是 ASCII 连字符，一并剥掉
    def norm(x):
        for c in ('-', '–', '—', ' '):
            x = x.replace(c, '')
        return x.lower()

    bad = []
    for bk in data['books']:
        for s in bk['sections']:
            for w in s['words']:
                rebuilt = ' '.join(''.join(y['t'] for y in p) for p in w['syl'])
                if norm(rebuilt) != norm(w['w']):
                    bad.append((w['id'], rebuilt))
    if bad:
        raise SystemExit('音节拼写与原词不符: %s' % bad)
    return sum(len(s['words']) for bk in data['books'] for s in bk['sections'])


def check_ids(data):
    """同一本书内 id 不能重复。这道会自动兜住 PDF 里同词出现两次那类问题。"""
    for bk in data['books']:
        seen = set()
        for s in bk['sections']:
            for w in s['words']:
                if w['id'] in seen:
                    raise SystemExit('%s 书内 id 重复: %s' % (bk['id'], w['id']))
                seen.add(w['id'])


def check_phon(data):
    """PHON 必须覆盖两本书的全部裸词。STRICT_PHON 之前只报缺口数。"""
    miss = sorted({w['w'] for bk in data['books']
                   for s in bk['sections'] for w in s['words']
                   if w['w'] not in PHON})
    if miss and STRICT_PHON:
        raise SystemExit('PHON 缺 %d 词: %s' % (len(miss), miss))
    if miss:
        print('  ⚠ 尚缺音标/助记 %d 词（占位中）: %s%s'
              % (len(miss), ', '.join(miss[:6]), ' …' if len(miss) > 6 else ''))
    return len(miss)


if __name__ == '__main__':
    data = build_data()
    n = check(data)
    check_ids(data)
    nmiss = check_phon(data)
    books = {b['id']: b for b in data['books']}
    ntr = attach_trans(books['sci'], TRANS)
    ntr += attach_trans(books['phy'], TRANS_PHY)
    nles = attach_lessons(data)
    tpl = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read()
    assert '__DATA__' in tpl, 'tpl.html 缺少 __DATA__ 占位符'
    assert '__BASE__' in tpl, 'tpl.html 缺少 __BASE__ 占位符'
    assert BASE.endswith('/'), 'BASE 末尾要有斜杠'
    html = (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
               .replace('__LOGO_URI__', logo_data_uri())      # 顺序要紧：先换 URI，再换裸 SVG
               .replace('__LOGO__', logo_svg())
               .replace('__BASE__', BASE)
               .replace('__N__', str(n)))
    dst = os.path.join(ROOT, 'index.html')
    open(dst, 'w', encoding='utf-8').write(html)
    print('built %s — %d 词（%d 句带翻译思路，%d 词缺音标）, %d 节预习, %d KB'
          % (dst, n, ntr, nmiss, nles, round(os.path.getsize(dst) / 1024)))
