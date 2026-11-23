# Projet Dominos avec IA — Variante 10|10 déterministe

Projet d'Intelligence Artificielle (binôme). Variante du jeu de Dominos transformée en jeu **déterministe à information parfaite** :

- **66 dominos** (de `0|0` à `10|10`), distribués 33 par joueur dès le départ.
- Pas de pioche cachée → **information parfaite**.
- Distribution initiale fixée par configuration → **déterministe**.

## Règles de la variante

- Le joueur qui possède le **plus fort double** commence et **doit le poser** en premier coup (10|10 par construction).
- Plateau **linéaire** : on pose à gauche ou à droite, sans bifurcation aux doubles.
- Si un joueur ne peut pas jouer, il **passe son tour**.
- **Blocage** (les deux joueurs passent) → vainqueur = celui qui a le **moins de pips** restants. Égalité possible.
- **Victoire** : le premier joueur à vider sa main gagne.

## Niveaux d'IA

| ID | Nom | Stratégie |
|---|---|---|
| `IA1_aleatoire` | Aléatoire | Coup légal pris au hasard (baseline) |
| `IA2_pip` | Pip | Minimax α-β profondeur **6**, évaluation = `f_pip` |
| `IA3_blocage` | Blocage | Minimax α-β profondeur **6**, évaluation = `f_blocage` |
| `IA4_protect` | Protection | Minimax α-β profondeur **6**, évaluation = `f_protect` |
| `IA5_mixte` | Mixte | Minimax α-β profondeur **4**, évaluation = `f_mixte` (somme des 3) |

## Fonctions d'évaluation

| ID | Définition |
|---|---|
| `f_pip` | `pips(adversaire) − pips(MAX)` |
| `f_blocage` | 3 cas hiérarchisés : blocage total → `total_pips_adv` ; partiel → `total_pips_adv − 1` ; aucun → somme pips dominos isolés |
| `f_protect` | Miroir négatif de `f_blocage` appliqué à NOTRE main |
| `f_mixte` | `f_pip + f_blocage + f_protect` |

## Installation

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Exécution

### Jouer Humain vs IA (en ligne de commande)

```bash
python -m scripts.jouer --niveau IA2_pip
python -m scripts.jouer --niveau IA5_mixte --joueur-commence
python -m scripts.jouer --niveau IA3_blocage --config-idx 5 --variante v1
```

### Interface graphique (Tkinter)

Visualiser une partie en direct :

```bash
python -m scripts.interface_graphique
```

Au démarrage, choix du mode :
- **IA vs IA** : regarder 2 IA s'affronter (auto-play, vitesse réglable, pas-à-pas)
- **Humain vs IA** : jouer soi-même en cliquant sur les dominos

Fonctionnalités :
- Plateau scrollable avec extrémités gauche/droite mises en évidence
- Mains des joueurs (cachée pour l'adversaire en mode Humain)
- Dominos jouables surlignés en jaune
- Boutons : coup suivant / auto-play / pause / retour menu
- Slider de vitesse (100 ms à 2 s par coup)
- Historique des coups en temps réel

### Lancer le tournoi complet

```bash
python -m scripts.lancer_tournoi
```

Tournoi : 5 IA × 10 couples × 60 parties = **600 parties** au total.
- **10 configurations** stratifiées (2 par type : ouverte / fermée / équilibrée / avantage_α / avantage_β)
- **3 variantes** par configuration
- **2 attributions** (alternance des mains entre les 2 IA)

Sorties dans `resultats/` :
- `tournoi.csv` : détail de toutes les parties
- `tournoi.synthese.json` : statistiques par couple
- `configurations.json` : les configurations utilisées (reproductibles via le seed)

### Générer les graphiques

```bash
python -m scripts.tracer_graphes --csv resultats/tournoi.csv
```

Produit dans `resultats/` :
- `heatmap_victoires.png` : matrice taux de victoire de A contre B
- `classement_global.png` : classement des 5 IA avec intervalles de confiance
- `triangle_non_transitif.png` : relations rock-paper-scissors entre les 3 stratégies pures
- `significativite_statistique.png` : matrice de domination avec hachures pour le bruit
- `performance_par_type_config.png` : taux de victoire par type de configuration
- `avantage_premier_joueur.png` : taux de victoire du starter par couple
- `duree_moyenne.png` : temps moyen par partie

### Benchmarks supplémentaires

```bash
python -m scripts.benchmark_alpha_beta     # Impact de α-β + ordering
python -m scripts.benchmark_profondeur     # Nœuds explorés vs profondeur (2 à 6)
```

Produit `resultats/impact_alpha_beta.png` et `resultats/noeuds_vs_profondeur.png`.

### Lancer les tests

```bash
pytest tests/
```

→ 35 tests, tous verts en ~10 s.

## Structure du projet

```
.
├── src/
│   ├── domino.py          # Classe Domino (immuable, __slots__)
│   ├── plateau.py         # Plateau linéaire avec extrémités
│   ├── joueur.py          # Joueur abstrait + JoueurHumain (CLI)
│   ├── partie.py          # Moteur de jeu (clone léger pour Minimax)
│   ├── ia/
│   │   ├── evaluation.py  # f_pip, f_blocage, f_protect, f_mixte
│   │   ├── ia_aleatoire.py
│   │   ├── ia_minimax.py  # Minimax + α-β + move ordering
│   │   └── factory.py     # Construction des 5 niveaux d'IA
│   └── tournoi/
│       ├── configurations.py  # Génération des 10 configs stratifiées
│       └── tournoi.py         # Runner et synthèse
├── scripts/
│   ├── jouer.py                  # Humain vs IA (CLI)
│   ├── interface_graphique.py    # GUI Tkinter (IA vs IA / Humain vs IA)
│   ├── lancer_tournoi.py         # Tournoi complet 600 parties
│   ├── tracer_graphes.py         # Génère les 7 graphiques principaux
│   ├── benchmark_alpha_beta.py   # Bench α-β + ordering
│   ├── benchmark_profondeur.py   # Bench nœuds vs profondeur
│   └── debug_position.py         # Debug du choix de coup d'une IA
├── tests/                 # 35 tests unitaires (pytest)
├── resultats/             # CSV, JSON, 9 PNG du tournoi
├── rapport/               # Rapport LaTeX + PDF
├── requirements.txt
└── README.md
```

## Reproductibilité

Toutes les composantes aléatoires sont contrôlées par un **seed** :
- Génération des configurations : `--seed-configs 42` (par défaut)
- Tournoi (seeds des IA aléatoires) : `--seed-tournoi 1000`
- Les configurations générées sont sauvegardées en JSON et rechargées au lancement suivant.
