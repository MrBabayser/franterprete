#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : franterprete_input.py
  Rôle ........ : gestion de la saisie du franterprete
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 05/11/2023
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : ./franterprete_input.py
'''

import os # récupère login et chemin du répertoire courant
from colorama import init, Fore, Style # colorise le prompt
from pynput import keyboard # écoute saisie clavier
import readline # historique des saisies

# gestion de la saisie du franterprète
class FranterpreteInput:
  
  # constructeur
  def __init__(self):
    self.listener = None
    self.shift_pressed = False # indique si Maj est enfoncée
    self.ctrl_pressed = False # indique si Ctrl est enfoncée
    self.multi_line = False # indique si mode multi-lignes
    self.saisie = None # facilement modifiable et récupérable
    self.noligne = 1
  
  # démarre l'écoute du clavier
  def ecoute_clavier(self):
    self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release) # charge l'écouteur
    self.listener.start() # démarre l'écouteur
  
  # quand une touche est enfoncée
  def on_press(self, key):
    if key == keyboard.Key.shift: # si Maj est enfoncée
      self.shift_pressed = True
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r: # si Ctrl est enfoncée
      self.ctrl_pressed = True
    elif self.ctrl_pressed and key == keyboard.Key.enter: # si Ctrl+Entrée sont enfoncées
      self.multi_line = not self.multi_line # switch mode multi-lignes
  
  # quand une touche est relachée
  def on_release(self, key):
    if key == keyboard.Key.shift: # si Maj est relachée
      self.shift_pressed = False
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r: # si Ctrl est relachée
      self.ctrl_pressed = False
  
  # récupère saisie
  def get_saisie(self):
    self.ecoute_clavier() # démarre l'écouteur
    self.noligne = 1
    self.saisie = input(Style.BRIGHT + Fore.GREEN + os.getlogin() + Fore.WHITE + ':' + Fore.BLUE + os.getcwd() + Fore.WHITE + ' 1> ' + Style.NORMAL) # prompt
    self.listener.stop() # arrête l'écouteur
    while self.shift_pressed or self.multi_line: # tant que Maj est enfoncée ou que mode multi-lignes activé
      self.get_saisie_multilignes() # récupère la saisie des lignes suivantes
    return self.saisie
  
  # récupère la saisie sur plusieurs lignes
  def get_saisie_multilignes(self):
    self.ecoute_clavier() # démarre l'écouteur
    self.noligne += 1
    self.saisie += '\n' + input(Style.BRIGHT + f'{self.noligne}> ' + Style.NORMAL) # prompt
    self.listener.stop() # arrête l'écouteur
    return self.saisie
    
# pour tester
if __name__ == '__main__':
  finput = FranterpreteInput()
  while True: # prompt
    try:
      saisie = finput.get_saisie()
      if saisie:
        print(saisie)
    except KeyboardInterrupt: # Ctrl+C passe à une nouvelle saisie
      print() # pour la lisibilité
    except EOFError: # Ctrl+D stoppe le prompt
      print() # pour la lisibilité
      break
