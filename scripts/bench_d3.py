import json, re, subprocess, sys, tempfile, textwrap, requests, os, shutil

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(os.environ.get("BMT", "4000"))
F = chr(96) * 3

CODE = [
 ("chacha20", "Ecris en Python chacha20_block(key, counter, nonce) qui calcule le bloc de 64 octets du keystream ChaCha20 (RFC 8439) avec key de 32 octets, counter entier et nonce de 12 octets, et renvoie un bytes. Sans librairie crypto. Reponds uniquement le code.",
  "\nkey = bytes(range(32))\nnonce = bytes.fromhex('000000090000004a00000000')\nks = chacha20_block(key, 1, nonce)\nassert len(ks) == 64\nassert ks[:16].hex() == '10f1e7e4d13b5915500fdd1fa32071c4', ks[:16].hex()\n"),
 ("hkdf", "Ecris en Python hkdf_sha256(ikm, salt, info, length) qui implemente HKDF avec SHA-256 (RFC 5869, extract puis expand) et renvoie length octets. Seuls hashlib et hmac sont autorises. Reponds uniquement le code.",
  "\nokm = hkdf_sha256(bytes([11])*22, bytes.fromhex('000102030405060708090a0b0c'), bytes.fromhex('f0f1f2f3f4f5f6f7f8f9'), 42)\nassert okm.hex() == '3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865', okm.hex()\n"),
 ("regex", "Ecris en Python regex_match(pattern, text) qui dit si le motif correspond au texte entier, en supportant uniquement les caracteres litteraux, le point qui matche un caractere quelconque, et l etoile de Kleene appliquee a l element precedent. Le motif peut etre vide et le texte aussi. Reponds uniquement le code.",
  "\nassert regex_match('aa', 'a') is False\nassert regex_match('aa', 'a*') is True\nassert regex_match('', 'a*') is True\nassert regex_match('ab', '.*') is True\nassert regex_match('aab', 'c*a*b') is True\nassert regex_match('mississippi', 'mis*is*p*.') is False\nassert regex_match('abc', 'a.c') is True\n"),
 ("suffix-array", "Ecris en Python suffix_array(s) qui renvoie la liste des indices de depart des suffixes de s tries par ordre lexicographique. Reponds uniquement le code.",
  "\nassert suffix_array('banana') == [5,3,1,0,4,2]\nassert suffix_array('a') == [0]\nassert suffix_array('') == []\nassert suffix_array('aaaa') == [3,2,1,0]\nassert suffix_array('mississippi') == [10,7,4,1,0,9,8,6,3,5,2]\n"),
]

def ask(p):
    r = requests.post(BASE + "/v1/chat/completions", headers=H, json={"model": MODEL,
        "messages": [{"role": "user", "content": p}], "max_tokens": MT, "temperature": 0.0}, timeout=1200)
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
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=d)
    except Exception as e:
        return False, ('timeout: ' + str(e))[:160]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode == 0, (r.stderr or '').strip()[-200:]

score = 0; rows = []
for qid, prompt, tests in CODE:
    p = prompt + "\n\nReponds uniquement avec un bloc ```python```."
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    ok, err = run(extract(c or rsn), tests)
    score += 1 if ok else 0
    rows.append({"q": qid, "ok": ok, "err": err})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
print(json.dumps({"tag": TAG, "score": score, "total": len(CODE), "rows": rows}), flush=True)
