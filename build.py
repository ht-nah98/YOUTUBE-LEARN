"""Ghép slides/<id>.html (thứ tự trong deck.json) thành index.html xem được ở local.
python3 build.py  →  index.html ;  xem: python3 -m http.server 8790  →  http://localhost:8790
Phím: ← → / Space chuyển slide · N bật/tắt ghi chú người nói · F toàn màn hình · O xem tổng quan"""
import json, re
from pathlib import Path

HERE = Path(__file__).parent
# ảnh đã tải lên lúc làm bản claude.ai → tên file trong img/
BLOB = {
    '95944c3c660dd54444cba17b417d1833': 'ab_geo60.jpg', '2a94e6f56960f1b132675629f1adbfeb': 'ab_strip.jpg',
    '13f7f219b6e6cee45829cdda92170fc5': 'dip_012.jpg', 'a1147251977cd621942e8da0186badbf': 'dip_1100.jpg',
    '56353cf0a2d67109be637657c109c1c9': 'dip_1156.jpg', '6bf5be1a7ae17fbcc922f61cc2695bd4': 'dip_1208.jpg',
    '824e2d538ab0eb06f8804b1467212ab7': 'dip_1402.jpg', '3e841b676a36df5c8a15325618a795a2': 'dip_1504.jpg',
    'c6fa3971c50a865152b4775620509472': 'dip_414.jpg', 'dc3365020156f3e9a46e028e7a2b1e5f': 'dip_622.jpg',
    '768d6b4630d863d24a2ae80d28a5b154': 'dip_852.jpg', '16ace52e315555304e40b31fd8523017': 'dip_928.jpg',
    'df94f488c16afb93bbb8632b9a862341': 'intro_gap.jpg', '071c2e31f403d2ae5878f7d54da53aae': 'intro_input.jpg',
    'ebfaf60b25019981954c93b84c0d76bd': 'intro_train.jpg', '8f4fd2cd69b563bf381cc1fb1d19d073': 'ret_a.jpg',
    '8f4ffe083a699579505beb44ed12192e': 'tp_c.jpg', '546ef4679ac2922627af01a765704904': 'tp_narrator.jpg',
    'efe2cc95a2a434b401b6aef900213282': 'tp_photo.jpg', 'c0ded9b94b5810b3aedbef0cb47b993f': 'wa_20.jpg',
    '5d6e5e2ba1a5b55bd688162d03263b0a': 'wa_70.jpg',
    '1e46245a0c0cab938f32be820abace6a': 'thumb_5wvmDSMH9AM.jpg', '9e2cbacddcbbcc115f7401e13e6fe0ae': 'thumb_5zu8s38ZwtQ.jpg',
    '9920fb8e3d432b37ecd85c720b0c9d4b': 'thumb_B1J6Ou4q8vE.jpg', 'fc067ade3ed16c30348d4ca392d43cd1': 'thumb_HZGCoVF3YvM.jpg',
    'e388ecd4742997f9367809baef9cbc6e': 'thumb_KE4zqD0ONDI.jpg', '2369f43346958ceadf785c8edeef1ac3': 'thumb_KzfWUEJjG18.jpg',
    'c544a47b6bde5dc118ceaad83518afd1': 'thumb_UXk8T9fpcWQ.jpg', '299276a093e78269b06de9d0e619a1ad': 'thumb_VEJWE6cpqw0.jpg',
    '386636453def2b80b2fce642d1d9cf14': 'thumb_eRWyf-oDdCI.jpg', '7844283e86cc8efb03d0b62db6c790c5': 'thumb_iCAdtp_CNno.jpg',
    '30cd83e743ed1e32d6b6ebdc39ceb3a3': 'thumb_mOFJLBV0LbM.jpg', '672fff0255f158a0c0ed4c677febc0fb': 'thumb_weWQ6sb9R30.jpg',
}

PAGE = """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,700;0,800;1,400&family=Lora:ital,wght@0,500;1,500&display=swap">
<style>
html,body{margin:0;height:100%%;background:#0d0e11;overflow:hidden}
#stage{position:absolute;left:50%%;top:50%%;width:1920px;height:1080px;transform-origin:50%% 50%%}
section{position:absolute;inset:0;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column}
section:not(.on){display:none!important}
section *{margin:0;box-sizing:border-box}
section ul,section ol{padding-left:1.2em}
table{border-collapse:collapse;width:100%%}
th,td{padding:.35em .6em;border-bottom:1px solid rgba(0,0,0,.12);text-align:left;vertical-align:top}
th{font-weight:700}
aside{display:none}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:38vh;overflow:auto;background:#1d2027ee;color:#e8e6e1;
 font:18px/1.5 'Be Vietnam Pro',sans-serif;padding:16px 24px;display:none;white-space:pre-wrap}
#bar{position:fixed;right:16px;bottom:12px;color:#888;font:14px sans-serif}
body.ov #stage{display:none} #ov{display:none} body.ov #ov{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;padding:16px;
 height:100%%;overflow:auto;box-sizing:border-box} #ov div{color:#ddd;font:14px sans-serif;background:#222;padding:10px;cursor:pointer;border-radius:6px}
</style></head><body>
<div id="stage">%(slides)s</div><div id="ov"></div><div id="notes"></div><div id="bar"></div>
<script>
const S=[...document.querySelectorAll('#stage>section')],st=document.getElementById('stage'),nt=document.getElementById('notes'),bar=document.getElementById('bar');
let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1)),notes=false;
function fit(){const k=Math.min(innerWidth/1920,innerHeight/1080);st.style.transform=`translate(-50%%,-50%%) scale(${k})`;}
function show(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,j)=>s.classList.toggle('on',j===i));
 const a=S[i].querySelector('aside');nt.textContent=a?a.textContent.trim():'';nt.style.display=notes&&a?'block':'none';
 bar.textContent=(i+1)+' / '+S.length;history.replaceState(null,'','#'+(i+1));}
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(i+1);else if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);
 else if(e.key==='n'||e.key==='N'){notes=!notes;show(i)}else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
 else if(e.key==='o'||e.key==='O'){document.body.classList.toggle('ov')}else if(e.key==='Home')show(0);else if(e.key==='End')show(S.length-1);});
addEventListener('click',e=>{if(document.body.classList.contains('ov'))return;e.clientX>innerWidth/2?show(i+1):show(i-1)});
const ov=document.getElementById('ov');S.forEach((s,j)=>{const d=document.createElement('div');const h=s.querySelector('h1,h2');
 d.textContent=(j+1)+'. '+(h?h.textContent:s.id);d.onclick=()=>{document.body.classList.remove('ov');show(j)};ov.appendChild(d)});
addEventListener('resize',fit);fit();show(i);
</script></body></html>"""


def main():
    deck = json.loads((HERE / 'deck.json').read_text())
    parts = []
    for sid in deck['order']:
        f = HERE / 'slides' / f'{sid}.html'
        if not f.exists():
            continue
        s = f.read_text()
        s = re.sub(r'/_blob/([0-9a-f]{32})', lambda m: 'img/' + BLOB[m.group(1)], s)
        parts.append(s)
    (HERE / 'index.html').write_text(PAGE % {'title': deck['title'], 'slides': '\n'.join(parts)})
    print(f'index.html · {len(parts)}/{len(deck["order"])} slide')


if __name__ == '__main__':
    main()
