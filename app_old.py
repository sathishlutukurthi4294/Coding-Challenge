import streamlit as st
import streamlit.components.v1 as components
import requests, json, re, time, hashlib, random, html as _html
from pathlib import Path

st.set_page_config(page_title='DoTT Connect | AURA Coding Challenge', page_icon='⚡', layout='wide', initial_sidebar_state='collapsed')
LOGO = Path(__file__).parent / 'assets' / 'aditya_ctt_logo.png'
TIMER_SECONDS = 60  # challenge countdown length

for k,v in {
    'stage':'welcome','language':None,'question':None,'start_time':None,'elapsed':None,
    'history':[],'participant_no':1,'api_error':None,'source':None,
    'api_url':'','api_key':'','model':'nemotron-ultra'
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

# If the on-screen countdown ran out, the challenge card redirects here with
# ?aura_timeout=1 — send the participant straight back to the Home screen.
if st.query_params.get('aura_timeout')=='1':
    st.query_params.clear()
    if st.session_state.stage=='challenge':
        for k,v in {'stage':'welcome','language':None,'question':None,'start_time':None,'elapsed':None,'api_error':None,'source':None}.items():
            st.session_state[k]=v
    st.rerun()

st.markdown('''
<style>
:root{
  --navy:#0b2350; --navy-700:#123566; --blue:#1a4b9c; --blue-2:#2f66bf;
  --blue-soft:#eef3fc; --blue-line:#d9e5f6;
  --gold:#c8922a; --gold-2:#e0a938; --gold-deep:#9c6f1c; --gold-soft:#f7efda; --gold-line:#ecdcb6;
  --page:#f4f7fc; --surface:#ffffff; --ink:#132741; --muted:#5f7189; --line:#e6ecf4;
  --shadow:0 18px 40px rgba(11,35,80,.10); --shadow-sm:0 8px 20px rgba(11,35,80,.06);
}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

html,body,[data-testid="stAppViewContainer"],.stApp{height:100vh!important;overflow:hidden!important}
[data-testid="stHeader"],[data-testid="stSidebar"],footer{display:none!important}
[data-testid="stMainBlockContainer"]{height:100vh!important;max-width:1560px!important;padding:16px 30px 18px!important;overflow:hidden!important}
*{font-family:Inter,Arial,sans-serif}
.stApp{
  background:
    radial-gradient(920px 420px at 100% -8%,rgba(26,75,156,.10),transparent 60%),
    radial-gradient(760px 380px at -6% 4%,rgba(200,146,42,.10),transparent 58%),
    linear-gradient(180deg,#f6f9fe,#eef3fb 60%,#f6f9fe);
}

/* ---------- Header brand ---------- */
.brand-wrap{animation:fadeUp .6s ease both;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;line-height:1.05}
.brand-kicker{display:inline-flex;align-items:center;gap:6px;font-size:9px;font-weight:800;letter-spacing:.22em;text-transform:uppercase;color:var(--gold-deep);margin-bottom:5px}
.brand-kicker:before{content:"";width:16px;height:2px;border-radius:2px;background:linear-gradient(90deg,var(--gold),var(--gold-2))}
.brand-title{font-size:30px;font-weight:900;letter-spacing:-.8px;line-height:1;
  background:linear-gradient(90deg,var(--navy),var(--blue) 34%,var(--gold) 56%,var(--blue) 78%,var(--navy));
  background-size:280% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 8s linear infinite}
.brand-sub{font-size:11.5px;color:var(--muted);margin-top:4px;font-weight:500}
@keyframes shine{to{background-position:280% 0}}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

/* ---------- Hero (welcome only) ---------- */
.hero{margin-top:14px;background:
     radial-gradient(560px 260px at 88% -40%,rgba(224,169,56,.28),transparent 60%),
     linear-gradient(135deg,var(--navy),var(--blue) 62%,var(--blue-2));
  border-radius:22px;padding:22px 28px;color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden;
  border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:18px;animation:fadeUp .5s ease both}
.hero-badge{flex:none;width:52px;height:52px;border-radius:16px;display:flex;align-items:center;justify-content:center;
  font-size:26px;background:linear-gradient(135deg,rgba(255,255,255,.18),rgba(255,255,255,.05));
  border:1px solid rgba(255,255,255,.22);box-shadow:inset 0 1px 0 rgba(255,255,255,.25)}
.hero-txt h1{margin:0;font-size:23px;font-weight:900;letter-spacing:-.5px}
.hero-txt p{margin:4px 0 0;font-size:12px;opacity:.86;font-weight:500}
.hero-pill{margin-left:auto;flex:none;font-size:10px;font-weight:800;letter-spacing:.06em;color:#fff;
  background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);padding:7px 12px;border-radius:999px;white-space:nowrap}

/* ---------- Welcome copy ---------- */
.eyebrow{color:var(--blue);font-weight:900;font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;margin-top:22px;display:flex;align-items:center;gap:7px}
.eyebrow:before{content:"";width:14px;height:2px;border-radius:2px;background:var(--gold)}
.title{font-size:23px;color:var(--navy);font-weight:900;margin:5px 0 2px;letter-spacing:-.4px}
.sub{font-size:12px;color:var(--muted);font-weight:500;max-width:100%;line-height:1.55;margin-bottom:18px}

/* ---------- Language pick cards ---------- */
.lang-card{position:relative;min-height:172px;border-radius:20px;padding:20px;background:var(--surface);
  border:1px solid var(--line);box-shadow:var(--shadow-sm);overflow:hidden;transition:transform .16s ease,box-shadow .16s ease}
.lang-card:before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:linear-gradient(90deg,var(--gold),var(--gold-2))}
.lang-card.blue:before{background:linear-gradient(90deg,var(--blue),var(--blue-2))}
.lang-card:hover{transform:translateY(-3px);box-shadow:var(--shadow)}
.lang-top{display:flex;align-items:center;gap:12px}
.lang-icon{width:50px;height:50px;border-radius:15px;display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:900;flex:none}
.lang-icon.c{background:var(--blue-soft);color:var(--blue);border:1px solid var(--blue-line)}
.lang-icon.py{background:var(--gold-soft);color:var(--gold-deep);border:1px solid var(--gold-line)}
.lang-title{font-size:19px;font-weight:900;color:var(--navy);letter-spacing:-.3px}
.lang-kicker{font-size:9.5px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:2px}
.lang-sub{font-size:11px;color:var(--muted);line-height:1.55;margin-top:13px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:13px}
.chip{font-size:9px;font-weight:700;color:var(--blue);background:var(--blue-soft);border:1px solid var(--blue-line);padding:4px 9px;border-radius:999px}
.level{position:absolute;top:18px;right:18px;background:var(--gold-soft);border:1px solid var(--gold-line);color:var(--gold-deep);
  font-size:8px;font-weight:900;letter-spacing:.05em;padding:5px 9px;border-radius:999px}

/* ---------- Process flow ---------- */
.flow{margin-top:22px;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap}
.node{display:flex;align-items:center;gap:7px;padding:8px 14px;background:var(--surface);border:1px solid var(--line);
  border-radius:11px;color:var(--navy);font-size:10.5px;font-weight:700;box-shadow:var(--shadow-sm)}
.node .num{width:18px;height:18px;border-radius:50%;background:var(--blue-soft);color:var(--blue);border:1px solid var(--blue-line);
  display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:900}
.arr{color:var(--gold);font-size:13px;font-weight:900}

/* ---------- Result card ---------- */
.result-card{position:relative;max-width:540px;margin:26px auto 0;text-align:center;
  background:var(--surface);border:1px solid var(--line);border-radius:26px;padding:36px 36px 30px;
  box-shadow:var(--shadow);overflow:hidden;animation:cardPop .55s cubic-bezier(.16,1,.3,1) both}
.result-card:before{content:"";position:absolute;inset:0 0 auto 0;height:5px;background:linear-gradient(90deg,#12915a,#3fbf83)}
.result-card.no:before{background:linear-gradient(90deg,#d33b3b,#f0776f)}
.result-card:after{content:"";position:absolute;width:340px;height:340px;border-radius:50%;top:-200px;left:50%;
  transform:translateX(-50%);pointer-events:none;background:radial-gradient(circle,rgba(63,191,131,.20),transparent 62%)}
.result-card.no:after{background:radial-gradient(circle,rgba(240,119,111,.20),transparent 62%)}

.result-icon{position:relative;width:84px;height:84px;border-radius:26px;display:flex;align-items:center;justify-content:center;
  font-size:41px;margin:0 auto 16px;box-shadow:var(--shadow-sm);animation:iconPop .6s cubic-bezier(.16,1.5,.3,1) .12s both}
.result-icon:before{content:"";position:absolute;inset:-8px;border-radius:32px;border:2px solid currentColor;opacity:.3;animation:ringPulse 1.9s ease-out .45s infinite}
.success{background:#e9f9ef;color:#12915a;border:1px solid #c7ecd6}
.bad{background:#fff1f0;color:#d33b3b;border:1px solid #f7d3d1}

.result-title{font-size:27px;font-weight:900;color:var(--navy);letter-spacing:-.5px;animation:riseIn .5s ease .18s both}
.result-copy{font-size:12.5px;color:var(--muted);font-weight:500;margin-top:4px;animation:riseIn .5s ease .24s both}

.rc-time-wrap{margin:20px auto 2px;display:inline-flex;flex-direction:column;align-items:center;gap:5px;
  background:linear-gradient(180deg,#fbf6ea,#f6edd7);border:1px solid var(--gold-line);border-radius:18px;
  padding:13px 34px;box-shadow:inset 0 1px 0 rgba(255,255,255,.65);animation:riseIn .5s ease .3s both}
.rc-time-label{font-size:9px;font-weight:900;letter-spacing:.22em;color:var(--gold-deep)}
.result-time{font-family:'JetBrains Mono',Consolas,monospace;color:var(--gold-deep);font-size:41px;font-weight:700;letter-spacing:-1px;line-height:1}
.result-meta{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:20px;animation:riseIn .5s ease .38s both}
.result-meta .rm{font-size:10px;font-weight:700;color:var(--navy);background:#fff;border:1px solid var(--line);
  border-radius:999px;padding:6px 13px;box-shadow:var(--shadow-sm)}

@keyframes cardPop{from{opacity:0;transform:translateY(18px) scale(.96)}to{opacity:1;transform:none}}
@keyframes iconPop{0%{opacity:0;transform:scale(.4)}60%{transform:scale(1.12)}100%{opacity:1;transform:scale(1)}}
@keyframes ringPulse{0%{transform:scale(1);opacity:.35}70%{transform:scale(1.2);opacity:0}100%{opacity:0}}
@keyframes riseIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

/* ---------- Section label (review decision) ---------- */
.dec-label{font-size:11px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
  margin:16px 0 2px;display:flex;align-items:center;gap:8px}
.dec-label:before{content:"";width:14px;height:2px;border-radius:2px;background:var(--gold)}

/* ---------- Buttons ---------- */
div.stButton{display:flex;justify-content:center}
div.stButton>button{width:auto!important;min-height:46px!important;padding:10px 26px!important;
  border-radius:13px!important;font-size:13.5px!important;font-weight:800!important;letter-spacing:.01em!important;
  transition:transform .14s ease,filter .14s ease,box-shadow .14s ease}
div.stButton>button:hover{transform:translateY(-2px)}
div.stButton>button:active{transform:translateY(0)}
div.stButton>button[kind="primary"],
div.stButton [data-testid="baseButton-primary"],
div.stButton [data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,var(--navy),var(--blue) 72%,var(--blue-2))!important;
  border:1px solid var(--navy)!important;color:#fff!important;box-shadow:0 10px 22px rgba(11,35,80,.24)!important;}
div.stButton>button[kind="primary"]:hover{filter:brightness(1.06)}
div.stButton>button[kind="secondary"],
div.stButton [data-testid="baseButton-secondary"],
div.stButton [data-testid="stBaseButton-secondary"]{
  background:var(--surface)!important;border:1.5px solid var(--gold-line)!important;color:var(--gold-deep)!important;
  box-shadow:var(--shadow-sm)!important}
div.stButton>button[kind="secondary"]:hover{background:var(--gold-soft)!important}

/* ---------- AURA config pill (popover trigger) ---------- */
[data-testid="stPopover"]{display:flex;justify-content:flex-end}
[data-testid="stPopover"] button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]),
[data-testid="stPopoverButton"]{
  width:auto!important;min-height:44px!important;border-radius:999px!important;
  background:linear-gradient(180deg,#ffffff,#eef4fd)!important;
  border:1px solid #d7e1f0!important;color:var(--navy)!important;
  font-weight:800!important;font-size:12.5px!important;letter-spacing:.01em!important;
  padding:10px 20px!important;box-shadow:0 6px 16px rgba(11,35,80,.08)!important;
  transition:transform .14s ease,box-shadow .14s ease,border-color .14s ease!important}
[data-testid="stPopover"] button:not([kind="primary"]):hover,
[data-testid="stPopoverButton"]:hover{
  transform:translateY(-1px)!important;border-color:#c2d2ea!important;
  box-shadow:0 10px 22px rgba(11,35,80,.14)!important}
[data-testid="stPopover"] button:not([kind="primary"]) p,
[data-testid="stPopoverButton"] p{font-weight:800!important;color:var(--navy)!important;margin:0!important}
[data-testid="stPopover"] button:not([kind="primary"]) svg,
[data-testid="stPopoverButton"] svg{color:#8496ad!important;fill:#8496ad!important;width:16px!important;height:16px!important}

/* ---------- Right-column timer button spacing (challenge stage) ---------- */
.timer-col-btn{margin-top:14px}

/* ---------- Spinner text in red ---------- */
[data-testid="stSpinner"]{color:#d33b3b!important}
[data-testid="stSpinner"] p{color:#d33b3b!important;font-weight:700!important}
[data-testid="stSpinner"] svg{color:#d33b3b!important;fill:#d33b3b!important}
</style>

''', unsafe_allow_html=True)

# ---------------- Header ----------------
l,c,r = st.columns([1.15,2.0,1.15], vertical_alignment='center')
with l:
    if LOGO.exists():
        st.image(str(LOGO), width=225)
with c:
    st.markdown('<div class="brand-wrap"><span class="brand-kicker">AURA Coding Challenge</span><div class="brand-title">DoTT Connect 2026</div><div class="brand-sub">First-year output-prediction sprint · powered by AURA</div></div>', unsafe_allow_html=True)
with r:
    ready=bool(st.session_state.api_url and st.session_state.api_key)
    label = '🟢 AURA Ready' if ready else '🟡 AURA Setup'
    with st.popover(label, use_container_width=True):
        st.markdown('### AURA Connection')
        st.caption('Configure once before the event starts.')
        u=st.text_input('API Endpoint',value=st.session_state.api_url,placeholder='http://server/v1/chat/completions')
        k=st.text_input('API Key',value=st.session_state.api_key,type='password',placeholder='Paste API key')
        m=st.text_input('Model',value=st.session_state.model)
        if st.button('Save Connection',type='primary',use_container_width=True):
            st.session_state.api_url=u.strip(); st.session_state.api_key=k.strip(); st.session_state.model=m.strip() or 'nemotron-ultra'; st.success('Saved'); time.sleep(.2); st.rerun()

# Hero: welcome only
if st.session_state.stage=='welcome':
    st.markdown('''<div class="hero"><div class="hero-badge">⚡</div><div class="hero-txt"><h1>Coding Challenge</h1><p>A fast, fair first-year coding experience powered by AURA</p></div><span class="hero-pill">20–60 sec · Predict the Output</span></div>''', unsafe_allow_html=True)

BANK={
'Python':[
{'question':'Predict the exact output.','code':'x = 4\ny = 3\nprint(x + y * 2)','answer':'10','explanation':'3 × 2 = 6, then 4 + 6 = 10.'},
{'question':'Predict the exact output.','code':"name = 'AURA'\nprint(name[0], name[-1])",'answer':'A A','explanation':'Index 0 is first; -1 is last.'},
{'question':'What is the output?','code':'x = [2, 4, 6]\nx.append(8)\nprint(len(x))','answer':'4','explanation':'append() adds one element.'},
{'question':'Predict the output.','code':"for i in range(1, 5, 2):\n    print(i, end=' ')",'answer':'1 3','explanation':'range uses 1 and 3, stopping before 5.'},
{'question':'What is the output?','code':'a = 9\nb = 4\nprint(a // b, a % b)','answer':'2 1','explanation':'Integer division gives 2 and remainder gives 1.'}],
'C':[
{'question':'Predict the exact output.','code':'int a = 5, b = 2;\nprintf("%d", a + b * 3);','answer':'11','explanation':'2 × 3 = 6, then 5 + 6 = 11.'},
{'question':'What is printed?','code':'int x = 7;\nprintf("%d", x % 3);','answer':'1','explanation':'7 divided by 3 leaves remainder 1.'},
{'question':'Predict the output.','code':'int x = 4;\nx += 3;\nprintf("%d", x);','answer':'7','explanation':'x += 3 means x = x + 3.'},
{'question':'What is the output?','code':'int i;\nfor(i = 0; i < 3; i++)\n    printf("%d ", i);','answer':'0 1 2','explanation':'The loop runs for 0, 1 and 2.'},
{'question':'Predict the output.','code':'int a = 10, b = 4;\nprintf("%d", a / b);','answer':'2','explanation':'Integer division gives 2.'}]}

def qhash(q): return hashlib.sha256((q['code']+'|'+q['answer']).encode()).hexdigest()[:16]
def fallback(lang):
    used=set(st.session_state.history[-20:]); pool=[q for q in BANK[lang] if qhash(q) not in used] or BANK[lang]; q=random.choice(pool).copy(); q.update(language=lang,difficulty='First-Year Standard'); return q

def parse_json(text):
    try:return json.loads(text)
    except:
        m=re.search(r'\{.*\}',text,re.S)
        if m:return json.loads(m.group(0))
    raise ValueError('Invalid JSON')

def generate(lang):
    if not st.session_state.api_url or not st.session_state.api_key:
        st.session_state.api_error='AURA is not configured — local fallback used.'; st.session_state.source='Local Fallback'; return fallback(lang)
    prompt=f'''Generate ONE fair coding-stall challenge for FIRST-YEAR engineering students.
Language: {lang}
Challenge type: Predict exact output.
Difficulty: fixed Beginner-to-Moderate, same level for every participant.
Expected solve time: 20-60 seconds.
Use only fundamentals and short deterministic code.
C: variables, arithmetic, conditions, simple loops, very basic arrays, printf.
Python: variables, arithmetic, strings, lists, indexing, conditions, simple loops/range, len/sum/append.
Never use recursion, pointers, dynamic memory, OOP, file handling, advanced libraries, undefined/platform-dependent behavior, or obscure tricks.
Return ONLY JSON:
{{"question":"Predict the exact output.","code":"short code","answer":"exact output","explanation":"short explanation","difficulty":"First-Year Standard","language":"{lang}"}}'''
    try:
        r=requests.post(st.session_state.api_url,headers={'Authorization':f'Bearer {st.session_state.api_key}','Content-Type':'application/json'},json={'model':st.session_state.model,'messages':[{'role':'system','content':'Return only valid JSON.'},{'role':'user','content':prompt}],'temperature':0.8},timeout=35)
        r.raise_for_status(); d=r.json(); raw=d['choices'][0]['message']['content'] if 'choices' in d else d.get('response') or d.get('text') or json.dumps(d); q=parse_json(raw)
        for f in ['question','code','answer','explanation']:
            if not str(q.get(f,'')).strip(): raise ValueError('Missing '+f)
        banned=['malloc','calloc','realloc','struct ','union ','->','class ','lambda ','async ','await ','numpy','pandas']
        if any(x in q['code'].lower() for x in banned): raise ValueError('Outside first-year scope')
        q.update(language=lang,difficulty='First-Year Standard'); st.session_state.api_error=None; st.session_state.source='AURA AI'; return q
    except Exception as e:
        st.session_state.api_error=f'AURA unavailable — fallback used. ({e})'; st.session_state.source='Local Fallback'; return fallback(lang)

def code_card_height(code, with_answer=False):
    """Estimate a component iframe height tall enough for the full code block
    (chrome + header + one line per code line), so long snippets never clip."""
    lines = code.count('\n') + 1
    base = 210 + lines*24
    if with_answer:
        base += 120
    return int(min(680, max(384, base)))

def review_panel_height(explanation):
    """Estimate height for the right-hand review panel (ring + correct-output box)."""
    lines = max(1, (len(explanation)//55)+1)
    return int(min(640, max(460, 300 + lines*20)))

def fmt(sec):
    if sec is None:return '00:00.000'
    m=int(sec//60); s=int(sec%60); ms=int((sec-int(sec))*1000); return f'{m:02d}:{s:02d}.{ms:03d}'
def start(lang):
    st.session_state.language=lang
    with st.spinner(f'AURA is preparing a fresh {lang} challenge...'): q=generate(lang)
    st.session_state.question=q; st.session_state.history.append(qhash(q)); st.session_state.start_time=time.perf_counter(); st.session_state.elapsed=None; st.session_state.stage='challenge'; st.rerun()
def review(): st.session_state.elapsed=time.perf_counter()-st.session_state.start_time; st.session_state.stage='review'; st.rerun()
def judge(ok): st.session_state.stage='correct' if ok else 'wrong'; st.rerun()
def nxt():
    st.session_state.participant_no+=1
    for k,v in {'stage':'welcome','language':None,'question':None,'start_time':None,'elapsed':None,'api_error':None,'source':None}.items(): st.session_state[k]=v
    st.rerun()

# ---- shared styling for the code/timer cards ----
CARD_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
*{box-sizing:border-box;font-family:Inter,Arial,sans-serif}
html,body{height:100%}
body{margin:0;background:transparent}
.cc{background:#fff;border:1px solid #e6ecf4;border-radius:22px;box-shadow:0 18px 40px rgba(11,35,80,.10);overflow:hidden;height:100%;display:flex;flex-direction:column}
.cc-head{display:flex;align-items:center;justify-content:space-between;padding:14px 22px;
  border-bottom:1px solid #eef2f8;gap:10px;flex-wrap:wrap;
  background:linear-gradient(180deg,#fbfcff,#f4f7fc);flex:none}
.eye{display:flex;align-items:center;gap:8px;color:#1a4b9c;font-weight:900;font-size:10px;letter-spacing:.16em;text-transform:uppercase}
.eye:before{content:"";width:15px;height:2px;border-radius:2px;background:#c8922a}
.metas{display:flex;gap:6px;flex-wrap:wrap}
.meta{background:#eef3fc;border:1px solid #d9e5f6;color:#1a4b9c;border-radius:999px;padding:4px 11px;font-size:8.5px;font-weight:800;letter-spacing:.02em}
.cc-body{display:flex;gap:22px;padding:20px 22px;align-items:stretch;flex:1;min-height:0}
.cc-left{flex:1.65;min-width:0;display:flex;flex-direction:column;min-height:0}
.cc-right{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}
.qtitle{font-size:17px;font-weight:900;color:#0b2350;margin:0 0 12px;letter-spacing:-.3px;flex:none}
.editor{border-radius:16px;overflow:hidden;border:1px solid #16304f;box-shadow:0 12px 26px rgba(11,25,45,.28);
  display:flex;flex-direction:column;flex:1;min-height:0}
.etop{height:32px;background:#0f2338;display:flex;align-items:center;justify-content:space-between;padding:0 13px;color:#93a6bb;font-size:9px;font-weight:600;flex:none}
.dots{display:flex;gap:5px}.d{width:9px;height:9px;border-radius:50%}.rr{background:#ff5f57}.yy{background:#febc2e}.gg{background:#28c840}
.file{letter-spacing:.03em}
.code{background:linear-gradient(150deg,#0a182c,#0e2138);color:#eaf3ff;padding:16px 18px;
  font-family:'JetBrains Mono',Consolas,monospace;font-size:15px;line-height:1.55;white-space:pre-wrap;
  flex:1;min-height:0;overflow:auto;margin:0}
.answer{margin-top:14px;background:linear-gradient(180deg,#f0f5fd,#eaf1fb);border:1px solid #cfe0f5;
  border-left:5px solid #1a4b9c;border-radius:14px;padding:13px 16px;color:#1c405f;font-size:13.5px;flex:none}
.answer .alab{display:block;font-size:9px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;color:#1a4b9c;margin-bottom:5px}
.answer .aval{font-family:'JetBrains Mono',Consolas,monospace;font-weight:700;font-size:15px;color:#0b2350}
.answer .aexp{display:block;color:#6c8098;font-size:11px;margin-top:7px;line-height:1.5}
.ring{width:158px;height:158px;border-radius:50%;
  background:conic-gradient(#c8922a 0deg,#e8c27a 150deg,#eef2f8 150deg);padding:10px;
  box-shadow:0 14px 28px rgba(200,146,42,.20)}
.ring-in{width:100%;height:100%;border-radius:50%;background:#fff;border:1px solid #f0e6cf;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px}
.tl{font-size:8.5px;letter-spacing:.22em;color:#9c6f1c;font-weight:900}
.tv2{font-family:'JetBrains Mono',Consolas,monospace;font-size:25px;color:#9c6f1c;font-weight:700;letter-spacing:-.5px}
.tv2.done{color:#d33b3b}
.tfmt{font-family:'JetBrains Mono',Consolas,monospace;font-size:9px;font-weight:700;letter-spacing:.04em;color:#9c6f1c;background:#f7efda;border:1px solid #ecdcb6;border-radius:999px;padding:3px 11px}
.tcap{font-size:9.5px;color:#8496a9;font-weight:600;text-align:center;max-width:160px;line-height:1.4}
/* solo (split-column) variants */
.cc-solo-left .cc-body{padding:20px 22px}
.cc-solo-right{align-items:center;justify-content:center;padding:24px 18px;gap:10px}
.cc-solo-right .answer{align-self:stretch;margin-top:6px}
</style>"""

SCRIPT_TMPL = ("<script>var total=__TOTAL__;var base=__BASE__;var t0=performance.now();"
"function pad(n,l){return String(n).padStart(l,'0');}"
"function tick(){var ms=total-(base+(performance.now()-t0));if(ms<0)ms=0;"
"var m=Math.floor(ms/60000);var s=Math.floor(ms/1000)%60;var f=Math.floor(ms%1000);"
"var el=document.getElementById('tv');if(el){el.textContent=pad(m,2)+':'+pad(s,2)+'.'+pad(f,3);if(ms<=0)el.classList.add('done');}"
"var rg=document.getElementById('ring');if(rg){var a=(ms/total)*360;rg.style.background='conic-gradient(#c8922a 0deg,#e8c27a '+a+'deg,#eef2f8 '+a+'deg)';}"
"if(ms>0){requestAnimationFrame(tick);}else{try{var u=new URL(window.parent.location.href);u.searchParams.set('aura_timeout','1');window.parent.location.href=u.toString();}catch(e){}}}tick();</script>")

def card_html(q, lang, participant, source, eyebrow, timer_ms=None, final_time=None, show_answer=False):
    """Combined code + timer card (used for the review stage)."""
    code=_html.escape(q['code']); question=_html.escape(q['question'])
    metas = f'<span class="meta">Participant #{participant}</span><span class="meta">{lang}</span>'
    if source: metas += f'<span class="meta">{source}</span>'
    ans = ''
    if show_answer:
        ans = (f'<div class="answer"><span class="alab">Correct Output</span>'
               f'<span class="aval">{_html.escape(str(q["answer"]))}</span>'
               f'<span class="aexp">{_html.escape(q["explanation"])}</span></div>')
    live = final_time is None
    label = 'TIME LEFT' if live else 'TIME TAKEN'
    tval = fmt(TIMER_SECONDS) if live else final_time
    tid = ' id="tv"' if live else ''
    ring_id = ' id="ring"' if live else ''
    cap = 'Counting down from 60s — read the code and lock your answer.' if live else 'Time you took before pressing Review Answer.'
    script = SCRIPT_TMPL.replace('__TOTAL__', str(int(TIMER_SECONDS*1000))).replace('__BASE__', str(int(timer_ms or 0))) if live else ''
    body = (
        f'{CARD_CSS}<div class="cc">'
        f'<div class="cc-head"><span class="eye">{eyebrow}</span><div class="metas">{metas}</div></div>'
        f'<div class="cc-body"><div class="cc-left"><div class="qtitle">{question}</div>'
        f'<div class="editor"><div class="etop"><div class="dots"><span class="d rr"></span><span class="d yy"></span><span class="d gg"></span></div>'
        f'<div class="file">{lang.lower()} · read only</div></div><pre class="code">{code}</pre></div>{ans}</div>'
        f'<div class="cc-right"><div class="ring"{ring_id}><div class="ring-in"><div class="tl">{label}</div>'
        f'<div class="tv2"{tid}>{tval}</div></div></div><div class="tfmt">min : sec . ms</div><div class="tcap">{cap}</div></div></div></div>{script}'
    )
    return body

def code_card_html(q, lang, participant, source, eyebrow):
    """Standalone left card: header + full-height code terminal (no timer)."""
    code=_html.escape(q['code']); question=_html.escape(q['question'])
    metas = f'<span class="meta">Participant #{participant}</span><span class="meta">{lang}</span>'
    if source: metas += f'<span class="meta">{source}</span>'
    body = (
        f'{CARD_CSS}<div class="cc cc-solo-left">'
        f'<div class="cc-head"><span class="eye">{eyebrow}</span><div class="metas">{metas}</div></div>'
        f'<div class="cc-body"><div class="cc-left" style="flex:1"><div class="qtitle">{question}</div>'
        f'<div class="editor"><div class="etop"><div class="dots"><span class="d rr"></span><span class="d yy"></span><span class="d gg"></span></div>'
        f'<div class="file">{lang.lower()} · read only</div></div><pre class="code">{code}</pre></div></div></div></div>'
    )
    return body

def timer_card_html(timer_ms=None, final_time=None):
    """Standalone right card: just the countdown ring, meant to sit above the Review Answer button."""
    live = final_time is None
    label = 'TIME LEFT' if live else 'TIME TAKEN'
    tval = fmt(TIMER_SECONDS) if live else final_time
    tid = ' id="tv"' if live else ''
    ring_id = ' id="ring"' if live else ''
    cap = 'Counting down from 60s — read the code and lock your answer.' if live else 'Time you took before pressing Review Answer.'
    script = SCRIPT_TMPL.replace('__TOTAL__', str(int(TIMER_SECONDS*1000))).replace('__BASE__', str(int(timer_ms or 0))) if live else ''
    body = (
        f'{CARD_CSS}<div class="cc cc-solo-right">'
        f'<div class="ring"{ring_id}><div class="ring-in"><div class="tl">{label}</div>'
        f'<div class="tv2"{tid}>{tval}</div></div></div><div class="tfmt">min : sec . ms</div><div class="tcap">{cap}</div>'
        f'</div>{script}'
    )
    return body

def review_side_html(final_time, q):
    """Right-column panel for the review stage: time-taken ring + Correct Output box stacked below it."""
    ans = (f'<div class="answer"><span class="alab">Correct Output</span>'
           f'<span class="aval">{_html.escape(str(q["answer"]))}</span>'
           f'<span class="aexp">{_html.escape(q["explanation"])}</span></div>')
    body = (
        f'{CARD_CSS}<div class="cc cc-solo-right" style="justify-content:flex-start;padding-top:26px">'
        f'<div class="ring"><div class="ring-in"><div class="tl">TIME TAKEN</div>'
        f'<div class="tv2">{final_time}</div></div></div>'
        f'<div class="tfmt">min : sec . ms</div>'
        f'<div class="tcap">Time you took before pressing Review Answer.</div>'
        f'{ans}'
        f'</div>'
    )
    return body

# ================= STAGES (each renders exactly once) =================
if st.session_state.stage=='welcome':
    st.markdown('<div class="eyebrow">Participant Experience</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="title">Participant #{st.session_state.participant_no} · Pick Your Challenge</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Choose your preferred language. AURA generates a fresh question at the same first-year difficulty for every participant.</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="lang-card blue"><span class="level">FIRST-YEAR STANDARD</span><div class="lang-top"><div class="lang-icon c">C</div><div><div class="lang-title">C Programming</div><div class="lang-kicker">Output Prediction</div></div></div><div class="lang-sub">Core fundamentals kept short and deterministic — perfect for a quick, fair sprint.</div><div class="chips"><span class="chip">Operators</span><span class="chip">Conditions</span><span class="chip">Loops</span><span class="chip">Basic Arrays</span></div></div><br/>',unsafe_allow_html=True)
        if st.button('Start C Challenge',type='primary',use_container_width=True): start('C')
    with c2:
        st.markdown('<div class="lang-card"><span class="level">FIRST-YEAR STANDARD</span><div class="lang-top"><div class="lang-icon py">Py</div><div><div class="lang-title">Python Programming</div><div class="lang-kicker">Output Prediction</div></div></div><div class="lang-sub">Strings, lists and simple loops — readable code that rewards careful tracing.</div><div class="chips"><span class="chip">Strings</span><span class="chip">Lists</span><span class="chip">Conditions</span><span class="chip">Loops</span></div></div><br/>',unsafe_allow_html=True)
        if st.button('Start Python Challenge',type='primary',use_container_width=True): start('Python')
    st.markdown('<div class="flow"><span class="node"><span class="num">1</span>Choose</span><span class="arr">→</span><span class="node"><span class="num">2</span>Think</span><span class="arr">→</span><span class="node"><span class="num">3</span>Tell Answer</span><span class="arr">→</span><span class="node"><span class="num">4</span>Review</span><span class="arr">→</span><span class="node"><span class="num">5</span>Result</span></div>',unsafe_allow_html=True)

elif st.session_state.stage=='challenge':
    q=st.session_state.question
    elapsed_ms=int(max(0.0,(time.perf_counter()-st.session_state.start_time))*1000)
    card_h = code_card_height(q['code'])
    col_l, col_r = st.columns([1.65, 1], gap="medium")
    with col_l:
        components.html(
            code_card_html(q, st.session_state.language, st.session_state.participant_no, st.session_state.source,
                            'Challenge · Predict the Output'),
            height=card_h, scrolling=False)
    with col_r:
        components.html(timer_card_html(timer_ms=elapsed_ms), height=max(310, min(card_h, 400)), scrolling=False)
        st.markdown('<div class="timer-col-btn"></div>', unsafe_allow_html=True)
        if st.button('🔍 Review Answer', type='primary', use_container_width=True): review()

elif st.session_state.stage=='review':
    q=st.session_state.question
    left_h = code_card_height(q['code'])
    right_h = review_panel_height(q['explanation'])
    col_l, col_r = st.columns([1.65, 1], gap="medium")
    with col_l:
        components.html(
            code_card_html(q, st.session_state.language, st.session_state.participant_no, None,
                            'Review · Predict the Output'),
            height=left_h, scrolling=False)
    with col_r:
        components.html(review_side_html(fmt(st.session_state.elapsed), q), height=right_h, scrolling=False)
        st.markdown('<div class="dec-label" style="margin-top:14px">Stall In-charge Decision</div>', unsafe_allow_html=True)
        bl, br = st.columns(2, gap="small")
        with bl:
            if st.button('✅ RIGHT', type='primary', use_container_width=True): judge(True)
        with br:
            if st.button('❌ WRONG', use_container_width=True): judge(False)

else:
    good=st.session_state.stage=='correct'
    if good:
        st.balloons()
        state,icon_cls,icon='ok','success','✓'
        rtitle,rcopy='Congratulations!','Correct answer — a great start to your coding journey.'
    else:
        state,icon_cls,icon='no','bad','×'
        rtitle,rcopy='Good Attempt!','Keep exploring — every challenge makes you stronger.'
    st.markdown(
        f'<div class="result-card {state}">'
        f'<div class="result-icon {icon_cls}">{icon}</div>'
        f'<div class="result-title">{rtitle}</div>'
        f'<div class="result-copy">{rcopy}</div>'
        f'<div class="rc-time-wrap"><div class="rc-time-label">TIME TAKEN</div>'
        f'<div class="result-time">{fmt(st.session_state.elapsed)}</div></div>'
        f'<div class="result-meta"><span class="rm">Participant #{st.session_state.participant_no}</span>'
        f'<span class="rm">{st.session_state.language}</span>'
        f'<span class="rm">Correct output: {st.session_state.question["answer"]}</span></div>'
        f'</div> <br/>', unsafe_allow_html=True)
    if st.button('Next Participant →',type='primary',use_container_width=True): nxt()