import json, re, subprocess, sys, tempfile, textwrap, requests, os, shutil

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(os.environ.get("BMT", "2500"))
F = chr(96) * 3

Q = [
 ("ecb", "Blocs de texte clair identiques", "cyber", ["produisent des blocs chiffres differents car le IV change", "produisent des blocs chiffres identiques", "sont rejetes par le mode ECB", "ne sont pas chiffres"], "B"),
 ("kerberoast", "Kerberoasting consiste a", "cyber", ["forcer un mot de passe par pulverisation", "demander un ticket de service pour un SPN puis casser le hash hors ligne", "rejouer un ticket TGT expire", "modifier le PAC d un ticket"], "B"),
 ("ntlm-relay", "La relève NTLM est bloquee principalement par", "cyber", ["le chiffrement SMB3", "la desactivation de LLMNR", "la signature SMB obligatoire", "le filtrage des ports 445 en sortie"], "C"),
 ("cap-net-raw", "Quelle capacite Linux permet d ouvrir une socket brute sans etre root", "cyber", ["CAP_NET_RAW", "CAP_SYS_ADMIN", "CAP_NET_BIND_SERVICE", "CAP_DAC_READ_SEARCH"], "A"),
 ("imdsv2", "Le service de metadonnees IMDSv2 exige", "cyber", ["une adresse IP fixe dans le VPC", "un jeton obtenu par requete PUT avec en-tete", "un certificat client TLS", "une signature SigV4 dans l URL"], "B"),
 ("httponly", "Un cookie marque HttpOnly empeche", "cyber", ["son envoi en HTTPS", "sa lecture par document.cookie en JavaScript", "sa reecriture par le serveur", "son vol par un attaquant reseau"], "B"),
 ("canary", "Un canari de pile detecte en priorite", "cyber", ["l ecrasement du sauvegardeur d adresse par un debordement lineaire", "une fuite de pointeur", "une execution de code dans le tas", "un double free"], "A"),
 ("aslr-bypass", "Quelle primitive faut-il pour contourner ASLR de facon fiable", "cyber", ["un debordement sans fuite", "une fuite d adresse memoire", "un fork repetitif", "un acces en lecture seule"], "B"),
 ("jwt-kid", "Un champ kid de JWT injectable permet typiquement", "cyber", ["de changer le sujet du jeton", "une traversee de chemin vers un fichier de cle controle", "de desactiver la signature automatiquement", "d allonger la duree de vie du jeton"], "B"),
 ("pinning", "Le certificate pinning protege contre", "cyber", ["un CA compromis emettant un faux certificat", "une attaque par rejeu TLS", "un downgrade vers TLS 1.0", "une attaque par force brute sur la cle"], "A"),
 ("padding-oracle", "Une attaque par oracle de bourrage vise", "cyber", ["GCM avec nonce reutilise", "CBC avec remplissage PKCS 7", "CTR sans authentification", "RSA sans bourrage"], "B"),
 ("second-order", "Une injection SQL de second ordre se declenche", "cyber", ["pendant la validation du formulaire", "a la construction de la requete initiale", "quand une entree stockee est reutilisee dans une requete ulterieure", "uniquement sur les bases NoSQL"], "C"),
 ("false-sharing", "Le faux partage entre coeurs designe", "cs", ["deux coeurs modifiant des variables distinctes sur la meme ligne de cache", "un cache L2 partage entre deux sockets", "une invalidation TLB globale", "un defaut de pagination"], "A"),
 ("fast-retransmit", "La retransmission rapide TCP est declenchee par", "cs", ["trois ACK dupliques", "un delai RTO expire", "une fenetre nulle", "un paquet hors sequence unique"], "A"),
 ("heap-build", "Construire un tas binaire a partir de n elements coute", "cs", ["O(n log n)", "O(n)", "O(log n)", "O(n^2)"], "B"),
 ("consistent-hash", "Le hachage coherent limite", "cs", ["le nombre de cles deplacees lors de l ajout d un noeud", "la taille des messages", "le nombre de replicas", "la latence reseau"], "A"),
 ("cow", "Apres un fork, la memoire de l enfant est", "cs", ["copiee immediatement", "partagee en lecture jusqu a la premiere ecriture", "toujours distincte", "placee en swap"], "B"),
 ("twopc", "Le protocole de validation en deux phases bloque si", "cs", ["un participant repond non", "le client se deconnecte", "le coordinateur tombe apres la phase de preparation", "un journal est plein"], "C"),
 ("bloom", "Un filtre de Bloom peut produire", "cs", ["des faux negatifs mais pas de faux positifs", "des faux positifs mais pas de faux negatifs", "les deux", "aucun des deux"], "B"),
 ("raid5-hole", "Le trou d ecriture du RAID 5 survient quand", "cs", ["un disque tombe pendant la reconstruction", "une ecriture de bande est interrompue et la parite reste incoherente", "le cache du controleur est desactive", "une bande depasse la taille du disque"], "B"),
 ("numa", "Sur une machine NUMA, un acces a la memoire d un autre noeud", "cs", ["est plus lent qu un acces local", "est plus rapide grace au cache partage", "est impossible sans migration", "ne passe pas par le cache"], "A"),
 ("spinlock", "Un spinlock est preferable a un mutex quand", "cs", ["la section critique est longue et peut bloquer", "la section critique est tres courte et le coeur est dedie", "le thread doit dormir", "on est sur un seul coeur"], "B"),
 ("pages-64g", "64 Gio d espace d adressage avec des pages de 8 Kio: combien d entrees dans la table de pages de dernier niveau", "num", ["2^20", "2^23", "2^26", "2^32"], "B"),
 ("tcp-segments", "Ouverture puis fermeture normale d une connexion TCP: nombre total de segments echanges", "num", ["5", "6", "7", "8"], "C"),
 ("rsa-2048", "Longueur maximale d un message en clair avec RSA-2048 et PKCS 1 v1.5", "num", ["245 octets", "256 octets", "234 octets", "512 octets"], "A"),
 ("gcm-tag", "Taille standard du tag d authentification AES-GCM", "num", ["8 octets", "12 octets", "16 octets", "32 octets"], "C"),
]

CODE = [
 ("merge-k", "Ecris en Python merge_k(lists) qui fusionne k listes triees croissantes en une seule liste triee, sans utiliser sorted ni heapq. Reponds uniquement le code.",
  "\nassert merge_k([[1,4,5],[1,3,4],[2,6]]) == [1,1,2,3,4,4,5,6]\nassert merge_k([]) == []\nassert merge_k([[]]) == []\nassert merge_k([[1],[2],[3]]) == [1,2,3]\n"),
 ("n-queens", "Ecris en Python n_queens(n) qui renvoie le nombre de solutions distinctes du probleme des n dames. Reponds uniquement le code.",
  "\nassert n_queens(1) == 1\nassert n_queens(4) == 2\nassert n_queens(6) == 4\nassert n_queens(8) == 92\n"),
 ("edit-distance", "Ecris en Python edit_distance(a, b) qui calcule la distance de Levenshtein par programmation dynamique. Reponds uniquement le code.",
  "\nassert edit_distance('kitten', 'sitting') == 3\nassert edit_distance('', 'abc') == 3\nassert edit_distance('abc', 'abc') == 0\nassert edit_distance('flaw', 'lawn') == 2\n"),
 ("sudoku", "Ecris en Python solve_sudoku(board) qui resout une grille 9x9 de listes d entiers, 0 designant une case vide, et renvoie la grille resolue ou None si insoluble. Reponds uniquement le code.",
  "\nb = [[5,3,0,0,7,0,0,0,0],[6,0,0,1,9,5,0,0,0],[0,9,8,0,0,0,0,6,0],[8,0,0,0,6,0,0,0,3],[4,0,0,8,0,3,0,0,1],[7,0,0,0,2,0,0,0,6],[0,6,0,0,0,0,2,8,0],[0,0,0,4,1,9,0,0,5],[0,0,0,0,8,0,0,7,9]]\ns = solve_sudoku(b)\nassert s is not None\nassert s[0] == [5,3,4,6,7,8,9,1,2], s[0]\nassert solve_sudoku([[0]*9 for _ in range(9)])[0][0] in range(1,10)\n"),
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
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=d)
    except Exception as e:
        return False, ('timeout: ' + str(e))[:160]
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode == 0, (r.stderr or '').strip()[-200:]

score = 0; rows = []
for qid, prompt, dom, opts, ans in Q:
    p = prompt + "\n\n" + "\n".join(chr(65+i) + ". " + o for i, o in enumerate(opts)) + "\n\nTermine par une ligne REPONSE: <lettre>"
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "dom": dom, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    m = re.findall(r"REPONSE\s*:\s*([A-D])", (c or "").upper())
    got = m[-1] if m else "-"
    ok = got == ans
    score += 1 if ok else 0
    rows.append({"q": qid, "dom": dom, "ok": ok, "got": got, "exp": ans})
    print(json.dumps(rows[-1]), flush=True)
for qid, prompt, tests in CODE:
    p = prompt + "\n\nReponds uniquement avec un bloc ```python```."
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "dom": "code", "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    ok, err = run(extract(c or rsn), tests)
    score += 1 if ok else 0
    rows.append({"q": qid, "dom": "code", "ok": ok, "err": err})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
print(json.dumps({"tag": TAG, "score": score, "total": len(Q) + len(CODE), "rows": rows}), flush=True)
