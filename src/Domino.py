class Domino:
    def __init__(self,gauche ,droite) :
        self.__gauche = gauche 
        self.__droite = droite
    
    def get_gauche (self):
        return self.__gauche

    def get_droite (self) : 
        return self.__droite

    #setters
    def set_gauche(self ,valeur):
        if  0<= valeur <= 6 :
            self.__gauche = valeur
        else :
            print(f"{valeur} est invalide !!!")
    
    def set_droite(self,valeur):
        if 0<= valeur <= 6:
            self.__droite = valeur
        else :
            print (f"{valeur} est invalide mon amis ")
            
    def afficher (self):
        print(f"[{self.__gauche}|{self.__droite}]")
    # Méthode pour représenter le domino sous forme de chaîne
    #REPR pour representation
    def __repr__(self):
        return f"[{self.__gauche}|{self.__droite}]"

    
    def retourner (self):
        self.__gauche,self.__droite = self.__droite , self.__gauche
    
    def est_double (self) : 
        return self.__droite == self.__gauche


    