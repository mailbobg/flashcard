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
from trans import TRANS                     # noqa: E402
from extra import EXTRA                     # noqa: E402
from lessons import LESSONS                 # noqa: E402


def logo_svg():
    """src/logo.svg 是标志的唯一来源，页头 mark、favicon、分享图都从这里取"""
    return open(os.path.join(HERE, 'logo.svg'), encoding='utf-8').read().strip()


def logo_data_uri():
    """内联成 data URI 作 favicon —— 单文件离线打开时也有图标"""
    from urllib.parse import quote
    return 'data:image/svg+xml,' + quote(logo_svg(), safe="/:=<>' ")


def enrich(it):
    """给一个词条补上音标、音节切分与助记。PHON 是唯一来源。"""
    syl, tip = PHON[it['w']]
    # "ob=ˌɒb|ser=zə" → [[{t:'ob',p:'ˌɒb'},…]]，词与词之间用 " / " 分隔
    sw = [[{'t': x.split('=')[0], 'p': x.split('=')[1]} for x in p.split('|')]
          for p in syl.split(' / ')]
    ipa = '/' + ' '.join(''.join(y['p'] for y in p) for p in sw) + '/'
    return {**it, 'ipa': ipa, 'syl': sw, 'tip': tip}


def build_data():
    """parsed.json（PDF 原文）+ PHON（手写音标/音节/助记）→ data.json"""
    src = os.path.join(HERE, 'parsed.json')
    if not os.path.exists(src):              # 已经有合成好的 data.json 就直接用
        data = json.load(open(os.path.join(HERE, 'data.json'), encoding='utf-8'))
        have = {w['w'] for s in data['sections'] for w in s['words']}
        missing = [enrich(it) for it in EXTRA['words'] if it['w'] not in have]
        if missing:                          # 补充词汇尚未并入缓存时补上
            data['sections'].append({'id': len(data['sections']) + 1,
                                     'cn': EXTRA['cn'], 'en': EXTRA['en'], 'words': missing})
        return data

    d = json.load(open(src, encoding='utf-8'))
    out, sid = {'sections': [], 'frames': d['frames']}, 0
    for s in d['sections']:
        if not s['items']:
            continue
        body = re.match(r'^[一二三四五六七八九]、(.+)$', s['title']).group(1)
        m = re.search(r'(?<=[一-鿿])(?=[A-Za-z])', body)     # 中英文标题分界
        cn, en = (body[:m.start()].strip(), body[m.start():].strip()) if m else (body, '')
        sid += 1
        words = [enrich(it) for it in s['items']]
        out['sections'].append({'id': sid, 'cn': cn, 'en': en, 'words': words})

    sid += 1                                   # 衔接课程带来的补充词汇单列一章
    out['sections'].append({'id': sid, 'cn': EXTRA['cn'], 'en': EXTRA['en'],
                            'words': [enrich(it) for it in EXTRA['words']]})

    json.dump(out, open(os.path.join(HERE, 'data.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    return out


def attach_lessons(data):
    """课时里引用的词必须在词库中查得到，否则「开始学这些词」会点空"""
    have = {w['w'] for s in data['sections'] for w in s['words']}
    for les in LESSONS:
        miss = [v[0] for v in les['vocab'] if v[0] not in have]
        if miss:
            raise SystemExit('第 %s 节引用了词库中不存在的词: %s' % (les['id'], miss))
    data['lessons'] = LESSONS
    return len(LESSONS)


def attach_trans(data):
    """把例句的翻译思路挂上去。独立于 build_data——没有 parsed.json、
    直接吃缓存 data.json 时也要生效。"""
    n, seen = 0, set()
    for s in data['sections']:
        for w in s['words']:
            if w['w'] in TRANS:
                w['tr'] = TRANS[w['w']]; n += 1; seen.add(w['w'])
            else:
                w.pop('tr', None)                  # 标注被删掉时同步清掉
    unknown = set(TRANS) - seen
    if unknown:
        raise SystemExit('trans.py 里有词表中不存在的词条: %s' % sorted(unknown))
    missing = [w['w'] for s in data['sections'] for w in s['words'] if 'tr' not in w]
    if missing:
        print('  ⚠ 尚缺翻译思路 %d 条: %s%s'
              % (len(missing), ', '.join(missing[:6]), ' …' if len(missing) > 6 else ''))
    for w, t in TRANS.items():                      # 结构自检
        for k in ('pat', 'flow', 'core', 'final', 'tip'):
            if k not in t:
                raise SystemExit('%s 缺字段 %s' % (w, k))
        if any(len(x) != 3 for x in t['flow']):
            raise SystemExit('%s 的 flow 每项要写成 [英文, 中文, 成分]' % w)
    # final 各段拼起来必须与原书译文完全一致，防止标注时漏字或改写
    for s in data['sections']:
        for w in s['words']:
            if 'tr' not in w:
                continue
            joined = ''.join(seg[0] for seg in w['tr']['final'])
            if re.sub(r'\s+', '', joined) != re.sub(r'\s+', '', w['exzh']):
                raise SystemExit('%s 的 final 拼接与译文不符:\n  %s\n  %s' % (w['w'], joined, w['exzh']))
    return n


def check(data):
    """音节拼写拼回原词必须一致，否则说明 PHON 写错了"""
    bad = []
    for s in data['sections']:
        for w in s['words']:
            rebuilt = ' '.join(''.join(y['t'] for y in p) for p in w['syl'])
            norm = lambda x: x.replace('-', '').replace(' ', '').lower()
            if norm(rebuilt) != norm(w['w']):
                bad.append((w['w'], rebuilt))
    if bad:
        raise SystemExit('音节拼写与原词不符: %s' % bad)
    return sum(len(s['words']) for s in data['sections'])


if __name__ == '__main__':
    data = build_data()
    n = check(data)
    ntr = attach_trans(data)
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
    print('built %s — %d 词（%d 句带翻译思路）, %d 节预习, %d KB'
          % (dst, n, ntr, nles, round(os.path.getsize(dst) / 1024)))
