<p align="center">
  <a href="https://github.com/Bapt5/parcoursupy">
    <img src="https://upload.wikimedia.org/wikipedia/fr/thumb/d/dc/Logo_parcoursup.svg/1280px-Logo_parcoursup.svg.png" alt="Logo" height="80">
  </a>

  <h3 align="center">parcoursupy</h3>

  <p align="center">
    Python API wrapper pour Parcoursup
    <br />
  </p>
</p>

[![pypi version](https://img.shields.io/pypi/v/parcoursupy.svg)](https://pypi.org/project/parcoursupy/)
[![python version](https://img.shields.io/pypi/pyversions/parcoursupy.svg)](https://pypi.org/project/parcoursupy/)
[![license](https://img.shields.io/pypi/l/parcoursupy.svg)](https://pypi.org/project/parcoursupy/)

## Introduction

C'est un wrapper python pour Parcoursup qui permet de récupérer des informations sur les voeux pendant la phase d'admission.

## A propos

### Dependances

 - python-dateutil
 - beautifulsoup4
 - requests

### Installation
**Stable**

Intallez directement depuis pypi avec la commande `pip install parcoursupy` (Si vous êtes sous Windows et avez des difficultés avec cette commande, utilisez celle-ci en supposant que vous avez python 3.x.x installé sur votre ordinateur: `py -3 -m pip install parcoursupy`)

**Latest**

Vous pouvez installez la dernière version de la bibliothèque directement depuis Github

`pip install git+https://github.com/Bapt5/parcoursupy`

### Usage

Un programme simple permettant de récupérer tous les voeux et d'en afficher le nom et l'établissement
```python
from parcoursupy import *

client = Parcoursup_Client("Your Username", "Your Password")
wishes = client.get_wishes()

for w in wishes:
    print(w.name, w.etablissement["nom"])

```

## Contribution

N'hésitez pas à apporter votre contribution. Toute aide est appréciée. Pour contribuer, veuillez créer un Pull Request avec vos changements.

La configuration de l'environnement de développement consiste simplement à cloner le dépôt et à s'assurer que vous avez toutes les dépendances en
en exécutant `pip install -r requirements.txt`.

## Ajout de fonctionnalités

Parcoursupy couvre les fonctionnalités essentielles, mais si vous avez besoin de quelque chose qui n'est pas encore implémenté, vous pouvez [créer un issue](https://github.com/Bapt5/parcoursupy/issues/new) avec votre demande. (ou vous pouvez contribuer en l'ajoutant vous-même)

## License

Mozilla Public License, version 2.0
