class Joueur : 
    def __init__(self,nom , main) :
        self.__nom = nom
        self.__main = main  # liste de dominos dans la main du joueur

    def get_nom (self):
        return self.__nom

    def get_main (self):
        return self.__main

    def retirer_domino (self,domino):
        self.__main.remove(domino)

    def afficher_main (self):
        for domino in self.__main :
            domino.afficher()
    
    def a_gagne(self):
        return len(self.__main) == 0

    def somme_main(self):
        total = 0
        for domino in self.__main:
            total += domino.get_gauche() + domino.get_droite()
        return total
    
    def __repr__(self):
        return f"{self.__nom} ({self.somme_main()} pts, {len(self.__main)} dominos)"
