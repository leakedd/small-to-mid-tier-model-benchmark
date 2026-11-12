import json, re, subprocess, sys, tempfile, textwrap, requests, os, shutil

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(os.environ.get("BMT", "3500"))
F = chr(96) * 3

T = [
 ("path-within", "Ecris en Python path_is_within(base, target) qui renvoie True si le chemin absolu target est strictement a l interieur de base apres normalisation, en refusant les remontees. Attention au piege du prefixe (base /srv/data ne doit pas accepter /srv/data2). Reponds uniquement le code.",
  "\nassert path_is_within('/srv/data', '/srv/data/a') is True\nassert path_is_within('/srv/data', '/srv/data2/x') is False\nassert path_is_within('/srv/data', '/srv/data/../etc') is False\nassert path_is_within('/srv/data', '/srv/data/a/../../data/b') is True\nassert path_is_within('/srv/data', '/etc/passwd') is False\n"),
 ("jwt-verify", "Ecris en Python jwt_verify(token, secret) qui verifie un JWT HS256 sans librairie externe: header et payload en base64url sans padding, signature HMAC-SHA256 comparee en temps constant, refus si alg different de HS256, refus si la signature est invalide. Renvoie le dict du payload si valide, sinon None. Reponds uniquement le code.",
  "\nimport base64, hmac, hashlib, json\ndef mk(h, p, k):\n    e = lambda d: base64.urlsafe_b64encode(json.dumps(d, separators=(',',':')).encode()).rstrip(b'=').decode()\n    a, b = e(h), e(p)\n    s = hmac.new(k.encode(), (a+'.'+b).encode(), hashlib.sha256).digest()\n    return a + '.' + b + '.' + base64.urlsafe_b64encode(s).rstrip(b'=').decode()\nok = mk({'alg':'HS256','typ':'JWT'}, {'sub':'x'}, 'k')\nassert jwt_verify(ok, 'k') == {'sub': 'x'}\nassert jwt_verify(ok, 'wrong') is None\nassert jwt_verify(mk({'alg':'none'}, {'sub':'x'}, 'k'), 'k') is None\nassert jwt_verify(mk({'alg':'HS512','typ':'JWT'}, {'sub':'x'}, 'k'), 'k') is None\n"),
 ("first-true", "Ecris en Python binary_search_first_true(pred, lo, hi) qui renvoie le plus petit indice i dans [lo, hi] tel que pred(i) est vrai, en supposant pred monotone croissante, et -1 si aucun. Complexite logarithmique. Reponds uniquement le code.",
  "\nassert binary_search_first_true(lambda i: i >= 37, 0, 100) == 37\nassert binary_search_first_true(lambda i: False, 0, 50) == -1\nassert binary_search_first_true(lambda i: i >= 0, 0, 10) == 0\nassert binary_search_first_true(lambda i: i >= 10, 0, 10) == 10\n"),
 ("cycle-detect", "Ecris en Python has_cycle(n, edges) qui detecte la presence d un cycle dans un graphe oriente a n sommets, edges etant des tuples (u, v). Reponds uniquement le code.",
  "\nassert has_cycle(3, [(0,1),(1,2)]) is False\nassert has_cycle(3, [(0,1),(1,2),(2,0)]) is True\nassert has_cycle(1, [(0,0)]) is True\nassert has_cycle(4, [(0,1),(2,3),(3,2)]) is True\n"),
]

def ask(p):
    r = requests.post(BASE + "/v1/chat/completions", headers=H, json={"model": MODEL,
        "messages": [{"role": "user", "content": p}], "max_tokens": MT, "temperature": 0.0}, timeout=900)
    j = r.json(); m = (j.get("choices") or [{}])[0].get("message") or {}
    return (m.get("content") or ""), (m.get("reasoning_content") or "")

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
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90, cwd=d)
    except Exception as e:
        return False, ('timeout: ' + str(e))[:160]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode == 0, (r.stderr or '').strip()[-160:]

score = 0; rows = []
for qid, prompt, tests in T:
    p = prompt + "\n\nReponds uniquement avec un bloc ```python```."
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    ok, err = run(extract(c or rsn), tests)
    score += 1 if ok else 0
    rows.append({"q": qid, "ok": ok, "err": err})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
print(json.dumps({"tag": TAG, "score": score, "total": len(T), "rows": rows}), flush=True)
