#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : franterprete_parser.py
  Rôle ........ : parseur du franterprete
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 05/11/2023
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : ./franterprete_parser.py
'''

from .franterprete_input import FranterpreteInput # gère les saisies
from .franterprete_lexer import FranterpreteLexer
from sly import Parser

#####################################################################################
#                                       PARSER                                      #
#####################################################################################

class FranterpreteParser(Parser):
  
  # pour débuguer la grammaire au besoin
  # debugfile = 'grammaire.txt'
  
  tokens = FranterpreteLexer.tokens
  
  # précédence inspirée du C
  precedence = (
    ('left', OU),
    ('left', ET),
    ('left', OUEX),
    ('left', EGAL, DIFFERENT), # opérateurs d'égalité
    ('left', INFERIEUR, INFERIEUREGAL, SUPERIEUR, SUPERIEUREGAL), # opérateurs relationnels
    ('left', DECALG, DECALD), # opérateurs de décalage de bits
    ('left', PLUS, MOINS),  # opérateurs additifs
    ('left', MULTIPLIE, DIVISE, MODULO), # opérateurs multiplicatifs
    ('right', NON, MOINSU), # opérateurs unaires
    ('left', INCG, DECG), # opérateurs d'incrémentation gauche
    ('right', INCD, DECD), # opérateurs d'incrémentation droite
    ('right', PUISSANCE),
  )
  
  # toute saisie est une suite d'instructions
  @_('suite_instructions')
  def start(self, p):
    return p.suite_instructions
  
  ###################################################################################
  #                                       BLOC                                      #
  ###################################################################################
  
  # bloc pour les fonctions, structures de choix et structures de répétitions
  @_('DEBLOC suite_instructions FINBLOC', 
     '"{" suite_instructions "}"')
  def bloc(self, p):
    return p.suite_instructions
  
  ###################################################################################
  #                                   INSTRUCTIONS                                  #
  ###################################################################################
  
  @_('instruction')
  def suite_instructions(self, p):
    return 'instruction', p.instruction
  
  @_('instruction PUIS suite_instructions')
  def suite_instructions(self, p):
    return 'suite_instructions', p.instruction, p.suite_instructions
  
  # stoppe une suite d'instructions et renvoie une valeur
  @_('FIN "(" expression ")"')
  def instruction(self, p):
    return 'fin', p.expression
  
  ############################## DÉCLARATION FONCTION ###############################
  
  @_('FONCTION NOM "(" liste_parametres ")" bloc')
  def instruction(self, p):
    return 'declaration_fonction', ('chaine', p.NOM), p.liste_parametres, p.bloc
  
  @_('NOM')
  def liste_parametres(self, p):
    return 'parametre', ('chaine', p.NOM)
  
  @_('NOM "," liste_parametres')
  def liste_parametres(self, p):
    return 'liste_parametres', ('chaine', p.NOM), p.liste_parametres
  
  @_('')
  def liste_parametres(self, p):
    return 'parametre', ('chaine', None) # liste vide pour l'interpréteur
  
  @_('RETOURNER expression')
  def instruction(self, p):
    return 'retourner', p.expression
  
  ####################################### SI ########################################
  
  @_('SI expression_non_vide bloc')
  def instruction(self, p):
    return 'si', p.expression_non_vide, p.bloc
  
  @_('SI expression_non_vide bloc SINON bloc')
  def instruction(self, p):
    return 'si_sinon', p.expression_non_vide, p.bloc0, p.bloc1
  
  ###################################### SWITCH #####################################
  
  @_('SELON expression_non_vide DEBLOC suite_cas FINBLOC', 
     'SELON expression_non_vide "{" suite_cas "}"')
  def instruction(self, p):
    return 'switch', p.expression_non_vide, p.suite_cas
  
  @_('CAS expression_non_vide bloc suite_cas')
  def suite_cas(self, p):
    return 'cas', p.expression_non_vide, p.bloc, p.suite_cas
  
  @_('AUTREMENT bloc')
  def suite_cas(self, p):
    return 'autrement', p.bloc
  
  @_('')
  def suite_cas(self, p):
    pass
  
  ###################################### POUR #######################################
  
  # expression0 et expression2 sont à traiter comme des instructions dans l'interpréteur
  @_('POUR "(" expression PUIS expression PUIS expression ")" bloc')
  def instruction(self, p):
    return 'pour', ('instruction', p.expression0), p.expression1, ('instruction', p.expression2), p.bloc
  
  @_('POUR CHAQUE NOM DANS expression_iterable bloc')
  def instruction(self, p):
    return 'pour_chaque', p.NOM, p.expression_iterable, p.bloc
  
  ##################################### TANTQUE #####################################
  
  @_('TANTQUE expression_non_vide bloc')
  def instruction(self, p):
    return 'tantque', p.expression_non_vide, p.bloc
  
  ##################################### RÉPÉTER #####################################
  
  @_('REPETER bloc TANTQUE expression_non_vide', 
     'REPETER bloc JUSQUA expression_non_vide')
  def instruction(self, p):
    return 'repeter', p.bloc, p.expression_non_vide
  
  ####################### CONTRÔLE STRUCTURES DE RÉPÉTITIONS ########################
  
  @_('CONTINUER')
  def instruction(self, p):
    return 'continuer', None
  
  @_('INTERROMPRE')
  def instruction(self, p):
    return 'interrompre', None
  
  ################################### EXPRESSION ####################################
  
  @_('expression')
  def instruction(self, p):
    return p.expression
  
  ###################################################################################
  #                                   EXPRESSIONS                                   #
  ###################################################################################
  
  @_('')
  def expression(self, p):
    pass
  
  @_('affectation')
  def expression(self, p):
    return 'affectation', p.affectation
  
  @_('expression_non_vide')
  def expression(self, p):
    return p.expression_non_vide
  
  # gestion des parenthèses pour la précédence des opérations
  @_(' "(" expression_non_vide ")" ')
  def expression_non_vide(self, p):
    return p.expression_non_vide
  
  #################################### ITÉRABLE #####################################
  
  @_('expression_iterable')
  def expression_non_vide(self, p):
    return p.expression_iterable
  
  @_('NOM')
  def expression_iterable(self, p):
    return 'nom', p.NOM
  
  @_('tableau')
  def expression_iterable(self, p):
    return p.tableau
  
  @_('acces_tableau')
  def expression_iterable(self, p):
    return p.acces_tableau
  
  ##################################### TABLEAU #####################################
  
  @_('"[" liste_expressions "]"')
  def tableau(self, p):
    return 'tableau', p.liste_expressions
  
  @_('NOM liste_indices')
  def acces_tableau(self, p):
    return 'acces_tableau', ('nom', p.NOM), p.liste_indices
  
  @_('"[" expression "]"')
  def liste_indices(self, p):
    return 'indice', p.expression
  
  @_('"[" expression "]" liste_indices')
  def liste_indices(self, p):
    return 'liste_indices', p.expression, p.liste_indices
  
  ################################### AFFECTATION ###################################
  
  @_('NOM')
  def emplacement(self, p):
    return 'nom', p.NOM, None
  
  @_('GLOBALE NOM')
  def emplacement(self, p):
    return 'nom', p.NOM, 'globale'
  
  @_('acces_tableau')
  def emplacement(self, p):
    return p.acces_tableau
  
  @_('emplacement AFFECTE expression_non_vide', 
     'expression_non_vide DANS emplacement')
  def affectation(self, p):
    return 'egal_affectation', p.emplacement, p.expression_non_vide
  
  @_('emplacement PLUSAFFECTE expression_non_vide')
  def affectation(self, p):
    return 'plus_affectation', p.emplacement, p.expression_non_vide
  
  @_('emplacement MOINSAFFECTE expression_non_vide')
  def affectation(self, p):
    return 'moins_affectation', p.emplacement, p.expression_non_vide
  
  @_('emplacement MULTIPLIEAFFECTE expression_non_vide')
  def affectation(self, p):
    return 'multiplie_affectation', p.emplacement, p.expression_non_vide
  
  @_('emplacement DIVISEAFFECTE expression_non_vide')
  def affectation(self, p):
    return 'divise_affectation', p.emplacement, p.expression_non_vide
  
  @_('emplacement MODULOAFFECTE expression_non_vide')
  def affectation(self, p):
    return 'modulo_affectation', p.emplacement, p.expression_non_vide
  
  ################################# DÉCALAGE DE BITS ################################
  
  @_('expression_non_vide DECALG expression_non_vide')
  def expression_non_vide(self, p):
    return 'decalg', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide DECALD expression_non_vide')
  def expression_non_vide(self, p):
    return 'decald', p.expression_non_vide0, p.expression_non_vide1
  
  ######################### INCRÉMENTATION / DÉCRÉMENTATION #########################
  
  @_('NOM INCREMENTE %prec INCG')
  def expression_non_vide(self, p):
    return 'incg', ('nom', p.NOM)
  
  @_('INCREMENTE NOM %prec INCD')
  def expression_non_vide(self, p):
    return 'incd', ('nom', p.NOM)
  
  @_('NOM DECREMENTE %prec DECG')
  def expression_non_vide(self, p):
    return 'decg', ('nom', p.NOM)
  
  @_('DECREMENTE NOM %prec DECD')
  def expression_non_vide(self, p):
    return 'decd', ('nom', p.NOM)
  
  ################################### COMPARAISON ###################################
  
  @_('expression_non_vide EGAL expression_non_vide')
  def expression_non_vide(self, p):
    return 'egal', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide DIFFERENT expression_non_vide')
  def expression_non_vide(self, p):
    return 'different', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide SUPERIEUR expression_non_vide')
  def expression_non_vide(self, p):
    return 'superieur', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide INFERIEUR expression_non_vide')
  def expression_non_vide(self, p):
    return 'inferieur', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide SUPERIEUREGAL expression_non_vide')
  def expression_non_vide(self, p):
    return 'superieuregal', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide INFERIEUREGAL expression_non_vide')
  def expression_non_vide(self, p):
    return 'inferieuregal', p.expression_non_vide0, p.expression_non_vide1
  
  ################################## ARITHMÉTIQUE ###################################
  
  @_('expression_non_vide PLUS expression_non_vide')
  def expression_non_vide(self, p):
    return 'addition', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide MOINS expression_non_vide')
  def expression_non_vide(self, p):
    return 'soustraction', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide MULTIPLIE expression_non_vide')
  def expression_non_vide(self, p):
    return 'multiplication', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide DIVISE expression_non_vide')
  def expression_non_vide(self, p):
    return 'division', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide MODULO expression_non_vide')
  def expression_non_vide(self, p):
    return 'modulo', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide PUISSANCE expression_non_vide')
  def expression_non_vide(self, p):
    return 'puissance', p.expression_non_vide0, p.expression_non_vide1
  
  @_('MOINS expression_non_vide %prec MOINSU')
  def expression_non_vide(self, p):
    return 'moins', p.expression_non_vide
  
  ############################### LOGIQUE ET BINAIRE ################################
  
  @_('NON expression_non_vide')
  def expression_non_vide(self, p):
    return 'non', p.expression_non_vide
  
  @_('expression_non_vide ET expression_non_vide')
  def expression_non_vide(self, p):
    return 'et', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide OU expression_non_vide')
  def expression_non_vide(self, p):
    return 'ou', p.expression_non_vide0, p.expression_non_vide1
  
  @_('expression_non_vide OUEX expression_non_vide')
  def expression_non_vide(self, p):
    return 'ouex', p.expression_non_vide0, p.expression_non_vide1
  
  #################################### FONCTION #####################################
  
  @_('NOM "(" liste_expressions ")"')
  def expression_non_vide(self, p):
    return 'appel_fonction', p.NOM, p.liste_expressions
  
  @_('FONCTIONS_NATIVES "(" liste_expressions ")"')
  def expression_non_vide(self, p):
    return 'appel_fonction', p.FONCTIONS_NATIVES, p.liste_expressions
  
  ###################################### LISTE ######################################
  
  @_('expression')
  def liste_expressions(self, p):
    return 'expression', p.expression
  
  @_('expression "," liste_expressions')
  def liste_expressions(self, p):
    return 'liste_expressions', p.expression, p.liste_expressions
  
  ###################################### TYPES ######################################
  
  @_('BOOLEEN')
  def expression_non_vide(self, p):
    return 'booleen', p.BOOLEEN
  
  @_('CHAINE')
  def expression_iterable(self, p):
    return 'chaine', p.CHAINE
  
  @_('NOMBRE')
  def expression_non_vide(self, p):
    return 'nombre', p.NOMBRE
  
  @_('VIDE')
  def expression_non_vide(self, p):
    return 'vide', p.VIDE
  
#####################################################################################
#                                        MAIN                                       #
#####################################################################################

# pour tester
if __name__ == '__main__':
  finput = FranterpreteInput() # gère la saisie
  lexer = FranterpreteLexer()
  parser = FranterpreteParser()
  while True: # prompt
    try:
      saisie = finput.get_saisie()
      if saisie: # à chaque saisie:
        arbre = parser.parse(lexer.tokenize(saisie)) # contruit l'arbre syntaxique
        while not arbre: # tant que saisie incomplète alors complète
          saisie = finput.get_saisie_multilignes()
          arbre = parser.parse(lexer.tokenize(saisie))
        print(arbre)
    except EOFError: # Ctrl+D stoppe le prompt
      print() # pour la lisibilité
      break
    except (Exception, KeyboardInterrupt) as e: # erreur ou Ctrl+C, passe à une nouvelle saisie
      print(e) # affiche erreur ou passe à une nouvelle ligne
