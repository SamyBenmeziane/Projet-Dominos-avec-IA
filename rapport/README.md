# Rapport LaTeX — Compilation

## Option 1 — Overleaf (le plus simple, sans rien installer)

1. Va sur [overleaf.com](https://www.overleaf.com) (compte gratuit)
2. Crée un nouveau projet vide
3. Upload :
   - `rapport.tex`
   - **Tous les fichiers PNG** du dossier `../resultats/` (8 fichiers)
4. Mets les PNG dans un sous-dossier `resultats/` au même niveau que `rapport.tex` (ou modifie les chemins `../resultats/` en `resultats/`)
5. Clique sur **Recompile** → tu obtiens le PDF

## Option 2 — Local (Windows avec MiKTeX)

```bash
cd C:\Users\sol\Desktop\Projet-Dominos-avec-IA\rapport
pdflatex rapport.tex
pdflatex rapport.tex   # 2e passe pour la table des matières
```

→ Génère `rapport.pdf`

## Option 3 — VS Code avec extension LaTeX Workshop

1. Installe l'extension "LaTeX Workshop" dans VS Code
2. Installe MiKTeX (Windows) ou TeX Live (autre)
3. Ouvre `rapport.tex` → Build automatique au save

## Ce que tu dois faire dans le fichier

Recherche les **`% TODO`** dans `rapport.tex` :

1. **Page de titre** : remplacer `NOM1 Prénom1` et `NOM2 Prénom2` par tes vrais noms et ceux de ton binôme + emails
2. **Section 5 (IA générative)** : compléter avec ton expérience réelle (modèles, prompts, regard critique)
3. **Optionnel** : ajouter d'autres sous-sections, captures d'écran de tests, etc.

## Structure

```
rapport/
├── rapport.tex     ← le fichier principal (350+ lignes pré-remplies)
├── README.md       ← ce fichier
└── (rapport.pdf généré après compilation)
```

Les 8 graphiques sont référencés depuis `../resultats/*.png`. Si tu déplaces
le rapport ailleurs, ajuste les chemins.
