class Partie :
    #S0 : état initial
    def __init__(self,main_joueur1 , main_joueur2  ):
        self.__MAX = Joueur("MAX",main_joueur1)
        self.__MIN = Joueur("MIN",main_joueur2)
        self.__plateau = Plateau()
        
        self.__joueur_courant = self.__MAX
    #TerminalTest
    def est_terminee(self):

        if self.__MAX.a_gagne():
            return True

        if self.__MIN.a_gagne():
            return True

        if not self.__plateau.coups_possibles(self.__joueur_courant.get_main()):
            return True

        return False
    #player(s)
    def changer_joueur(self):
        if self.__joueur_courant == self.__MAX:
            self.__joueur_courant = self.__MIN
        else:
            self.__joueur_courant = self.__MAX
            
            
    def jouer(self, domino, position):

        ok = self.__plateau.poser_domino(domino, position)

        if ok:
            self.__joueur_courant.retirer_domino(domino)
            self.changer_joueur()

        return ok
    
    #Utility
    def utility(self):

        # Cas 1 : MAX a gagné
        if self.__MAX.a_gagne():
            return self.__MIN.somme_main()  # gain = points adversaire

        # Cas 2 : MIN a gagné
        if self.__MIN.a_gagne():
            return -self.__MAX.somme_main()  # gain négatif pour MAX

        # Cas 3 : partie bloquée (aucun coup possible)
        coups_MAX = self.__plateau.coups_possibles(self.__MAX.get_main())
        coups_MIN = self.__plateau.coups_possibles(self.__MIN.get_main())

        if not coups_MAX and not coups_MIN:
            somme_MAX = self.__MAX.somme_main()
            somme_MIN = self.__MIN.somme_main()
            if somme_MAX < somme_MIN:
                return somme_MIN  # MAX gagne
            elif somme_MIN < somme_MAX:
                return -somme_MAX  # MIN gagne
            else:
                return 0  # égalité

        # Sinon, partie pas terminée
        return None

    def get_joueur1(self) : 
        return self.__MAX

    def get_joueur2(self) : 
        return self.__MIN

    def get_plateau(self):
        return self.__plateau

    def get_joueur_courant(self):
        return self.__joueur_courant

    def set_joueur1(self ,joueur1 ):
        self.__MAX = joueur1

    def set_joueur2(self ,joueur2 ):
        self.__MIN = joueur2

    def set_plateau(self ,plateau ):
        self.__plateau = plateau
        
        
    @staticmethod
    def creer_jeu_complet():
        """Crée la liste complète des 28 dominos."""
        return [Domino(i, j) for i in range(7) for j in range(i, 7)]

    @staticmethod
    def repartir_dominos(dominos):
        """Distribue les dominos équitablement entre 2 joueurs."""
        joueur1 = dominos[::2]  # tous les dominos d'index pair
        joueur2 = dominos[1::2] # tous les dominos d'index impair
        return joueur1, joueur2

    def afficher_partie(self):
        print(f"Joueur 1 : {self.__MAX.get_nom()} avec la main : {self.__joueur1.get_main()}")
        print(f"Joueur 2 : {self.__MIN.get_nom()} avec la main : {self.__joueur2.get_main()}")
        print(f"Plateau : {self.__plateau.get_dominosPoses()} avec extremites gauche : {self.__plateau.get_extremiteGauche()} et droite : {self.__plateau.get_extremiteDroite()}")



    def jouer_tour(self):
        coups = self.__plateau.coups_possibles(self.__joueur_courant.get_main())
        
        if not coups:
            print(f"{self.__joueur_courant.get_nom()} ne peut pas jouer, tour passé")
            self.changer_joueur()
            return  # rien joué ce tour
        
        # sinon choisir et jouer un coup (humain ou IA)
        #choisir_coup retourne un tuple (domino, position) elle est pas deffinie pour le moment 
        domino, position = self.__joueur_courant.choisir_coup(self)
        self.jouer(domino, position)
