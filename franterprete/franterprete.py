#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : franterprete.py
  Rôle ........ : interpréteur en français inspiré du langage C et de Python
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 05/11/2023
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : ./franterprete.py
'''

from .franterprete_input import FranterpreteInput # gère les saisies
from .franterprete_lexer import FranterpreteLexer
from .franterprete_parser import FranterpreteParser
from .franterprete_interpreter import FranterpreteInterpreter

#####################################################################################
#                                        MAIN                                       #
#####################################################################################

def main():
  finput = FranterpreteInput() # gère la saisie
  lexer = FranterpreteLexer()
  parser = FranterpreteParser()
  interpreter = FranterpreteInterpreter() # crée l'environnement d'exécution
  print('Bienvenue dans le Franterprète !')
  while True: # prompt
    try:
      saisie = finput.get_saisie()
      if saisie: # à chaque saisie:
        if saisie == 'QUITTER': break # commande de sortie du programme
        arbre = parser.parse(lexer.tokenize(saisie)) # contruit l'arbre syntaxique
        while not arbre: # tant que saisie incomplète alors complète
          saisie = finput.get_saisie_multilignes()
          arbre = parser.parse(lexer.tokenize(saisie))
        interpreter.execute(arbre)
    except EOFError: # Ctrl+D stoppe le prompt
      print() # pour la lisibilité
      break
    except (Exception, KeyboardInterrupt) as e: # erreur ou Ctrl+C, passe à une nouvelle saisie
      interpreter.clear() # vide les postIntructions et revient à l'environnement global
      print(e) # affiche erreur ou passe à une nouvelle ligne
  print('À bientôt !')

if __name__ == '__main__':
  main()
