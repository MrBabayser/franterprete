#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
  Nom ......... : setup.py
  Rôle ........ : installateur du franterprète
  Auteur ...... : Georges Miot
  Version ..... : V1.0 du 27/02/2024
  Licence ..... : réalisé dans le cadre du cours de I&C
  Exécution ... : pip install -e .
'''

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
name='franterprete', # nom du paquet
version='1.0.0', # version du paquet
packages=find_packages(), # détecte automatiquement tous les paquets à inclure grâce à __init__.py
install_requires=[ # liste des dépendances nécessaires à l'installation de ce paquet
'sly==0.5',
'pynput==1.7.6',
'colorama==0.4.4',
],
url='https://github.com/MrBabayser/franterprete',
license='GNU General Public License v3.0',
author='Georges Miot',
description='A french programming language created with the SLY library',
long_description=long_description,
long_description_content_type="text/markdown",
# crée un script exécutable 'franterprete' qui appelle la fonction main du module franterprete
entry_points={'console_scripts': ['franterprete=franterprete.franterprete:main']}
)
