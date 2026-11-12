import json, re, subprocess, sys, tempfile, textwrap, requests, os, shutil

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(os.environ.get("BMT", "3000"))
F = chr(96) * 3
ROUNDS = 3

BUGGY_CHACHA = '''import struct
def rotl(v, c):
    return ((v << c) | (v >> (32 - c))) & 0xffffffff
def qr(s, a, b, c, d):
    s[a] = (s[a] + s[b]) & 0xffffffff; s[d] ^= s[a]; s[d] = rotl(s[d], 16)
    s[c] = (s[c] + s[d]) & 0xffffffff; s[b] ^= s[c]; s[b] = rotl(s[b], 12)
    s[a] = (s[a] + s[b]) & 0xffffffff; s[d] ^= s[a]; s[d] = rotl(s[d], 8)
    s[c] = (s[c] + s[d]) & 0xffffffff; s[b] ^= s[c]; s[b] = rotl(s[b], 7)
def chacha20_block(key, counter, nonce):
    st = list(struct.unpack('<4I', b'expand 32-byte k')) + list(struct.unpack('<8I', key))
    st += [counter] + list(struct.unpack('<3I', nonce))
    w = st[:]
    for _ in range(4):
        qr(w, 0, 4, 8, 12); qr(w, 1, 5, 9, 13); qr(w, 2, 6, 10, 14); qr(w, 3, 7, 11, 15)
        qr(w, 0, 5, 10, 15); qr(w, 1, 6, 11, 12); qr(w, 2, 7, 8, 13); qr(w, 3, 4, 9, 14)
    out = [(w[i] + st[i]) & 0xffffffff for i in range(16)]
    return struct.pack('<16I', *out)
'''

BUGGY_REGEX = '''def regex_match(pattern, text):
    i = 0
    j = 0
    while i < len(pattern):
        if i + 1 < len(pattern) and pattern[i+1] == '*':
            while j < len(text) and (pattern[i] == '.' or text[j] == pattern[i]):
                j += 1
            i += 2
        else:
            if j >= len(text) or (pattern[i] != '.' and text[j] != pattern[i]):
                return False
            i += 1; j += 1
    return j == len(text)
'''

TASKS = [
 ("chacha20-fix", BUGGY_CHACHA,
  "Cette implementation de ChaCha20 ne passe pas les tests. Corrige-la. Reponds uniquement le code complet.",
  "\nkey = bytes(range(32))\nnonce = bytes.fromhex('000000090000004a00000000')\nks = chacha20_block(key, 1, nonce)\nassert len(ks) == 64\nassert ks[:16].hex() == '10f1e7e4d13b5915500fdd1fa32071c4', ks[:16].hex()\n"),
 ("regex-fix", BUGGY_REGEX,
  "Cette implementation de correspondance de motif avec point et etoile ne passe pas les tests. Corrige-la. Reponds uniquement le code complet.",
  "\nassert regex_match('aa', 'a') is False\nassert regex_match('aa', 'a*') is True\nassert regex_match('', 'a*') is True\nassert regex_match('ab', '.*') is True\nassert regex_match('aab', 'c*a*b') is True\nassert regex_match('mississippi', 'mis*is*p*.') is False\nassert regex_match('abc', 'a.c') is True\n"),
]

def ask(msgs):
    r = requests.post(BASE + "/v1/chat/completions", headers=H, json={"model": MODEL,
        "messages": msgs, "max_tokens": MT, "temperature": 0.0}, timeout=900)
    j = r.json(); m = (j.get("choices") or [{}])[0].get("message") or {}
    return (m.get("content") or "") + " " + (m.get("reasoning_content") or "")

def extract(t):
    b = re.findall(F + r"(?:python)?\s*(.*?)" + F, t, re.S)
    return textwrap.dedent(b[-1] if b else t).strip(chr(10))

def run(code, tests):
    d = tempfile.mkdtemp()
    path = os.path.join(d, 't.py')
    with open(path, 'w') as f:
        f.write(code + chr(10) + tests)
    cmd = [sys.executable, '-I', '-B', '/home/user/AI/sbx.py', path, d]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=d)
    except Exception as e:
        return False, ('timeout: ' + str(e))[:200]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode == 0, (r.stderr or '').strip()[-300:]

rows = []
for qid, buggy, prompt, tests in TASKS:
    msgs = [{"role": "user", "content": prompt + chr(10) + chr(10) + chr(96)*3 + 'python' + chr(10) + buggy + chr(96)*3 + chr(10)*2 + 'Tests a passer:' + chr(10) + chr(96)*3 + 'python' + chr(10) + tests.strip() + chr(10) + chr(96)*3}]
    code = None; ok = False; rounds = 0; err = ''
    for k in range(1, ROUNDS + 1):
        rounds = k
        try:
            out = ask(msgs)
        except Exception as e:
            err = str(e)[:80]; break
        code = extract(out)
        ok, err = run(code, tests)
        if ok:
            break
        msgs = msgs + [{"role": "assistant", "content": out[:4000]},
            {"role": "user", "content": "Le test echoue encore: " + err + " Corrige. Reponds uniquement le code complet dans un bloc python."}]
    rows.append({"q": qid, "ok": ok, "rounds": rounds, "err": ('' if ok else err[:200])})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
score = sum(1 for r in rows if r['ok'])
mean = round(sum(r['rounds'] for r in rows if r['ok']) / max(1, score), 2)
print(json.dumps({"tag": TAG, "fixed": score, "total": len(TASKS), "mean_rounds": mean, "rows": rows}), flush=True)
