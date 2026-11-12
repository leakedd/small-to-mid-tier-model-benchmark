import json, re, subprocess, sys, tempfile, textwrap, requests, os, shutil

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(os.environ.get("BMT", "3500"))
F = chr(96) * 3

MCQ = [
 ("tcp-goodput", "Une connexion TCP sans perte a un MSS de 1460 octets, un RTT de 40 ms et une fenetre de reception de 65535 octets qui est le facteur limitant. Quel debit utile maximal en Mbit/s ? Arrondis a une decimale.", ["5.3", "13.1", "26.2", "131.0"], "B"),
 ("lru-hits", "Cache LRU de 3 cases, acces aux blocs dans cet ordre: 1 2 3 4 1 2 5 1 2 3 4 5. Combien de succes (hits) ?", ["0", "2", "4", "6"], "B"),
 ("pte-top", "Adressage virtuel 48 bits, pages de 4096 octets, table sur 4 niveaux de 9 bits d index. Combien d entrees contient la table de premier niveau ?", ["256", "512", "1024", "2048"], "B"),
 ("amdahl", "Une tache est parallelisable a 80 pour cent et le reste est sequentiel. Quel acceleration maximale avec 16 coeurs ? Arrondis a une decimale.", ["3.2", "4.0", "5.0", "16.0"], "B"),
 ("rsa-cube", "RSA avec e=3, module n=3233 et chiffre c=110592. Le message est plus petit que n et il n y a pas de bourrage. Quel est le message clair m ?", ["12", "24", "48", "96"], "C"),
 ("sqli-order", "Code Python: q = 'SELECT * FROM t WHERE id = %s ORDER BY ' + colonne  puis cursor.execute(q, (uid,)); la valeur colonne vient du parametre ?sort= GET, validee contre une liste blanche. Quelle faille subsiste si la validation est retiree ?", ["Injection SQL possible dans ORDER BY car un identifiant ne peut pas etre un parametre lie", "Aucune, le WHERE reste parametre", "Injection uniquement dans le WHERE", "Fuite de donnees par erreur HTTP"], "A"),
 ("toctou", "Code systeme: if not os.path.exists(p): shutil.copy(src, p). Quel probleme de securite principal ?", ["Aucun, os.path.exists est fiable", "Fenetre de course entre le test et l ecriture, permettant d ecraser ou de suivre un lien", "Fuite de descripteur", "Injection de commande"], "B"),
]

CODE = [
 ("range-sum", "Ecris en Python range_sum_ops(n, arr, ops) qui applique une sequence d operations sur un tableau de n entiers et renvoie la liste des resultats de somme. Operations: ('add', i, v) ajoute v a arr[i]; ('sum', l, r) renvoie la somme de arr[l..r] inclus. Complexite logarithmique attendue par operation. Reponds uniquement le code.",
  "\nassert range_sum_ops(5, [1,2,3,4,5], [('sum',0,4), ('add',2,10), ('sum',1,3)]) == [15, 19]\nassert range_sum_ops(1, [7], [('add',0,3), ('sum',0,0)]) == [10]\nassert range_sum_ops(4, [0,0,0,0], [('add',1,5),('sum',0,0),('sum',1,1),('sum',0,3)]) == [0,5,5]\n"),
 ("rabin-karp", "Ecris en Python count_occurrences(text, pat) qui compte les occurrences de pat dans text, chevauchements compris, en utilisant un algorithme de hachage glissant. Renvoie un entier. Reponds uniquement le code.",
  "\nassert count_occurrences('aaaa', 'aa') == 3\nassert count_occurrences('abcabcabd', 'abc') == 2\nassert count_occurrences('abc', 'z') == 0\nassert count_occurrences('', 'a') == 0\nassert count_occurrences('abababa', 'aba') == 3\n"),
 ("dijkstra", "Ecris en Python shortest_paths(n, edges, src) qui renvoie la liste des distances minimales depuis src vers chaque sommet avec edges = liste de tuples (u, v, w) orientes, poids positifs, et -1 pour un sommet inatteignable. Reponds uniquement le code.",
  "\nd = shortest_paths(4, [(0,1,1),(0,2,4),(1,2,2),(2,3,1)], 0)\nassert d == [0,1,3,4], d\nassert shortest_paths(2, [(0,1,5)], 1) == [-1,0]\nassert shortest_paths(3, [(0,1,2),(1,2,2)], 0) == [0,2,4]\n"),
 ("matrix-chain", "Ecris en Python matrix_chain(dims) qui renvoie le nombre minimal de multiplications scalaires pour multiplier une chaine de matrices dont les dimensions des matrices i sont dims[i] x dims[i+1]. Reponds uniquement le code.",
  "\nassert matrix_chain([10,30,5,60]) == 4500\nassert matrix_chain([1,2,3,4]) == 18\nassert matrix_chain([5,10]) == 0\n"),
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
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=d)
    except Exception as e:
        return False, ('timeout: ' + str(e))[:160]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode == 0, (r.stderr or '').strip()[-160:]

score = 0; rows = []
for qid, prompt, opts, ans in MCQ:
    p = prompt + "\n\n" + "\n".join(chr(65+i) + ". " + o for i, o in enumerate(opts)) + "\n\nTermine par une ligne REPONSE: <lettre>"
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    m = re.findall(r"REPONSE\s*:\s*([A-D])", (c or "").upper())
    got = m[-1] if m else "-"
    ok = got == ans
    score += 1 if ok else 0
    rows.append({"q": qid, "dom": "calc", "ok": ok, "got": got, "exp": ans})
    print(json.dumps(rows[-1]), flush=True)
for qid, prompt, tests in CODE:
    p = prompt + "\n\nReponds uniquement avec un bloc ```python```."
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    ok, err = run(extract(c or rsn), tests)
    score += 1 if ok else 0
    rows.append({"q": qid, "dom": "code", "ok": ok, "err": err})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
print(json.dumps({"tag": TAG, "score": score, "total": len(MCQ) + len(CODE), "rows": rows}), flush=True)
