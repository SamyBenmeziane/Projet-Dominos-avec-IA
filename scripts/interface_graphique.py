"""Interface graphique Tkinter pour visualiser une partie de Domino 10|10.

Deux modes au demarrage :
  - IA vs IA  : on regarde 2 IA s'affronter (auto-play / pas a pas)
  - Humain vs IA : on joue soi-meme en cliquant sur un domino jouable

Usage :
    python -m scripts.interface_graphique
"""
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domino import Domino
from src.ia.factory import creer_ia, NIVEAUX
from src.joueur import Joueur, JoueurHumain
from src.partie import Partie
from src.plateau import Coup
from src.tournoi.configurations import configurations_par_defaut


# ======= STYLES =======
COULEUR_FOND = "#2c3e50"
COULEUR_PLATEAU = "#34495e"
COULEUR_DOMINO = "#ecf0f1"
COULEUR_DOMINO_ACTIF = "#f1c40f"
COULEUR_DOMINO_DESACTIVE = "#7f8c8d"
COULEUR_TEXTE = "#ecf0f1"
COULEUR_TEXTE_DOMINO = "#2c3e50"
COULEUR_BOUTON = "#3498db"
COULEUR_VICTOIRE = "#27ae60"


class JoueurHumainGUI(Joueur):
    """Joueur humain pilote par la GUI (clics sur dominos)."""

    def __init__(self, nom: str, main):
        super().__init__(nom, main)

    def choisir_coup(self, partie):
        # Jamais appele : la GUI gere directement le tour humain.
        return None


# ======= FRAME D'ACCUEIL =======

class FrameAccueil(tk.Frame):
    def __init__(self, master, callback_lancer):
        super().__init__(master, bg=COULEUR_FOND)
        self.callback_lancer = callback_lancer

        tk.Label(
            self,
            text="Domino 10|10 — Visualiseur",
            font=("Arial", 24, "bold"),
            fg=COULEUR_TEXTE,
            bg=COULEUR_FOND,
        ).pack(pady=20)

        cadre = tk.Frame(self, bg=COULEUR_FOND)
        cadre.pack(pady=10)

        # Mode
        tk.Label(cadre, text="Mode :", font=("Arial", 12), fg=COULEUR_TEXTE, bg=COULEUR_FOND).grid(
            row=0, column=0, sticky="e", padx=10, pady=5
        )
        self.var_mode = tk.StringVar(value="ia_vs_ia")
        modes = [("IA vs IA", "ia_vs_ia"), ("Humain vs IA", "humain_vs_ia")]
        cadre_modes = tk.Frame(cadre, bg=COULEUR_FOND)
        cadre_modes.grid(row=0, column=1, sticky="w")
        for txt, val in modes:
            tk.Radiobutton(
                cadre_modes,
                text=txt,
                variable=self.var_mode,
                value=val,
                fg=COULEUR_TEXTE,
                bg=COULEUR_FOND,
                selectcolor=COULEUR_PLATEAU,
                font=("Arial", 11),
                command=self._maj_visibilite,
            ).pack(side="left", padx=5)

        # IA A
        tk.Label(cadre, text="Niveau IA A :", font=("Arial", 12), fg=COULEUR_TEXTE, bg=COULEUR_FOND).grid(
            row=1, column=0, sticky="e", padx=10, pady=5
        )
        self.var_ia_a = tk.StringVar(value="IA2_pip")
        self.combo_ia_a = ttk.Combobox(
            cadre, textvariable=self.var_ia_a, values=list(NIVEAUX), state="readonly", width=25
        )
        self.combo_ia_a.grid(row=1, column=1, sticky="w")

        # IA B
        self.label_ia_b = tk.Label(
            cadre, text="Niveau IA B :", font=("Arial", 12), fg=COULEUR_TEXTE, bg=COULEUR_FOND
        )
        self.label_ia_b.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.var_ia_b = tk.StringVar(value="IA5_mixte")
        self.combo_ia_b = ttk.Combobox(
            cadre, textvariable=self.var_ia_b, values=list(NIVEAUX), state="readonly", width=25
        )
        self.combo_ia_b.grid(row=2, column=1, sticky="w")

        # Configuration
        try:
            self.configs = configurations_par_defaut(Path("resultats") / "configurations.json")
        except Exception:
            self.configs = configurations_par_defaut()
        tk.Label(cadre, text="Configuration :", font=("Arial", 12), fg=COULEUR_TEXTE, bg=COULEUR_FOND).grid(
            row=3, column=0, sticky="e", padx=10, pady=5
        )
        self.var_config = tk.StringVar(value=self.configs[0].id)
        self.combo_config = ttk.Combobox(
            cadre,
            textvariable=self.var_config,
            values=[c.id for c in self.configs],
            state="readonly",
            width=25,
        )
        self.combo_config.grid(row=3, column=1, sticky="w")

        # Variante
        tk.Label(cadre, text="Variante :", font=("Arial", 12), fg=COULEUR_TEXTE, bg=COULEUR_FOND).grid(
            row=4, column=0, sticky="e", padx=10, pady=5
        )
        self.var_variante = tk.StringVar(value="v0")
        ttk.Combobox(
            cadre, textvariable=self.var_variante, values=["v0", "v1", "v2"], state="readonly", width=25
        ).grid(row=4, column=1, sticky="w")

        # Bouton lancer
        tk.Button(
            self,
            text="Lancer la partie",
            font=("Arial", 14, "bold"),
            bg=COULEUR_BOUTON,
            fg="white",
            command=self._on_lancer,
            padx=20,
            pady=10,
        ).pack(pady=30)

    def _maj_visibilite(self):
        if self.var_mode.get() == "humain_vs_ia":
            self.label_ia_b.config(text="Niveau de l'IA :")
            self.combo_ia_a.grid_remove()
            # Cache la ligne IA A
        else:
            self.label_ia_b.config(text="Niveau IA B :")
            self.combo_ia_a.grid()

    def _on_lancer(self):
        cfg = next(c for c in self.configs if c.id == self.var_config.get())
        var = next(v for v in cfg.variantes if v.id == self.var_variante.get())
        self.callback_lancer(
            mode=self.var_mode.get(),
            niveau_a=self.var_ia_a.get(),
            niveau_b=self.var_ia_b.get(),
            main_alpha=list(var.main_alpha),
            main_beta=list(var.main_beta),
            cfg_id=cfg.id,
            var_id=var.id,
        )


# ======= WIDGET DOMINO =======

def make_domino_widget(parent, domino: Domino, jouable: bool = False, on_click=None) -> tk.Frame:
    """Cree un widget visuel pour un domino : 2 cases avec les nombres."""
    couleur_fond = COULEUR_DOMINO_ACTIF if jouable else COULEUR_DOMINO
    f = tk.Frame(parent, bg="black", bd=1)
    g = tk.Label(
        f,
        text=str(domino.a),
        font=("Arial", 14, "bold"),
        bg=couleur_fond,
        fg=COULEUR_TEXTE_DOMINO,
        width=2,
        height=1,
    )
    d = tk.Label(
        f,
        text=str(domino.b),
        font=("Arial", 14, "bold"),
        bg=couleur_fond,
        fg=COULEUR_TEXTE_DOMINO,
        width=2,
        height=1,
    )
    g.pack(side="left", padx=1, pady=1)
    d.pack(side="left", padx=1, pady=1)
    if jouable and on_click is not None:
        for w in (f, g, d):
            w.bind("<Button-1>", lambda e: on_click())
            w.config(cursor="hand2")
    return f


# ======= FRAME DE JEU =======

class FrameJeu(tk.Frame):
    def __init__(self, master, callback_retour):
        super().__init__(master, bg=COULEUR_FOND)
        self.callback_retour = callback_retour
        self.partie: Optional[Partie] = None
        self.humain: Optional[Joueur] = None
        self.auto_play = False
        self.vitesse_ms = 700
        self.coup_humain_choisi: Optional[Coup] = None
        self._construire()

    def _construire(self):
        # Bandeau du haut : statut
        self.label_statut = tk.Label(
            self,
            text="",
            font=("Arial", 14, "bold"),
            fg=COULEUR_TEXTE,
            bg=COULEUR_FOND,
        )
        self.label_statut.pack(pady=10)

        # Main joueur 1 (haut) - scrollable
        (
            self.label_main_a,
            self.canvas_main_a,
            self.inner_main_a,
        ) = self._construire_main_scrollable(self)

        # Plateau
        cadre_plateau = tk.Frame(self, bg=COULEUR_PLATEAU, height=80)
        cadre_plateau.pack(pady=10, fill="x", padx=10)
        cadre_plateau.pack_propagate(False)
        self.canvas_plateau = tk.Canvas(
            cadre_plateau, bg=COULEUR_PLATEAU, height=70, highlightthickness=0
        )
        self.canvas_plateau.pack(side="top", fill="both", expand=True)
        scroll_pl = tk.Scrollbar(cadre_plateau, orient="horizontal", command=self.canvas_plateau.xview)
        scroll_pl.pack(side="bottom", fill="x")
        self.canvas_plateau.config(xscrollcommand=scroll_pl.set)
        self.frame_plateau_inner = tk.Frame(self.canvas_plateau, bg=COULEUR_PLATEAU)
        self.canvas_plateau.create_window((10, 10), window=self.frame_plateau_inner, anchor="nw")

        # Main joueur 2 (bas) - scrollable
        (
            self.label_main_b,
            self.canvas_main_b,
            self.inner_main_b,
        ) = self._construire_main_scrollable(self)

        # Controles
        cadre_ctrl = tk.Frame(self, bg=COULEUR_FOND)
        cadre_ctrl.pack(pady=10)

        self.bouton_step = tk.Button(
            cadre_ctrl, text="Coup suivant >", command=self._on_step, bg=COULEUR_BOUTON, fg="white",
            font=("Arial", 11), padx=10
        )
        self.bouton_step.pack(side="left", padx=5)

        self.bouton_auto = tk.Button(
            cadre_ctrl, text="▶ Auto", command=self._toggle_auto, bg=COULEUR_BOUTON, fg="white",
            font=("Arial", 11), padx=10
        )
        self.bouton_auto.pack(side="left", padx=5)

        self.bouton_reset = tk.Button(
            cadre_ctrl, text="↻ Retour menu", command=self._on_retour, bg="#e74c3c", fg="white",
            font=("Arial", 11), padx=10
        )
        self.bouton_reset.pack(side="left", padx=5)

        tk.Label(cadre_ctrl, text="Vitesse :", fg=COULEUR_TEXTE, bg=COULEUR_FOND, font=("Arial", 11)).pack(
            side="left", padx=(20, 5)
        )
        self.scale_vitesse = tk.Scale(
            cadre_ctrl,
            from_=100,
            to=2000,
            orient="horizontal",
            length=200,
            bg=COULEUR_FOND,
            fg=COULEUR_TEXTE,
            highlightthickness=0,
            troughcolor=COULEUR_PLATEAU,
            label="ms / coup",
            command=self._on_vitesse,
        )
        self.scale_vitesse.set(self.vitesse_ms)
        self.scale_vitesse.pack(side="left", padx=5)

        # Historique
        cadre_hist = tk.Frame(self, bg=COULEUR_FOND)
        cadre_hist.pack(pady=5, fill="both", expand=True, padx=10)
        tk.Label(
            cadre_hist, text="Historique des coups", fg=COULEUR_TEXTE, bg=COULEUR_FOND,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        self.text_hist = tk.Text(
            cadre_hist, height=8, bg=COULEUR_PLATEAU, fg=COULEUR_TEXTE,
            font=("Consolas", 10), state="disabled",
        )
        self.text_hist.pack(fill="both", expand=True)

    def _construire_main_scrollable(self, parent):
        """Cree un cadre main joueur avec scrollbar horizontale."""
        frame = tk.Frame(parent, bg=COULEUR_FOND)
        frame.pack(pady=5, fill="x", padx=10)

        label = tk.Label(
            frame, text="", font=("Arial", 11, "bold"),
            fg=COULEUR_TEXTE, bg=COULEUR_FOND, anchor="w",
        )
        label.pack(side="top", fill="x")

        cadre_canvas = tk.Frame(frame, bg=COULEUR_FOND, height=70)
        cadre_canvas.pack(side="top", fill="x")
        cadre_canvas.pack_propagate(False)

        canvas = tk.Canvas(cadre_canvas, bg=COULEUR_FOND, height=55, highlightthickness=0)
        canvas.pack(side="top", fill="x", expand=True)

        scroll = tk.Scrollbar(cadre_canvas, orient="horizontal", command=canvas.xview)
        scroll.pack(side="bottom", fill="x")
        canvas.config(xscrollcommand=scroll.set)

        inner = tk.Frame(canvas, bg=COULEUR_FOND)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        # support molette : scroll horizontal avec Shift+wheel ou wheel direct
        def _on_wheel(e, c=canvas):
            c.xview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_wheel)
        inner.bind("<MouseWheel>", _on_wheel)

        return label, canvas, inner

    # ----- API publique -----

    def demarrer(
        self,
        mode: str,
        niveau_a: str,
        niveau_b: str,
        main_alpha: list,
        main_beta: list,
        cfg_id: str,
        var_id: str,
    ):
        self.auto_play = False
        self.coup_humain_choisi = None
        self.cfg_info = f"{cfg_id} / {var_id}"
        if mode == "ia_vs_ia":
            j1 = creer_ia(niveau_a, "IA_A", main_alpha, seed=42)
            j2 = creer_ia(niveau_b, "IA_B", main_beta, seed=43)
            self.humain = None
        else:
            j1 = JoueurHumainGUI("Humain", main_alpha)
            j2 = creer_ia(niveau_b, niveau_b.split("_", 1)[0], main_beta, seed=43)
            self.humain = j1
        self.partie = Partie(j1, j2)
        self._maj_affichage()

    # ----- Logique de jeu -----

    def _on_step(self):
        if self.partie is None or self.partie.est_terminee():
            return
        courant = self.partie.joueur_courant
        coups = self.partie.plateau.coups_possibles(courant.main)
        if not coups:
            self.partie._historique.append((courant.nom, None))
            self.partie.changer_joueur()
            self._maj_affichage()
            return
        forced = self.partie.coup_force()
        if forced is not None:
            self.partie.jouer_coup(*forced)
            self._maj_affichage()
            return
        if self.humain is not None and courant is self.humain:
            # Attendre clic
            self._maj_affichage()
            return
        coup = courant.choisir_coup(self.partie)
        if coup is not None:
            self.partie.jouer_coup(*coup)
        else:
            # Defensive : IA retourne None malgre des coups dispo -> on passe
            self.partie._historique.append((courant.nom, None))
            self.partie.changer_joueur()
        self._maj_affichage()

    def _toggle_auto(self):
        if self.partie is None:
            return
        self.auto_play = not self.auto_play
        self.bouton_auto.config(text="⏸ Pause" if self.auto_play else "▶ Auto")
        if self.auto_play:
            self._auto_step()

    def _auto_step(self):
        if not self.auto_play or self.partie is None or self.partie.est_terminee():
            self.auto_play = False
            self.bouton_auto.config(text="▶ Auto")
            return
        # En mode humain : si c'est le tour de l'humain et qu'il doit choisir,
        # on attend son clic SANS desactiver auto_play. Ainsi l'IA pourra
        # repondre automatiquement apres le clic via _on_clic_humain.
        if self.humain is not None and self.partie.joueur_courant is self.humain:
            coups = self.partie.plateau.coups_possibles(self.humain.main)
            forced = self.partie.coup_force()
            if coups and forced is None:
                # En attente du clic humain — auto_play reste actif
                self._maj_affichage()
                return
        self._on_step()
        if self.partie.est_terminee():
            self.auto_play = False
            self.bouton_auto.config(text="▶ Auto")
            return
        self.after(self.vitesse_ms, self._auto_step)

    def _on_vitesse(self, val):
        self.vitesse_ms = int(val)

    def _on_retour(self):
        self.auto_play = False
        self.callback_retour()

    def _on_clic_humain(self, coup):
        if self.humain is None or self.partie is None:
            return
        if self.partie.joueur_courant is not self.humain:
            return
        self.partie.jouer_coup(*coup)
        self._maj_affichage()
        # Si auto_play est actif, relancer la boucle pour que l'IA reponde
        # automatiquement apres le coup humain (sans clic supplementaire)
        if self.auto_play and not self.partie.est_terminee():
            self.after(self.vitesse_ms, self._auto_step)

    # ----- Affichage -----

    def _maj_affichage(self):
        if self.partie is None:
            return
        self._dessiner_main(
            self.partie.joueur1, self.label_main_a, self.canvas_main_a, self.inner_main_a
        )
        self._dessiner_main(
            self.partie.joueur2, self.label_main_b, self.canvas_main_b, self.inner_main_b
        )
        self._dessiner_plateau()
        self._maj_statut()
        self._maj_historique()
        if self.partie.est_terminee():
            self._afficher_fin()

    def _dessiner_main(self, joueur: Joueur, label: tk.Label, canvas: tk.Canvas, inner: tk.Frame):
        # Mise a jour du label
        nom = f"{joueur.nom} ({joueur.somme_pips()} pips, {len(joueur.main)} dominos)"
        if self.partie.joueur_courant is joueur and not self.partie.est_terminee():
            nom = "▶ " + nom + "  [c'est son tour]"
        label.config(text=nom)

        # Vide les anciens widgets
        for w in inner.winfo_children():
            w.destroy()

        # Cacher la main de l'IA en mode humain
        cacher = self.humain is not None and joueur is not self.humain
        if cacher:
            tk.Label(
                inner, text="[ main cachee ]", font=("Arial", 11),
                fg=COULEUR_DOMINO_DESACTIVE, bg=COULEUR_FOND
            ).pack(side="left", padx=5, pady=10)
            inner.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            return

        coups_jouables = (
            self.partie.plateau.coups_possibles(joueur.main)
            if self.partie.joueur_courant is joueur and not self.partie.est_terminee()
            else []
        )
        forced = self.partie.coup_force() if self.partie.joueur_courant is joueur else None

        for d in joueur.main:
            est_courant = self.partie.joueur_courant is joueur
            jouable = est_courant and any(c[0] == d for c in coups_jouables)
            if forced is not None:
                jouable = est_courant and (d == forced[0])
            on_click = None
            if jouable and joueur is self.humain:
                positions = [c[1] for c in coups_jouables if c[0] == d]
                if forced is not None and d == forced[0]:
                    positions = [forced[1]]
                on_click = lambda dom=d, poss=positions: self._sur_clic_domino(dom, poss)
            w = make_domino_widget(inner, d, jouable=jouable, on_click=on_click)
            w.pack(side="left", padx=2, pady=2)

        # Met a jour la zone scrollable
        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _sur_clic_domino(self, domino: Domino, positions_possibles: list[str]):
        if len(positions_possibles) == 1:
            self._on_clic_humain((domino, positions_possibles[0]))
            return
        # Demander la position
        choix = messagebox.askyesnocancel(
            "Position", f"Poser {domino} a gauche (Oui) ou a droite (Non) ?"
        )
        if choix is None:
            return
        position = "gauche" if choix else "droite"
        if position in positions_possibles:
            self._on_clic_humain((domino, position))

    def _dessiner_plateau(self):
        for w in self.frame_plateau_inner.winfo_children():
            w.destroy()
        plateau = self.partie.plateau
        if plateau.vide:
            tk.Label(
                self.frame_plateau_inner, text="Plateau vide",
                font=("Arial", 12, "italic"), fg=COULEUR_TEXTE, bg=COULEUR_PLATEAU
            ).pack()
        else:
            # extremites visibles a gauche et a droite
            tk.Label(
                self.frame_plateau_inner, text=f"<-{plateau.extremite_gauche}",
                font=("Arial", 12, "bold"), fg=COULEUR_DOMINO_ACTIF, bg=COULEUR_PLATEAU
            ).pack(side="left", padx=5)
            for d in plateau.dominos_poses:
                w = make_domino_widget(self.frame_plateau_inner, d, jouable=False)
                w.pack(side="left", padx=2)
            tk.Label(
                self.frame_plateau_inner, text=f"{plateau.extremite_droite}->",
                font=("Arial", 12, "bold"), fg=COULEUR_DOMINO_ACTIF, bg=COULEUR_PLATEAU
            ).pack(side="left", padx=5)
        self.frame_plateau_inner.update_idletasks()
        self.canvas_plateau.config(scrollregion=self.canvas_plateau.bbox("all"))

    def _maj_statut(self):
        p = self.partie
        nb_coups = len(p.historique)
        if p.est_terminee():
            statut = "Partie terminee"
        else:
            statut = f"Tour {nb_coups + 1} - Joueur courant : {p.joueur_courant.nom}"
        self.label_statut.config(text=f"{statut}    |    Configuration : {self.cfg_info}")

    def _maj_historique(self):
        self.text_hist.config(state="normal")
        self.text_hist.delete("1.0", "end")
        for i, (nom, coup) in enumerate(self.partie.historique, 1):
            if coup is None:
                self.text_hist.insert("end", f"{i:3d}. {nom} : passe\n")
            else:
                d, pos = coup
                self.text_hist.insert("end", f"{i:3d}. {nom} pose {d} a {pos}\n")
        self.text_hist.see("end")
        self.text_hist.config(state="disabled")

    def _afficher_fin(self):
        u = self.partie.utility()
        if u == 1:
            gagnant = self.partie.joueur1.nom
        elif u == -1:
            gagnant = self.partie.joueur2.nom
        else:
            gagnant = "Egalite"
        msg = (
            f"Vainqueur : {gagnant}\n\n"
            f"Pips restants :\n"
            f"  {self.partie.joueur1.nom}: {self.partie.joueur1.somme_pips()}\n"
            f"  {self.partie.joueur2.nom}: {self.partie.joueur2.somme_pips()}\n\n"
            f"Nombre de coups : {len(self.partie.historique)}"
        )
        messagebox.showinfo("Fin de partie", msg)


# ======= APPLICATION =======

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Domino 10|10 - Visualiseur IA")
        self.geometry("1100x750")
        self.configure(bg=COULEUR_FOND)
        self.frame_accueil = FrameAccueil(self, callback_lancer=self._on_lancer)
        self.frame_jeu = FrameJeu(self, callback_retour=self._on_retour_accueil)
        self.frame_accueil.pack(fill="both", expand=True)

    def _on_lancer(self, **kwargs):
        self.frame_accueil.pack_forget()
        self.frame_jeu.pack(fill="both", expand=True)
        self.frame_jeu.demarrer(**kwargs)

    def _on_retour_accueil(self):
        self.frame_jeu.pack_forget()
        self.frame_accueil.pack(fill="both", expand=True)


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
