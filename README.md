# Benchmarks de LLM locaux sur Radeon RX 9070 XT

Mesures comparatives de modèles 9B à 35B exécutés entièrement en local sur une
carte 16 Go, avec PolyStrata, llama.cpp et le moteur ternaire Strata.

L'objectif est de répondre à une question concrète : quel modèle local choisir
pour du travail de sécurité et d'informatique, et à quel prix en vitesse et en
contexte.

## Matériel et logiciels

| Élément | Valeur |
|---|---|
| GPU | Radeon RX 9070 XT, gfx1201 (RDNA4), 16 Go de VRAM |
| CPU / RAM | 6 cœurs / 12 threads, 30 Go |
| Disque | NVMe PCIe Gen5 |
| OS | Ubuntu, ROCm |
| Moteurs | strata 0.1.56, engine-poly 0.1.45, llama.cpp build Clover HIP (master nov. 2026) |

## Modèles évalués

| Modèle | Format | Taille | Contexte |
|---|---|---:|---:|
| Cybertiel Coder 35B-A3B | GGUF UD-Q4_K_XL (MoE) | 22,4 Go | 262 144 |
| Gyro-S (Qwen3.8 Flash-Next) | TQ1_0 abliterated (MoE) | 55 Go | 262 144 |
| Ornith 1.5 35B-A3B | GGUF CRACK Q4_K_M (MoE) | 20,2 Go | 262 144 |
| Bonsai 2 27B | GGUF Q2_0 ternaire (dense) | 7,6 Go | 65 536 testés |
| Swift 1.5 27B | GGUF IQ3_S GSQ-RCO (dense) | 11,8 Go | 32 768 testés |
| Qwen3.5-9B | GGUF Q3_K_M (dense) | 4,7 Go | 32 768 testés |
| DeepSeek-V4-Pro-9B heretic | GGUF IQ4_XS (dense, base Qwen3.5-9B) | 5,2 Go | 65 536 |
| Bonsai 2 9B | GGUF Q2_0 ternaire | 2,6 Go | 131 072 |

## Protocole

Cinq batteries, toutes scorées automatiquement, sans jugement humain :

1. **Cyber et informatique (18)** — 7 questions de sécurité, 7 d'informatique
   système, 4 implémentations. Réponses à choix unique vérifiées, code exécuté
   contre des assertions.
2. **Calcul et implémentation (11)** — goodput TCP, LRU, table de pages, Amdahl,
   RSA à exposant 3, SQL de second ordre, TOCTOU, puis segment tree, Rabin-Karp,
   Dijkstra et chaîne de matrices.
3. **Cryptographie et algorithmique (4)** — ChaCha20 contre le vecteur RFC 8439,
   HKDF contre RFC 5869, moteur regex avec point et étoile, table de suffixes.
4. **Grosse batterie (30)** — 12 cyber, 10 informatique, 4 numériques, 4
   implémentations (merge-k, n-queens, distance d'édition, sudoku).
5. **Réparation (2)** — un code volontairement cassé est fourni avec ses tests
   en échec ; l'erreur est renvoyée au modèle jusqu'à trois tours.

Le budget de sortie est fixé entre 2 500 et 5 000 tokens selon la batterie. Ce
point est décisif : les modèles de raisonnement consomment le budget en réflexion
et, avec 600 tokens, la réponse n'est jamais émise. Les premières mesures, faites
à 600 tokens, sous-estimaient fortement Bonsai (10/16 au lieu de 14/16).

Le code produit est exécuté dans un lanceur restreint : hook d'audit Python
bloquant les sockets, les sous-processus, les écritures hors bac et les lectures
de fichiers système, complété par des limites CPU, mémoire et taille de fichier.

## Résultats

### Classement général (67 épreuves + réparation)

| Modèle | 37 épreuves | Grosse batterie /30 | Total /67 | Réparation | Décodage |
|---|---:|---:|---:|---:|---:|
| Swift 1.5 27B | **34** | **30** | **64** | 1/2 | 36 tok/s |
| Gyro-S | 33 | **30** | 63 | **2/2** | 74 tok/s |
| Bonsai 27B | 33 | 29 | 62 | 1/2 | 46 tok/s |
| Cybertiel 35B-A3B | 32 | 28 | 60 | 1/2 | 114 tok/s |
| Qwen3.5-9B Q3 | — | 29 | — | — | 120 tok/s |
| DeepSeek-V4-Pro-9B | — | 24 | — | — | 150 tok/s |

En ajoutant la réparation sur 2 points, Swift et Gyro sont à égalité à 65/69.
Gyro reste devant en usage réel : il est le seul à savoir corriger son propre
code, il tient 262 144 de contexte et tourne deux fois plus vite.

### Détail par domaine (batterie 37)

| Modèle | Cyber /7 | Informatique /7 | Code /8 | Calcul /11 | Crypto /4 |
|---|---:|---:|---:|---:|---:|
| Cybertiel | 6 | 6 | **8** | 10 | 2 |
| Swift 1.5 | **7** | **7** | 7 | **11** | 2 |
| Bonsai 27B | **7** | **7** | 7 | **11** | 1 |
| Gyro-S | **7** | **7** | 7 | 10 | 2 |

### Ce que la batterie ne discrimine pas

Sur 70 questions de connaissance, **59 sont réussies par tous les modèles**. Tout
l'écart tient dans 11 items : injection SQL dans un ORDER BY, TOCTOU, sémantique
de nonce CSP, confusion d'algorithme JWT, contournement de filtre SSRF, golden
ticket KRBTGT, transition MESI, parsing CSV, top-k avec ex æquo, late binding
Python et le problème batte-et-balle. Les quatre modèles 27B descendent de la
même base Qwen : ils partagent les mêmes points forts et les mêmes angles morts,
ce qui rend les questions de cours peu informatives pour les classer.

### Les murs techniques

- **ChaCha20 depuis la RFC : aucun modèle ne le passe en one-shot**, sur quatre
  tentatives indépendantes. Seul Gyro le répare quand on lui rend l'erreur.
- **Moteur regex complet** : échec unanime en one-shot, corrigé par tous en deux
  tours au maximum.
- **Rabin-Karp avec chevauchements** : seuls Swift et Bonsai passent en one-shot ;
  Gyro et Cybertiel échouent là mais réussissent le reste du bloc.

### Vitesse et empreinte

| Modèle | Décodage | Contexte utile | VRAM |
|---|---:|---:|---:|
| Cybertiel 35B-A3B | 109-120 tok/s | 262 144 | ~14,7 Go |
| Gyro-S | 73-77 tok/s | 262 144 | ~15,4 Go |
| Bonsai 9B | 114 tok/s | 131 072 | ~3 Go |
| Swift 27B | 36 tok/s | 32 768 | ~12,5 Go |
| Bonsai 27B | 46 tok/s | 65 536 | ~8,5 Go |
| DeepSeek 9B | ~150 tok/s | 65 536 | ~5,5 Go |

Le décodage des modèles denses est limité par la bande passante mémoire : le
ternaire Q2_0 lit 7,6 Go par token, le IQ3_S de Swift 11,8 Go. Sur cette carte,
le plafond observé pour Bonsai 27B est de 46,5 tok/s, et le décodage spéculatif
par n-grammes n'apporte rien (46,7 tok/s mesurés).

## Enseignements

1. Le format de sortie compte autant que le modèle. Trois échecs sur la grosse
   batterie viennent d'une ligne de réponse absente, pas d'une erreur de fond.
2. Les 9B tiennent la connaissance mais s'effondrent sur le code : DeepSeek 9B
   rate les quatre implémentations, sa base Qwen en réussit trois.
3. Un fine-tune peut régresser : DeepSeek-V4-Pro-9B perd cinq points face à son
   modèle de base Qwen3.5-9B sur la même batterie.
4. La boucle de réparation est le meilleur discriminant observé. Elle sépare
   Gyro (2/2, un tour) de Swift, Bonsai et Cybertiel (1/2, deux tours ou échec).

## Méthode de reproduction

Chaque batterie est un script Python autonome qui prend quatre arguments : URL
de base compatible OpenAI, nom du modèle, étiquette de sortie et clé API. Les
épreuves de code extraient le bloc Python de la réponse et l'exécutent dans un
lanceur restreint, puis comparent le résultat aux assertions attendues.

Pour les QCM, la réponse est lue sur une ligne finale du type REPONSE: <lettre>,
avec repli sur la dernière lettre isolée du texte. Ce détail a son importance :
les modèles qui raisonnent beaucoup épuisent le budget avant d'écrire cette
ligne, ce qui produit des échecs de format et non de connaissance.

## Limites

- Échantillons de 30 à 70 items : un écart de 1 à 2 points n'est pas significatif.
- Les mesures de vitesse dépendent du build ROCm et du moment ; elles varient de
  10 à 15 % d'une session à l'autre.
- Les quatre modèles 27B partagent une base Qwen, donc la connaissance mesurée
  est largement commune.
- Aucun test agentique multi-étapes avec outils n'est inclus à ce stade.
- Les scripts et les sorties brutes peuvent être ajoutés au dépôt sur demande.

## Licence

MIT pour les textes et scripts.
