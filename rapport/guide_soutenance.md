# 🎓 Guide de soutenance — Projet Dominos IA

**BENMEZIANE Samy & CHEGGOUR Racha** · L3 Informatique · Mai 2026

---

## ⏱️ Plan de la soutenance (durée estimée 15-20 min)

| Temps | Étape | Contenu |
|---|---|---|
| 1 min | Intro | Présenter le jeu et le choix de la variante |
| 2 min | Architecture | Montrer la structure du projet en VS Code |
| 5 min | **DÉMO 1** | Lancer la GUI : IA vs IA puis Humain vs IA |
| 2 min | **DÉMO 2** | Lancer pytest (35 tests verts) |
| 3 min | **DÉMO 3** | Lancer le benchmark α-β |
| 3 min | Résultats | Montrer 2-3 graphiques du tournoi |
| 1 min | Conclusion | Limites + perspectives |
| reste | Q&A | Répondre aux questions |

---

## 📜 Script de démo

### Étape 1 — Présentation orale (1 min)
> *"Notre projet implémente une variante déterministe du jeu de Dominos double-10 :
> 66 dominos, 33 par joueur, distribution fixe — donc un problème de recherche pure
> au sens du cours. On a implémenté 5 IA : une aléatoire et 4 Minimax avec α-β,
> différenciées par leur fonction d'évaluation."*

### Étape 2 — Architecture du code (2 min)
1. Ouvrir VS Code dans le projet
2. Montrer la structure dans l'explorateur :
   - `src/` → moteur de jeu + 5 IA
   - `tests/` → 35 tests unitaires
   - `scripts/` → CLI et benchmarks
   - `resultats/` → données du tournoi
   - `rapport/` → LaTeX + PDF

> *"Architecture orientée objet : Domino, Plateau, Joueur, Partie. Le Domino est
> immuable, ce qui nous a permis d'écrire un clone léger 60× plus rapide que
> deepcopy pour Minimax."*

### Étape 3 — DÉMO interface graphique (5 min)

**Commande à taper** :
```bash
cd C:\Users\sol\Desktop\Projet-Dominos-avec-IA
python -m scripts.interface_graphique
```

**Mode 1 — IA vs IA** :
1. Sélectionner mode "IA vs IA"
2. IA-A = `IA2_pip`, IA-B = `IA3_blocage`
3. Configuration : `ouverte_01` / variante `v0`
4. Cliquer **▶ Auto** à vitesse 700ms
5. Commenter : *"On voit les deux IA jouer. IA-pip cherche à se débarrasser
   des gros pips, IA-blocage cherche à fermer les extrémités à l'adversaire."*
6. Attendre la fin → montrer le popup de fin

**Mode 2 — Humain vs IA** (court) :
1. Retour menu, sélectionner mode "Humain vs IA"
2. IA = `IA5_mixte`
3. Cliquer un domino jouable → l'IA répond automatiquement (auto-play)
4. Commenter : *"L'auto-play continue après notre coup. Les dominos jouables
   sont surlignés en jaune."*

### Étape 4 — DÉMO tests (2 min)

**Commande** :
```bash
python -m pytest tests/ -v
```

> *"35 tests, tous verts en environ 10 secondes. Ils couvrent le moteur de jeu
> mais aussi les 3 cas hiérarchisés de f_blocage et l'indépendance du clone
> léger entre l'original et la copie utilisée par Minimax."*

### Étape 5 — DÉMO benchmark α-β (3 min)

**Commande** :
```bash
python -m scripts.benchmark_alpha_beta
```

> *"On compare Minimax brut, avec α-β seul, et avec α-β + move ordering.
> Le résultat va apparaître dans 30 secondes."*

Quand le tableau s'affiche, commenter :
> *"3.39 secondes sans optim, 0.18 secondes avec α-β + ordering. Soit un facteur
> 18.8× sans changer la qualité du jeu — c'est ce qui nous a permis de faire
> un tournoi de 600 parties en 27 minutes au lieu de plus de 8 heures."*

### Étape 6 — Résultats du tournoi (3 min)

Ouvrir 2-3 graphiques dans `resultats/` :

1. **`classement_global.png`** :
   > *"Voici le classement des 5 IA après 600 parties. IA-pip légèrement en
   > tête à 60%, mais les 4 IA Minimax sont dans la même fourchette de
   > confiance — donc aucune stratégie pure ne domine clairement les autres."*

2. **`noeuds_vs_profondeur.png`** :
   > *"Ici on voit l'explosion exponentielle de l'arbre Minimax. Sans α-β,
   > à profondeur 6, on explore presque 1 million de nœuds par coup. Avec α-β
   > et ordering, on descend à 4 500. Soit 200× moins."*

3. **`avantage_premier_joueur.png`** :
   > *"Tous les couples montrent que le starter gagne en moyenne 61% du temps.
   > Mécaniquement, c'est parce qu'il pose le 10|10 immédiatement, soit 20 pips
   > de moins d'un coup."*

### Étape 7 — Conclusion (1 min)

> *"Pour conclure : on a un code solide validé par 35 tests, un tournoi de 600
> parties qui a tourné en moins d'une heure grâce à α-β, et plusieurs résultats
> scientifiques intéressants : le triangle non-transitif entre les stratégies
> pures, et l'avantage systématique du premier joueur. La principale limite,
> c'est que 60 parties par couple donnent un IC ±13%, donc certaines comparaisons
> ne sont pas significatives. Pour aller plus loin, un tournoi de 200+ parties
> par couple permettrait de trancher."*

---

## 💬 Points clés à mentionner (à caser pendant la démo)

1. **"Variante double-10 (66 dominos)"** — choix justifié par la prof qui a
   dit que 28 dominos étaient trop simples
2. **"Clone léger plutôt que deepcopy"** — gain de 60× sur Minimax
3. **"3 cas hiérarchisés dans f_blocage"** — design original (blocage total >
   partiel via le -1)
4. **"Tournoi stratifié"** — 5 types × 2 configs × 3 variantes × 2 attributions
   = 60 parties par couple, contournant le déterminisme
5. **"Move ordering par pips décroissants"** — gain de 3.7× supplémentaire vs α-β seul

---

## ❓ FAQ — Questions probables

### Sur le jeu

**Q : Pourquoi avez-vous choisi le double-10 et pas le double-6 classique ?**
> R : Parce que vous nous avez dit que 28 dominos étaient trop simples. Le
> double-10 (66 dominos, 33 par joueur) augmente significativement le facteur
> de branchement et la profondeur d'arbre, ce qui rend le projet intéressant
> pour Minimax.

**Q : Comment avez-vous géré le caractère déterministe ?**
> R : C'était notre principal défi. Deux IA déterministes face à la même
> configuration produisent toujours le même match. On a résolu ça avec une
> stratification : 5 types de configurations × 2 par type × 3 variantes
> proches × 2 attributions des mains = 60 parties par couple sans rien
> randomiser dans le moteur.

**Q : Le premier coup forcé, c'est trop rigide non ?**
> R : C'est la règle classique du domino : le possesseur du plus fort double
> commence et le pose. On a juste rendu cette règle explicite et déterministe.

### Sur le code

**Q : Pourquoi Domino est immuable ?**
> R : Pour qu'on puisse partager les références sans risque dans Minimax.
> Quand on clone une partie pour explorer un coup, on ne duplique pas les
> dominos — c'est ça qui nous a fait gagner 60× sur le temps de calcul.

**Q : Pourquoi 4 fonctions d'évaluation ?**
> R : Le sujet en demande 2 à 3 distinctes. On en a fait 4 pour mieux comparer :
> f_pip pour la course aux pips, f_blocage pour l'attaque, f_protect pour la
> défense, f_mixte qui combine les 3.

**Q : Les 3 cas de f_blocage, expliquez.**
> R : C'est une hiérarchie explicite. CAS 1 = les 2 extrémités bloquent
> l'adversaire, score = total des pips de sa main. CAS 2 = une seule
> extrémité, score = total - 1 (juste sous le CAS 1). CAS 3 = aucune
> extrémité bloquée, score = somme des pips des dominos individuellement
> non jouables. Le -1 garantit que blocage total > blocage partiel
> indépendamment de la main de l'adversaire.

### Sur Minimax / α-β

**Q : Pouvez-vous expliquer ce que fait l'élagage α-β ?**
> R : C'est une optimisation de Minimax qui coupe les branches inutiles.
> Quand on est sûr qu'une branche ne peut plus battre la meilleure trouvée
> (parce qu'on a déjà une borne meilleure), on arrête de l'explorer. Ça ne
> change pas le résultat, juste le temps de calcul.

**Q : Le move ordering, c'est quoi ?**
> R : C'est le tri des coups avant de les explorer. On les classe par pips
> décroissants, donc on examine d'abord les "gros coups" qui sont souvent
> les meilleurs. Ça déclenche les coupures α-β plus tôt et réduit l'arbre
> exploré. Mesure : on passe de 31 000 à 9 600 nœuds à profondeur 4.

**Q : Pourquoi IA5_mixte est à profondeur 4 et pas 6 ?**
> R : C'est volontaire. On voulait tester l'hypothèse : "une stratégie
> multi-critères peu profonde peut-elle compenser une moindre profondeur
> face à une stratégie mono-critère plus profonde ?" Réponse : partiellement.
> IA5_mixte bat IA3_blocage (51.7%) mais perd contre IA2_pip (41.7%).

### Sur le tournoi

**Q : Pourquoi 60 parties par couple et pas plus ?**
> R : Le sujet en demande 50 minimum, on a pris 60 (légèrement au-dessus pour
> la marge). Avec 5 IA, ça fait 600 parties au total. Si on était passé à 200
> parties par couple, le tournoi aurait pris plus de 4h au lieu de 27 min.

**Q : Vos résultats sont-ils statistiquement significatifs ?**
> R : Pas tous. À n=60, l'IC à 95% est environ ±13%. La domination de IA-Minimax
> sur l'aléatoire est massive (85%+, très significatif). Mais entre les IA
> Minimax, seules 2 relations sur 6 sont significatives :
> IA3_blocage > IA4_protect et IA2_pip > IA5_mixte. Le triangle non-transitif
> qu'on observe (pip > blocage > protect > pip) est suggéré par les données
> mais pas confirmé statistiquement.

**Q : C'est quoi ce résultat à 50% pour les configs "fermées" ?**
> R : C'est un résultat marquant. Sur les configs fermée, toutes les IA y
> compris l'aléatoire font 50%. Pourquoi ? Parce que ces configs sont
> symétriques par construction : pour chaque variante on joue 2 fois en
> inversant les mains. Dans une position très fermée, le résultat dépend
> uniquement de qui reçoit la "mauvaise" main, pas de la stratégie.
> Conclusion : la stratégie n'a pas d'influence dans ces positions.

**Q : Et l'avantage du premier joueur ?**
> R : 61.2% en moyenne sur les 600 parties, plage 53-67%. C'est mécanique :
> le starter pose le 10|10 dès son premier coup, soit 20 pips disposés d'un
> coup. Sur ~330 pips initiaux, c'est ~6% d'avantage qui se traduit par
> +11% en taux de victoire.

### Sur les difficultés

**Q : Quelle a été votre principale difficulté ?**
> R : La performance de Minimax. Notre première version utilisait deepcopy
> qui rendait un tournoi à profondeur 6 totalement infaisable (estimé à 8h+).
> On a réécrit un clone léger qui exploite l'immuabilité des dominos. Ça nous
> a fait gagner 60× sur le temps.

**Q : Avez-vous eu des bugs subtils ?**
> R : Oui, deux principaux. Le premier dans la GUI : un return mal placé
> lors d'un refactoring laissait tout le code des boutons après le retour
> de la fonction, donc jamais exécuté. Détecté visuellement quand la fenêtre
> apparaissait sans boutons. Le second : le calibrage de f_blocage. Une
> version trop agressive (+200 pour blocage total, +50 pour quasi-blocage)
> a dégradé les performances : trop de bonus rares non-linéaires faisaient
> que l'IA prenait des décisions pip-suboptimales en absence de blocage.

### Sur l'IA générative

**Q : Avez-vous utilisé une IA générative ?**
> R : Oui, ponctuellement, pour de l'aide syntaxique sur Python et LaTeX,
> et pour reformuler quelques tournures du rapport. La conception, les
> choix algorithmiques (notamment la formulation à 3 cas de f_blocage),
> la méthodologie de tournoi et l'analyse des résultats sont notre travail.
> Plusieurs propositions de l'IA ont été rejetées car incorrectes ou
> incohérentes avec notre architecture.

---

## 🎯 Mantras à se rappeler avant la soutenance

1. **Tu sais ce que tu as fait.** Tu as conçu, codé, testé, analysé.
2. **Si tu ne sais pas, dis-le.** "Je vais vérifier" est meilleur qu'inventer.
3. **Reste sur les points forts** : 35 tests verts, 600 parties, 9 graphiques,
   benchmarks reproductibles, structure OO propre.
4. **La prof apprécie la rigueur.** Mentionne les intervalles de confiance,
   le caractère honnête de "ce n'est pas significatif".
5. **Respire.** Tu as 8 jours d'avance sur la deadline. Ton projet est solide.

---

**Bonne chance ! 🍀**
