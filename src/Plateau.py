from copy import deepcopy
class Plateau :
    def __init__(self):
        self.__dominosPoses = []
        self.__extremiteGauche = None
        self.__extremiteDroite = None

    # action(s)
    def coups_possibles(self,main_joueur):
            coups = []
            if self.plateauVide() : 
                for domino in main_joueur :
                    coups.append((domino,"gauche"))
                    coups.append((domino,"droite"))
                return coups 
            else :
                for domino in main_joueur :
                    if domino.get_gauche() == self.__extremiteGauche or domino.get_droite() == self.__extremiteGauche :
                        coups.append((domino,"gauche"))
                    if domino.get_gauche() == self.__extremiteDroite or domino.get_droite() == self.__extremiteDroite :
                        coups.append((domino,"droite"))
                return coups
    
    # resultat(s,coup)        
    def simuler_coup(self, domino, position):
        copie = deepcopy(self)
        copie.poser_domino(domino, position)
        return copie   

    def poser_domino(self, domino, position):

        # Plateau vide
        if self.plateauVide():
            self.__dominosPoses.append(domino)
            self.__extremiteGauche = domino.get_gauche()
            self.__extremiteDroite = domino.get_droite()
            return True
        # ----- CÔTÉ GAUCHE -----
        if position == "gauche":
            # Si déjà bon
            if domino.get_droite() == self.__extremiteGauche:
                pass
            # Sinon on essaie de retourner
            elif domino.get_gauche() == self.__extremiteGauche:
                domino.retourner()
            # Sinon impossible
            else:
                print("Coup illégal à gauche")
                return False
            # On ajoute
            #INSERTION EN TÊTE SANS ECRASER LES AUTRES ÉLÉMENTS
            self.__dominosPoses.insert(0, domino)
            self.__extremiteGauche = domino.get_gauche()
            return True
        # ----- CÔTÉ DROIT -----
        elif position == "droite":
            if domino.get_gauche() == self.__extremiteDroite:
                pass
            elif domino.get_droite() == self.__extremiteDroite:
                domino.retourner()
            else:
                print("Coup illégal à droite")
                return False
            self.__dominosPoses.append(domino)
            self.__extremiteDroite = domino.get_droite()
            return True


        # ----- POSITION INVALIDE -----
        else:
            print("Position invalide")
            return False

    def get_dominosPoses (self):
        return self.__dominosPoses

    def get_extremiteGauche (self):
        return self.__extremiteGauche

    def get_extremiteDroite (self):
        return self.__extremiteDroite

    def plateauVide(self):
        return not self.__dominosPoses
            
    