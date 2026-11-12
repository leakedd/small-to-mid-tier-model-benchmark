import json, re, subprocess, sys, tempfile, textwrap, time, requests

BASE = sys.argv[1]; MODEL = sys.argv[2]; TAG = sys.argv[3]
KEY = sys.argv[4] if len(sys.argv) > 4 else ""
H = {"Authorization": "Bearer " + KEY} if KEY else {}
MT = int(__import__("os").environ.get("BMT", "3000"))
F = chr(96) * 3

MCQ = [
 ("gcm-nonce", "cyber", "Un service chiffre avec AES-256-GCM et un nonce aleatoire de 96 bits. Apres 2^32 messages, le generateur de nonce est remplace par un compteur qui redemarre a chaque redemarrage du service. Quelle est la consequence principale de reutiliser un couple cle/nonce ?", ["Seule la confidentialite est perdue, la verification d integrite reste fiable", "Seule la verification d integrite est perdue", "Confidentialite et integrite sont perdues, et la falsification de messages devient possible", "Aucune, GCM reste sur car le nonce fait 96 bits"], "C"),
 ("jwt-alg", "cyber", "Une API verifie des JWT avec une cle publique RSA. Le serveur lit l algorithme dans l en-tete alg et rejette explicitement alg=none. Un attaquant connait la cle publique. Quelle attaque permet de forger un jeton accepte ?", ["Passer alg a none et retirer la signature", "Passer alg a HS256 et signer le jeton avec la cle publique utilisee comme secret HMAC", "Rejouer le jeton d un autre utilisateur", "Modifier le champ kid pour pointer vers un fichier local"], "B"),
 ("ssrf-filter", "cyber", "Un filtre SSRF refuse toute URL dont le texte contient 169.254.169.254. Le serveur est un Linux standard avec resolution DNS. Quels contournements restent possibles ?", ["Aucun, le filtre couvre tous les cas", "Uniquement changer le port", "La forme decimale entiere de l adresse, la forme IPv6 mappee, et un nom DNS qui resout vers cette adresse", "Uniquement HTTPS a la place de HTTP"], "C"),
 ("csp-nonce", "cyber", "Une page envoie Content-Security-Policy: script-src nonce-abc123 strict-dynamic. Un attaquant injecte un script avec src distant et sans attribut nonce. Que fait le navigateur ?", ["Il execute le script car strict-dynamic autorise les scripts distants", "Il bloque le script car il ne porte pas le nonce attendu", "Il execute le script si le domaine est en HTTPS", "Il ignore la CSP car elle contient strict-dynamic"], "B"),
 ("suid-path", "cyber", "Un binaire tourne en root avec le bit SUID et appelle system avec la commande ls sans chemin absolu, en heritant du PATH. Comment obtenir un shell root ?", ["Placer un faux executable ls dans un repertoire present dans PATH", "Modifier /etc/ld.so.preload", "Exploiter une course sur /tmp", "Lancer sudo -l"], "A"),
 ("krbtgt", "cyber", "Quel secret faut-il pour forger un golden ticket Kerberos valide ?", ["Le hash NTLM d un administrateur du domaine", "La cle du compte KRBTGT", "Le mot de passe du controleur de domaine", "Le ticket de service de la cible"], "B"),
 ("tls13-rsa", "cyber", "Pourquoi TLS 1.3 supprime-t-il l echange de cle RSA ?", ["Parce qu il est plus lent que ECDHE", "Parce qu il ne fournit pas de confidentialite persistante", "Parce qu il est vulnerable a l attaque POODLE", "Parce qu il ne supporte pas les certificats"], "B"),
 ("mesi", "cs", "Deux coeurs partagent une ligne de cache, initialement en etat Modified chez le premier. Le second lit la ligne. Que se passe-t-il ?", ["Le premier ecrit la ligne en memoire et les deux passent a Shared", "Le premier reste Modified et le second recoit une copie sans transition", "Le premier passe a Invalid sans ecriture", "Les deux passent a Exclusive"], "A"),
 ("timewait", "cs", "A quoi sert l etat TIME_WAIT en TCP ?", ["A garantir la livraison des donnees applicatives", "A absorber les segments retardataires et a permettre la retransmission du dernier ACK", "A accelerer la reouverture du meme port", "A prevenir la congestion du reseau"], "B"),
 ("ssa-phi", "cs", "A quoi sert une fonction phi dans une representation SSA ?", ["A choisir une valeur selon le predecesseur quand plusieurs chemins convergent", "A implementer une boucle", "A allouer les registres", "A inliner une fonction"], "A"),
 ("release", "cs", "Que garantit une ecriture avec semantique release dans un modele memoire faible ?", ["Que les lectures precedentes ne sont pas deplacees apres elle", "Que les ecritures et lectures precedentes ne sont pas deplacees apres elle", "Que les operations suivantes sont bloquantes", "Qu elle est sequentiellement coherente"], "B"),
 ("btree-range", "cs", "Pourquoi un B+tree est-il prefere a un arbre binaire pour un index disque avec parcours par intervalle ?", ["Parce qu il est toujours plus petit", "Parce que les feuilles sont chainees et la hauteur faible, donc peu d acces disque pour un range scan", "Parce qu il supprime les ecritures", "Parce qu il est plus simple a implementer"], "B"),
 ("tlb-shootdown", "cs", "Un processus partage une page avec un autre processus, puis la demappe. Que doit faire le noyau sur les autres coeurs ?", ["Rien, le materiel invalide seul les entrees", "Invalider les entrees TLB correspondantes sur les autres coeurs", "Copier la page avant demappage", "Vider tout le cache L3"], "B"),
 ("prio-inv", "cs", "Quel mecanisme evite l inversion de priorite ?", ["Le round robin", "L heritage de priorite", "L ordonnanceur a temps partage", "Un nice negatif"], "B"),
]

CODE = [
 ("safe-join", "Ecris en Python une fonction safe_join(base, untrusted) qui renvoie le chemin absolu normalise si et seulement si le resultat reste dans base, sinon None. Elle doit refuser les chemins absolus et toute remontee par .. . Reponds uniquement le code.",
  "\nassert safe_join('/srv/data', 'a/b.txt') == '/srv/data/a/b.txt'\nassert safe_join('/srv/data', '../etc/passwd') is None\nassert safe_join('/srv/data', 'a/../../x') is None\nassert safe_join('/srv/data', '/etc/passwd') is None\nassert safe_join('/srv/data', './ok/../ok/z') == '/srv/data/ok/z'\n"),
 ("token-bucket", "Ecris en Python rate_limit(capacity, rate, times) qui simule un seau a jetons initialement plein. Chaque evenement de la liste times (secondes flottantes, ordre croissant) se voit ajouter (t - precedent) * rate jetons, plafonne a capacity, puis est accepte si au moins 1 jeton est disponible et le consomme. Renvoie la liste des booleens. Reponds uniquement le code.",
  "\nassert rate_limit(2, 1.0, [0.0, 0.0, 0.0]) == [True, True, False]\nassert rate_limit(1, 1.0, [0.0, 0.5, 2.0]) == [True, False, True]\nassert rate_limit(3, 0.0, [0.0, 9.0]) == [True, True]\n"),
 ("topo-sort", "Ecris en Python topo_sort(n, edges) qui renvoie un ordre topologique des sommets 0..n-1, les aretes etant des tuples (u, v) signifiant que u doit preceder v, ou une liste vide si le graphe contient un cycle. Reponds uniquement le code.",
  "\no = topo_sort(3, [(0,1),(1,2)])\nassert o == [0,1,2], o\nassert topo_sort(2, [(0,1),(1,0)]) == []\nassert topo_sort(4, [(0,1),(0,2),(1,3),(2,3)])[3] == 3\n"),
 ("xor-key", "Ecris en Python xor_repeating(data, key) qui applique un XOR repetitif entre un bytes data et un bytes key non vide, et renvoie un bytes. Reponds uniquement le code.",
  "\nassert xor_repeating(b'hello', b'k') == bytes(c ^ ord('k') for c in b'hello')\nassert xor_repeating(xor_repeating(b'secret', b'abc'), b'abc') == b'secret'\nassert xor_repeating(b'', b'x') == b''\n"),
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
    fd, path = tempfile.mkstemp(suffix=".py")
    with __import__("os").fdopen(fd, "w") as f:
        f.write(code + "\n" + tests)
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=60)
    __import__("os").unlink(path)
    return r.returncode == 0, (r.stderr or "").strip()[-150:]

score = 0; rows = []
for qid, dom, prompt, opts, ans in MCQ:
    p = prompt + "\n\n" + "\n".join(chr(65+i) + ". " + o for i, o in enumerate(opts)) + "\n\nTermine par une ligne REPONSE: <lettre>"
    try:
        c, rsn = ask(p)
    except Exception as e:
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    txt = c or ""
    m = re.findall(r"REPONSE\s*:\s*([A-D])", txt.upper())
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
        rows.append({"q": qid, "ok": False, "err": str(e)[:60]}); print(json.dumps(rows[-1]), flush=True); continue
    ok, err = run(extract(c or rsn), tests)
    score += 1 if ok else 0
    rows.append({"q": qid, "dom": "code", "ok": ok, "err": err})
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
print(json.dumps({"tag": TAG, "score": score, "total": len(MCQ) + len(CODE), "rows": rows}), flush=True)
