#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : franterprete_lexer.py
  Rôle ........ : lexeur du franterprete
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 05/11/2023
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : ./franterprete_lexer.py
'''

from .franterprete_input import FranterpreteInput # gère les saisies
from sly import Lexer

#####################################################################################
#                                       LEXER                                       #
#####################################################################################

class FranterpreteLexer(Lexer):
  tokens = { 
            DEBLOC, FINBLOC,
            DECALG, DECALD,
            INCREMENTE, DECREMENTE,
            PLUSAFFECTE, MOINSAFFECTE, MULTIPLIEAFFECTE, DIVISEAFFECTE, MODULOAFFECTE,
            EGAL, DIFFERENT, SUPERIEUREGAL, INFERIEUREGAL, SUPERIEUR, INFERIEUR,
            AFFECTE, DANS,
            NON, ET, OUEX, OU,
            PLUS, MOINS, PUISSANCE, MULTIPLIE, DIVISE, MODULO,
            SINON, SI,
            SELON, CAS, AUTREMENT,
            POUR, CHAQUE,
            TANTQUE,
            REPETER, JUSQUA,
            INTERROMPRE, CONTINUER,
            FONCTION, RETOURNER, FONCTIONS_NATIVES,
            BOOLEEN, NOMBRE, CHAINE, VIDE,
            PUIS, FIN, GLOBALE, NOM,
          }
  
  ignore = ' \t\r\f\v' # ignore caractères d'espacement
  
  literals = { '(', ')', '{', '}', '[', ']', ',' }
  
  ###################################### BLOCS ######################################
  
  # commentaires mono-ligne ou multi-lignes de type C++ et Python
  @_(r'(\/\/.*)|(\/\*[\s\S]*?\*\/)|#.*|\'\'\'[\s\S]*?\'\'\'|\"\"\"[\s\S]*?\"\"\"')
  def COMMENTAIRES(self, t):
    self.lineno += t.value.count('\n') # compte lignes => utile pour débogage par exemple (évolution possible)
    pass # ignore les commentaires
    
  DEBLOC = r'ALORS|:' # caractères de début de bloc d'exécution
  FINBLOC = r'\§|\$' # caractères de fin de bloc d'exécution
  
  #################################### OPÉRATEURS ###################################
  
  # décalage de bits
  DECALG = r'<<|DECALG'
  DECALD = r'>>|DECALD'
  
  # incrémentation / décrémentation
  INCREMENTE = r'\+\+|INC(REMENTE)?'
  DECREMENTE = r'--|DEC(REMENTE)?'
  
  # arithmétique avec affectation
  PLUSAFFECTE = r'\+=|PLUS(_)?A(FFECTE)?|PLUS(_)?EG(AL)?'
  MOINSAFFECTE = r'-=|MOINS(_)?A(FFECTE)?|MOINS(_)?EG(AL)?'
  MULTIPLIEAFFECTE = r'\*=|MULT(IPLIE)?(_)?A(FFECTE)?|MULT(IPLI)?(_)?EG(AL)?'
  DIVISEAFFECTE = r'/=|DIV(ISE)?(_)?A(FFECTE)?|DIV(IS)?(_)?EG(AL)?'
  MODULOAFFECTE = r'%=|MOD(ULO)?(_)?A(FFECTE)?|MOD(ULO)?(_)?EG(AL)?'
  
  # comparaison
  EGAL = r'==|EG(AL(E)?)?'
  DIFFERENT = r'!=|<>|DIFF(ERENT)?((_)?DE)?|PAS(_)?EG(AL(E)?)?((_)?A)?|PA(S)?(_)?DANS|EST(_)?PAS|VAU(T)?(_)?PAS'
  SUPERIEUREGAL = r'>=|SUPE(RIEUR)?((_)?OU)?((_)?E)?G(AL)?((_)?A)?'
  INFERIEUREGAL = r'<=|INFE(RIEUR)?((_)?OU)?((_)?E)?G(AL)?((_)?A)?'
  SUPERIEUR = r'>|SUP(ERIEUR)?((_)?A)?'
  INFERIEUR = r'<|INF(ERIEUR)?((_)?A)?'
  
  # affectation
  AFFECTE = r'=|VAUT|EST'
  DANS = r'->|DANS' # sert aussi pour structure de répétition POUR CHAQUE ... DANS ...
  
  # logique et binaire
  NON = r'!|NON|PAS'
  ET = r'&&|ET'
  OUEX = r'\^\^|OUEX'
  OU = r'\|\||OU'
  
  # arithmétique
  PLUS = r'\+|PLUS'
  MOINS = r'-|MOINS'
  PUISSANCE = r'\^|\*\*|PUISS(ANCE)?'
  MULTIPLIE = r'\*|FOIS|MULT(IPLIE)?((_)?PAR)?'
  DIVISE = r'/|DIV(ISE)?((_)?PAR)?'
  MODULO = r'%|MOD(ULO)?'
  
  ############################### STRUCTURES DE CHOIX ###############################
  
  # si...alors...sinon
  SINON = r'SINON'
  SI = r'SI'
  
  # switch
  SELON = r'SELON'
  CAS = r'CAS'
  AUTREMENT = r'AUTRE(MENT)?'
  
  ############################ STRUCTURES DE RÉPÉTITIONS ############################
  
  # instructions de contrôle
  CONTINUER = r'CONT(INUE(R)?)?|POURS(UIVRE)?'
  INTERROMPRE = r'INTER(ROMPRE)?|STOP(PE(R)?)?'
  
  # boucle for
  POUR = r'POUR'
  CHAQUE = r'CHAQUE'
  
  # boucle while
  TANTQUE = r'TAN(T)?(_)?QUE'
  
  # boucle do...while
  REPETER = r'REP(ETE(R)?)?|FAIRE|FAIS'
  JUSQUA = r'JUSQU(\')?A'
    
  #################################### FONCTIONS ####################################
  
  FONCTION = r'FONC(TION)?|DEF(INITION)?'
  RETOURNER = r'RET(OUR(NE(R)?)?)?'
  
  # fonctions natives du franterprète
  @_(r'AFF(ICHE(R)?)?|IMP(RIME(R)?)?|ARR(ONDI)?(_)?I(NF(ERIEUR)?)?|ARR(ONDI)?(_)?S(UP(ERIEUR)?)?|BOOL(EEN)?|(C)?EXE(CUTE(R)?)?|CHAI(NE)?|CHARGE(R)?|(C)?LIRE|CR|ECRIRE|ECRIS|LIS(TE)?|INST(ANCE)?|TYPE|GRAND(EUR)?|LONG(UEUR)?|SAISIR|TAILLE|MAJ(USCULE)?|MIN(USCULE)?|NOMB(RE)?|TAB(LEAU)?|TRI((E)?R)?')
  def FONCTIONS_NATIVES(self, t):
    if t.value[:3] in ('AFF', 'IMP'):
      t.value = 'AFFICHER'
    elif t.value[:4] == 'ARRI' or t.value[:8] == 'ARRONDII':
      t.value = 'ARRI'
    elif t.value[:4] == 'ARRS' or t.value[:8] == 'ARRONDIS':
      t.value = 'ARRS'
    elif t.value[:4] == 'BOOL':
      t.value = 'BOOLF'
    elif t.value[:4] == 'CEXE':
      t.value = 'CEXECUTER'
    elif t.value[:4] == 'CHAI':
      t.value = 'CHAINEF'
    elif t.value[:6] == 'CHARGE':
      t.value = 'CHARGER'
    elif t.value[:4] == 'ECRI':
      t.value = 'ECRIRE'
    elif t.value[:3] == 'EXE':
      t.value = 'EXECUTER'
    elif t.value in ('LIS', 'LIRE'):
      t.value = 'LIRE'
    elif t.value[:4] in ('INST', 'TYPE'):
      t.value = 'INSTANCE'
    elif t.value[:4] in ('GRAN', 'LONG', 'TAIL'):
      t.value = 'LONGUEUR'
    elif t.value[:3] == 'MAJ':
      t.value = 'MAJUSCULE'
    elif t.value[:3] == 'MIN':
      t.value = 'MINUSCULE'
    elif t.value[:4] == 'NOMB':
      t.value = 'NOMBREF'
    elif t.value[:3] in ('TAB', 'LIS'):
      t.value = 'TABLEAU'
    elif t.value[:3] == 'TRI':
      t.value = 'TRIER'
    return t
  
  ###################################### TYPES ######################################
  
  # booléen
  @_(r'VRAI|FAUX')
  def BOOLEEN(self, t):
    if t.value == 'VRAI':
      t.value = True
    else:
      t.value = False
    return t
  
  # chaînes encadrées
  # soit par des guillemets doubles (")
  # soit par des guillemets simples (')
  @_(r'\"[^\"]*\"|\'[^\']*\'')
  def CHAINE(self, t):
    # enlève guillemets
    # réencode en iso-8859-15 pour encodage sur un octet (notamment caractères non-ASCII)
    # convertit séquences d'échappement ('\n', '\t' par exemple)
    t.value = t.value[1:-1].encode('iso-8859-15').decode('unicode_escape')
    return t
    
  # nombres positifs ou négatifs, entiers ou flottants
  @_(r'-?\d+(\.\d+)?')
  def NOMBRE(self, t):
    if '.' in t.value: # si le token a un point (partie décimale)
      t.value = float(t.value) # alors le convertir en float
    else:
      t.value = int(t.value) # sinon le convertir en int
    return t
  
  # vide
  @_(r'°|AUCUN|VIDE|RIEN|NUL(LE)?')
  def VIDE(self, t):
    t.value = None
    return t
  
  ###################################################################################
  
  PUIS = r';|PUIS' # séparateur d'instructions
  
  # instruction d'arrêt d'une suite d'instructions
  FIN = r'FINIS|FIN(IR)?|TERM(INE(R)?)?|ARRE(TE(R)?)?'
  
  # uniquement pour affecter des variables existantes en-dehors d'une fonction
  GLOBALE = r'GLOB(ALE)?'
  
  # variables ou fonctions commençant par
  # une lettre (majuscule ou minuscule) ou un underscore (_),
  # suivies de zéro ou plusieurs lettres, chiffres ou underscores
  NOM = r'[a-zA-Z_][a-zA-Z0-9_]*'
  
  # compte lignes => utile pour débogage par exemple (évolution possible)
  @_(r'\n+')
  def newlines(self,t):
    self.lineno += t.value.count('\n')
    
#####################################################################################
#                                        MAIN                                       #
#####################################################################################

# pour tester
if __name__ == '__main__':
  finput = FranterpreteInput() # gère la saisie
  lexer = FranterpreteLexer()
  while True: # prompt
    try:
      saisie = finput.get_saisie()
      if saisie: # à chaque saisie:
        lex = lexer.tokenize(saisie) # récupère les tokens
        for token in lex: # affiche les tokens
          print(token)
        print(f'lineno = {lexer.lineno}') # affiche le nombre total de lignes
    except EOFError: # Ctrl+D stoppe le prompt
      print() # pour la lisibilité
      break
    except (Exception, KeyboardInterrupt) as e: # erreur ou Ctrl+C, passe à une nouvelle saisie
      print(e) # affiche erreur ou passe à une nouvelle ligne
