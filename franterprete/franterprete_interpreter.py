#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : franterprete_interpreter.py
  Rôle ........ : interprète les commandes du franterprète
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 05/11/2023
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : classes appelées dans franterprete.py
'''

import os # chdir
import math # floor / ceil (arrondis)
from .franterprete_input import FranterpreteInput # gère les saisies
from .franterprete_lexer import FranterpreteLexer
from .franterprete_parser import FranterpreteParser

# dictionnaires stockant les environnements d'exécution
class Env(dict):
  
  # constructeur
  def __init__(self, outer=None):
    self.outer = outer # environnement englobant
    
  # renvoie l'environnement le plus proche associé à un nom
  def findEnv(self, nom):
    return self if (nom in self) else self.outer.findEnv(nom)
  
  # renvoie la valeur associée à un nom dans l'environnement le plus proche
  def findValue(self, nom):
    return self.findEnv(nom)[nom]
  
  # change la valeur associée à un nom dans l'environnement le plus proche
  def changeValue(self, nom, valeur=None):
    self.findEnv(nom)[nom] = valeur
    
# exception mettant fin à l'exécution d'un programme avec valeur de retour
class Fin(Exception):
  
  # constructeur
  def __init__(self, valeur=None):
    self.valeur = valeur # valeur de retour  

#####################################################################################
#                                   INTERPRÉTEUR                                    #
#####################################################################################

class FranterpreteInterpreter:
  
  # constructeur
  def __init__(self):
    self.env = Env() # initialise l'environnement global
    self.postInstruction = [] # liste laissant la possibilité d'avoir plusieurs postInstructions (évolution possible)
    self.fonctions_natives = {
      'AFFICHER': self.affiche,
      'ARRI': self.arri,
      'ARRS': self.arrs,
      'BOOLF': self.boolf,
      'CEXECUTER': self.cexe,
      'CHAINEF': self.chainef,
      'CHARGER': self.charger,
      'CLIRE': self.clire,
      'CR': self.cr,
      'ECRIRE': self.ecrire,
      'EXECUTER': self.exe,
      'INSTANCE': self.instance,
      'LIRE': self.lire,
      'LONGUEUR': self.longueur,
      'MAJUSCULE': self.majuscule,
      'MINUSCULE': self.minuscule,
      'NOMBREF': self.nombref,
      'SAISIR' : self.saisir,
      'TABLEAU': self.tableau,
      'TRIER': self.trier,
      }
  
  # vide les post-instructions et revient à l'environnement global
  def clear(self):
    self.postInstruction.clear() # vide les postInstructions
    while self.env.outer is not None: # revient à l'environnement d'exécution global
      self.env = self.env.outer
  
  # parcourt et exécute l'arbre syntaxique puis affiche et retourne le résultat
  def execute(self, arbre):
    try:
      resultat = self.parcourir(arbre)
    except Fin as fin: # FIN acceptée comme simple commande
      if fin.valeur is not None:
        print(fin.valeur)
      return fin.valeur
    else: # pas finally pour les exceptions du prompt
      if isinstance(resultat, tuple): # instruction de contrôle
        if resultat[0] != 'retourner': # INTER et CONT non acceptée comme simple commande (boucle obligatoire)
          print('Instruction de contrôle de boucle invalide dans ce contexte')
        resultat = resultat[1] # RET acceptée comme simple commande
      if resultat is not None: # n'affiche pas un résultat vide
        print(resultat)
      return resultat
  
  # parcourt l'arbre syntaxique
  def parcourir(self, node, objet=None):
    
    ##################################### TYPES #####################################
    
    if isinstance(node, (bool, float, int, str)) or node is None:
      return node
    
    elif node[0] in ('booleen', 'chaine', 'nombre', 'tableau', 'vide'):
      return self.parcourir(node[1])
    
    ################################# INSTRUCTIONS ##################################
    
    elif node[0] in ('suite_instructions', 'instruction'):
      resultat = self.parcourir(node[1])
      for instruction in self.postInstruction: # exécute les postIntructions (i++ par exemple)
        self.parcourir(instruction)
      self.postInstruction.clear() # vide les postInstructions
      return resultat if (node[0] == 'instruction' or isinstance(resultat, tuple)) else self.parcourir(node[2]) # continue si d'autres instructions
    
    elif node[0] == 'fin': # arrête une suite d'instruction et renvoie une valeur
      fin = Fin(self.parcourir(node[1])) # crée l'exception avec la valeur à renvoyer
      self.clear() # vide les postIntructions et revient à l'environnement global
      raise fin # stoppe l'exécution et renvoie la valeur
    
    #################################################################################
    
    elif node[0] in ('liste_expressions', 'liste_indices', 'liste_parametres'):
      liste = [self.parcourir(node[1]), self.parcourir(node[2][1])] # une liste contient deux éléments au minimum
      if node[2][0] == node[0]: # vérifie que la liste continue
        liste.extend(self.parcourir(node[2][2])) # aplatie la liste imbriquée issue du parser
      return liste
    
    elif node[0] in ('expression', 'indice', 'parametre'):
      valeur = self.parcourir(node[1])
      return [] if (valeur is None) else [valeur] # si aucune valeur, renvoie [] au lieu de [None]
    
    ################################### FONCTIONS ###################################
    
    elif node[0] == 'declaration_fonction':
      nom = node[1][1]
      if nom in self.fonctions_natives:
        print(nom + '() est une fonction native du Franterprète')
        return
      liste_parametres = self.parcourir(node[2])
      self.env[nom] = liste_parametres, node[3] # stocke paramètres et instructions de la fonction
      print(nom + '(' + ', '.join(liste_parametres) + ')')
      
    elif node[0] == 'appel_fonction':
      try:
        liste_arguments = self.parcourir(node[2])
        if node[1] in self.fonctions_natives:
          return self.fonctions_natives[node[1]](liste_arguments)
        fonction = self.env.findValue(node[1])
        liste_parametres = fonction[0]
        self.env = Env(outer=self.env) # crée et bascule sur l'environnement local
        longueur_args_max = len(liste_parametres)
        longueur_args = len(liste_arguments)
        if longueur_args < longueur_args_max: # si arguments manquants:
          liste_arguments.extend([None] * (longueur_args_max - longueur_args)) # alors leur affecter None
        for parametre, argument in zip(liste_parametres, liste_arguments): # matche paramètres et arguments
          self.env[parametre] = argument # ajoute un paramètre et l'argument correspondant dans l'environnement local
        resultat = self.parcourir(fonction[1]) # exécute la fonction
        if isinstance(resultat, tuple) and resultat[0] == 'retourner':
          resultat = resultat[1]
        self.env = self.env.outer # revient à l'environnement initial
        return resultat
      except AttributeError:
        print('Fonction non définie ' + node[1])
        
    elif node[0] == 'retourner':
      return ('retourner', self.parcourir(node[1]))
    
    ###################################### SI #######################################
    
    elif node[0] == 'si':
      return self.parcourir(node[2]) if self.parcourir(node[1]) else None
    
    elif node[0] == 'si_sinon':
      return self.parcourir(node[2]) if self.parcourir(node[1]) else self.parcourir(node[3])
    
    ##################################### SWITCH ####################################
    
    elif node[0] == 'switch':
      return self.parcourir(node[2], self.parcourir(node[1])) # transmet l'expression à comparer
    
    # si expression == cas sinon passe au cas suivant
    elif node[0] == 'cas':
      return self.parcourir(node[2]) if (objet == self.parcourir(node[1])) else self.parcourir(node[3], objet)
    
    elif node[0] == 'autrement':
      return self.parcourir(node[1])
    
    ##################################### POUR ######################################
    
    elif node[0] == 'pour':
      self.parcourir(node[1]) # instruction d'initialisation de boucle
      while self.parcourir(node[2]):
        resultat = self.parcourir(node[4]) # exécute bloc d'instructions
        if isinstance(resultat, tuple) and resultat[0] != 'continuer': # si interrompre ou retourner
          return resultat if resultat[0] == 'retourner' else None
        self.parcourir(node[3]) # instruction fin de boucle
        
    elif node[0] == 'pour_chaque':
      for self.env[node[1]] in self.parcourir(node[2]):
        resultat = self.parcourir(node[3]) # exécute bloc d'instructions
        if isinstance(resultat, tuple) and resultat[0] != 'continuer': # si interrompre ou retourner
          return resultat if resultat[0] == 'retourner' else None
    
    #################################### TANTQUE ####################################
    
    elif node[0] == 'tantque':
      while self.parcourir(node[1]):
        resultat = self.parcourir(node[2]) # exécute bloc d'instructions
        if isinstance(resultat, tuple) and resultat[0] != 'continuer': # si interrompre ou retourner
          return resultat if resultat[0] == 'retourner' else None
    
    #################################### RÉPÉTER ####################################
    
    elif node[0] == 'repeter':
      while True:
        resultat = self.parcourir(node[1]) # exécute bloc d'instructions
        if isinstance(resultat, tuple) and resultat[0] != 'continuer': # si interrompre ou retourner
          return resultat if resultat[0] == 'retourner' else None
        if not self.parcourir(node[2]): break # condition de boucle
      
    ###################### CONTRÔLE STRUCTURES DE RÉPÉTITIONS #######################
    
    elif node[0] == 'continuer':
      return ('continuer', None)
    
    elif node[0] == 'interrompre':
      return ('interrompre', None)
    
    ################################### ITÉRABLE ####################################
    
    elif node[0] == 'nom':
      try:
        valeur = self.env.findValue(node[1])
        if isinstance(valeur, tuple): # si fonction
          print('Fonction usage: ' + node[1] + '(' + ', '.join(valeur[0]) + ')')
          return None
        return valeur
      except AttributeError:
        print("Variable non définie " + node[1])
        
    elif node[0] == 'acces_tableau':
      tableau = self.parcourir(node[1])
      liste_indices = self.parcourir(node[2])
      if not liste_indices:
        return tableau
      for indice in liste_indices:
        tableau = tableau[indice]
      return tableau
    
    ################################## AFFECTATION ##################################
    
    elif node[0] == 'affectation':
      if node[1][1][0] == 'nom':
        try:
          if node[1][1][2] == 'globale':
            self.env.changeValue(node[1][1][1], self.parcourir(node[1])) # la variable globale doit déjà exister
          else:
            self.env[node[1][1][1]] = self.parcourir(node[1]) # créer ou modifie la variable
          return node[1][1][1]
        except AttributeError:
          print("Variable non définie " + node[1][1][1])
          return None
      else:
        tableau = self.parcourir(node[1][1][1]) # le tablau doit déjà exister
        liste_indices = self.parcourir(node[1][1][2])
        if not liste_indices:
          tableau.append(self.parcourir(node[1])) # si aucun indice renseigné, ajoute à la fin du tableau
        else:
          for indice in liste_indices[:-1]: # balaye la matrice pour trouver l'emplacement
            tableau = tableau[indice]
          tableau[liste_indices[-1]] = self.parcourir(node[1]) # affecte dans la matrice
      return tableau
        
    elif node[0] == 'egal_affectation':
      return self.parcourir(node[2])
    
    ################################ DÉCALAGE DE BITS ###############################
    
    elif node[0] == 'decalg':
      return self.parcourir(node[1]) << self.parcourir(node[2])
    
    elif node[0] == 'decald':
      return self.parcourir(node[1]) >> self.parcourir(node[2])
    
    ######################## INCRÉMENTATION / DÉCRÉMENTATION ########################
    
    elif node[0] == 'incg':
      valeur = self.parcourir(node[1])
      if valeur is not None:
        self.postInstruction.append(('incd', node[1])) # ajoute l'incrémentation aux postinstructions
        return valeur # renvoie valeur avant incrémentation
    
    elif node[0] == 'incd':
      nom = node[1][1]
      valeur = self.parcourir(node[1])
      if valeur is not None:
        self.env.findEnv(nom)[nom] = valeur + 1 # incrémente
        return self.parcourir(node[1]) # renvoie valeur incrémentée
        
    elif node[0] == 'decg':
      valeur = self.parcourir(node[1])
      if valeur is not None:
        self.postInstruction.append(('decd', node[1])) # ajoute la décrémentation aux postinstructions
        return valeur # renvoie valeur avant décrémentation
    
    elif node[0] == 'decd':
      nom = node[1][1]
      valeur = self.parcourir(node[1])
      if valeur is not None:
        self.env.findEnv(nom)[nom] = valeur - 1 # décrémente
        return self.parcourir(node[1]) # renvoie valeur décrémentée
    
    ################################## COMPARAISON ##################################
    
    elif node[0] == 'egal':
      return self.parcourir(node[1]) == self.parcourir(node[2])
    
    elif node[0] == 'different':
      return self.parcourir(node[1]) != self.parcourir(node[2])
    
    elif node[0] == 'superieur':
      return self.parcourir(node[1]) > self.parcourir(node[2])
    
    elif node[0] == 'inferieur':
      return self.parcourir(node[1]) < self.parcourir(node[2])
    
    elif node[0] == 'superieuregal':
      return self.parcourir(node[1]) >= self.parcourir(node[2])
    
    elif node[0] == 'inferieuregal':
      return self.parcourir(node[1]) <= self.parcourir(node[2])
    
    ########################## ARITHMÉTIQUE / AFFECTATION ###########################
    
    elif node[0] in ('addition', 'plus_affectation'):
      return self.parcourir(node[1]) + self.parcourir(node[2])
    
    elif node[0] in ('soustraction', 'moins_affectation'):
      return self.parcourir(node[1]) - self.parcourir(node[2])
    
    elif node[0] in ('multiplication', 'multiplie_affectation'):
      return self.parcourir(node[1]) * self.parcourir(node[2])
    
    elif node[0] in ('division', 'divise_affectation'):
      return self.parcourir(node[1]) / self.parcourir(node[2])
    
    elif node[0] in ('modulo', 'modulo_affectation'):
      return self.parcourir(node[1]) % self.parcourir(node[2])
    
    elif node[0] == 'puissance':
      return self.parcourir(node[1]) ** self.parcourir(node[2])
    
    elif node[0] == 'moins':
      return -self.parcourir(node[1])
    
    ############################## LOGIQUE ET BINAIRE ###############################
    
    elif node[0] == 'non':
      return not self.parcourir(node[1])
    
    elif node[0] == 'et':
      return self.parcourir(node[1]) and self.parcourir(node[2])
    
    elif node[0] == 'ou':
      return self.parcourir(node[1]) or self.parcourir(node[2])
    
    elif node[0] == 'ouex':
      return self.parcourir(node[1]) ^ self.parcourir(node[2]) 
    
    #################################################################################
    
    else:
      print("Erreur d'exécution") # par précaution mais ne doit jamais arriver
      
  ###################################################################################
  #                                FONCTIONS NATIVES                                #
  ###################################################################################
  
  # affiche une liste d'objets
  # AFFICHER(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet...)
  def affiche(self, args):
    for objet in args:
      print(objet, end='') # ne passe pas à la ligne
    if not args or (args and args[-1] != ''): # pour passer à la ligne / ajouter '' pour ne pas passer à la ligne
      print()
  
  # renvoie l'arrondi inférieur d'un nombre
  # ARRI(<NOMBRE> nombre)
  def arri(self, args):
    try:
      return math.floor(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: ARRI(<NOMBRE> nombre)")
      
  # renvoie l'arrondi supérieur d'un nombre
  # ARRS(<NOMBRE> nombre)
  def arrs(self,args):
    try:
      return math.ceil(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: ARRS(<NOMBRE> nombre)")
      
  # renvoie la valeur booléenne d'un objet
  # BOOLEEN(<CHAINE|NOMBRE|BOOLEEN|LISTE> objet)
  def boolf(self, args):
    try:
      return bool(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: BOOLEEN(<CHAINE|NOMBRE|BOOLEEN|LISTE> objet)")
      
  # charge du code franterprète à partir de fichiers et renvoie les résultats de leur exécution
  # CEXE(<CHAINE|NOMBRE|VIDE> fichier...)
  def cexe(self, args):
    try:
      return self.exe(self.charger(args))
    except (IndexError, TypeError):
      print("Fonction usage: CEXE(<CHAINE|NOMBRE|VIDE> fichier...)")
      
  # convertit un objet en chaîne
  # CHAINE(<CHAINE|NOMBRE|BOOLEEN|LISTE> objet)
  def chainef(self, args):
    try:
      return str(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: CHAINE(<CHAINE|NOMBRE|BOOLEEN|LISTE> objet)")
      
  # renvoie le contenu des fichiers renseignés
  # CHARGER(<CHAINE|NOMBRE|VIDE> fichier...)
  def charger(self, args):
    try:
      resultat = []
      for fichier in args:
        with open(fichier, 'r') as f:
          resultat.append(f.read())
      return resultat
    except (IndexError, TypeError):
      print("Fonction usage: CHARGER(<CHAINE|NOMBRE|VIDE> fichier...)")
    except FileNotFoundError:
      print(f"'{fichier}' n'existe pas")
    except PermissionError:
      print(f"'{fichier}' : permission refusée")
    except IsADirectoryError:
      print(f"'{fichier}' est un répertoire")
    except UnicodeDecodeError:
      print(f"'{fichier}' : erreur de décodage Unicode")
    except OSError as e:
      print(f"Erreur d'E/S ou erreur liée au système d'exploitation : {e}")
      
  # charge, affiche et renvoie le contenu des fichiers renseignés
  # CLIRE(<CHAINE|NOMBRE|VIDE> fichier...)
  def clire(self, args):
    try:
      contenus = self.charger(args)
      self.affiche(contenus)
      return contenus
    except (IndexError, TypeError):
      print("Fonction usage: CLIRE(<CHAINE|NOMBRE|VIDE> fichier...)")
      
  # change le répertoire courant
  # un nombre indique un descripteur de fichier
  # CR(<CHAINE|NOMBRE> répertoire)
  def cr(self, args):
    try:
      os.chdir(str(args[0]))
    except FileNotFoundError:
      print("Le répertoire spécifié n'existe pas")
    except NotADirectoryError:
      print("Le chemin spécifié n'est pas un répertoire")
    except PermissionError:
      print("Vous n'avez pas les permissions nécessaires pour accéder au répertoire spécifié")
    except (IndexError, TypeError):
      print("CR(<CHAINE|NOMBRE> répertoire)")
    
  # écrit dans un fichier
  # réutilise les mêmes modes d'ouverture que Python
  # ECRIRE(<CHAINE> fichier, <CHAINE> mode, <CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> contenu_à_écrire...)
  def ecrire(self, args):
    try:
      with open(args[0], args[1]) as f:
        for contenu in args[2:]:
          f.write(str(contenu))
      return args[2:]
    except (IndexError, TypeError):
      print("Fonction usage: ECRIRE(<CHAINE> fichier, <CHAINE> mode, <CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> contenu_à_écrire...)")
    except FileNotFoundError:
      print(f"'{args[0]}' n'existe pas")
    except PermissionError:
      print(f"'{args[0]}' : permission refusée")
    except IsADirectoryError:
      print(f"'{args[0]}' est un répertoire")
    except UnicodeDecodeError:
      print(f"'{args[0]}' : erreur de décodage Unicode")
    except FileExistsError:
      print(f"'{args[0]}' existe déjà.'")
    except ValueError:
      print(f"'{args[0]}' n’est pas ouvert en mode écriture")
    except UnicodeEncodeError:
      print(f"'{args[0]}' : erreur d’encodage Unicode'")
    except OSError as e:
      print(f"Erreur d'E/S ou erreur liée au système d'exploitation : {e}")
      
  # exécute du code franterprète et renvoie les résultats
  # le code est exécuté dans le même environnement et non dans
  # une nouvelle instance de la classe FranterpreteInterpreter
  # EXECUTER(<CHAINE|VIDE> suite_instructions...)
  def exe(self, args):
    lexer = FranterpreteLexer()
    parser = FranterpreteParser()
    resultat = []
    for programme in args:
      resultat.append(self.execute(parser.parse(lexer.tokenize(programme))))
    return resultat
  
  # vérifie le type d'un objet
  # INSTANCE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet, <CHAINE> type)
  def instance(self,args):
    try:
      if args[1] == 'no':
        return isinstance(args[0], (int, float))
      elif args[1] == 'ch':
        return isinstance(args[0], str)
      elif args[1] == 'bo':
        return isinstance(args[0], bool)
      elif args[1] == 'ta' or args[1] == 'li':
        return isinstance(args[0], list)
      print("Instance '" + args[1] + "' invalide")
    except (IndexError, TypeError):
      print("Fonction usage: INSTANCE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet, <CHAINE> type)")
          
  # affiche le contenu de fichiers renseignés
  # ouvre avec le mode 'r' de Python
  # LIRE(<CHAINE|NOMBRE|VIDE> fichier...)
  def lire(self, args):
    try:
      for fichier in args:
        with open(fichier, 'r') as f:
          print(f.read())
    except (IndexError, TypeError):
      print("Fonction usage: LIRE(<CHAINE|NOMBRE|VIDE> fichier...)")
    except FileNotFoundError:
      print(f"'{fichier}' n'existe pas")
    except PermissionError:
      print(f"'{fichier}' : permission refusée")
    except IsADirectoryError:
      print(f"'{fichier}' est un répertoire")
    except UnicodeDecodeError:
      print(f"'{fichier}' : erreur de décodage Unicode")
    except OSError as e:
      print(f"Erreur d'E/S ou erreur liée au système d'exploitation : {e}")
      
  # renvoie la longueur d'une chaine ou d'une liste
  # TAILLE(<CHAINE|LISTE> objet)
  def longueur(self, args):
    try:
      return len(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: TAILLE(<CHAINE|LISTE> objet)")
      
  # convertit en chaine une liste d'objets puis la met en majuscule
  # MAJUSCULE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet)
  def majuscule(self, args):
    try:
      texte = ''
      for objet in args:
        texte += str(objet)
      return texte.upper()
    except (IndexError, TypeError):
      print("Fonction usage: MAJUSCULE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet)")
      
  # convertit en chaine une liste d'objets puis la met en minuscule
  # MINUSCULE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet)
  def minuscule(self, args):
    try:
      texte = ''
      for objet in args:
        texte += str(objet)
      return texte.lower()
    except (IndexError, TypeError):
      print("Fonction usage: MINUSCULE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet)")
    
  # convertit une chaine en nombre
  # NOMBRE(<CHAINE> nombre)
  def nombref(self, args):
    try:
      return float(args[0]) if ('.' in args[0]) else int(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: NOMBRE(<CHAINE> nombre)")
    except ValueError:
      print("'" + str(args[0]) + "' n'est pas un nombre valide")
  
  # permet à l'utilisateur de saisir du texte avec un prompt
  # SAISIR(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet...)
  def saisir(self, args):
    for objet in args: # affiche le prompt
      print(objet, end='') # ne passe pas à la ligne
    return input()
  
  # convertit un objet en tableau / liste
  # LISTE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet...)
  def tableau(self, args):
    try:
      return list(args)
    except (IndexError, TypeError):
      print("Fonction usage: LISTE(<CHAINE|NOMBRE|BOOLEEN|LISTE|VIDE> objet...)")
      
  # trie une liste de chaines ou une liste de nombres
  # TRIER(<LISTE <CHAINE|VIDE||NOMBRE|VIDE>> liste)
  def trier(self, args):
    try:
      return sorted(args[0])
    except (IndexError, TypeError):
      print("Fonction usage: TRIER(<LISTE <CHAINE|VIDE||NOMBRE|VIDE>> liste)")
      
