import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import tz
import json
import re
import random
import string
import locale

from typing import Optional, Union, no_type_check

parcoursup_url: str = "https://dossier.parcoursup.fr/Candidat/"
parcoursup_mobile: str = "https://mobile.parcoursup.fr/NotificationsService/services/"
JSON_HEADERS: dict = {"Content-Type": "application/json"}

locale.setlocale(locale.LC_ALL, 'fr_FR')


class _Wish:
    def __init__(self, json_dict: dict) -> None:
        self.id: str = json_dict["voeuId"]
        self.name: str = json_dict["formation"]
        self.is_apprentissage: bool = json_dict["formationEnApprentissage"]
        self.etablissement: dict = json_dict["etablissement"]
        self.additional_infos: str = json_dict["infosComplementaires"]

    @no_type_check
    def __new__(cls, json_dict: dict):
        if cls != _Wish:
            return super(_Wish, cls).__new__(cls)

        state = json_dict["situation"]["code"]
        if state == 1:
            return Proposition(json_dict)
        elif state == 0:
            return PendingWish(json_dict)
        elif state == -1:
            return RefusedWish(json_dict)
        else:
            raise Exception("Unable to find state")

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.etablissement['nom']} {self.name}>"


class Proposition(_Wish):
    """
    Represente une propostion d'admission. Vous n'avez pas à creer cette classe manuellement

    Attributes
    ----------
    id : str
        Id du voeu
    name : str
        Nom de la formation
    is_apprentissage : bool
        Est ce que le voeu est un voeu d'apprentissage
    etablissement : dict
        Info sur l'etablissement de la formation
    reply_deadline: Optional[datetime.datetime]
        Date a laquelle il faut avoir répondu au voeu
    accepted: bool
        Est ce que le candidat est accepté dans la formation
    """

    def __init__(self, json_dict: dict) -> None:
        super().__init__(json_dict)

        self.reply_deadline: Optional[datetime]
        self.accepted: bool

        if json_dict["dateLimiteReponse"]:
            self.reply_deadline = datetime.strptime(re.sub(r" \([^\)]*\)", "", json_dict["dateLimiteReponse"]), "%d %B %H:%M").replace(
                year=datetime.now().year, tzinfo=tz.gettz('Europe/Paris'))
            self.accepted = False
        else:
            self.reply_deadline = None
            self.accepted = True


class PendingWish(_Wish):
    """
    Represente un voeu en attente. Vous n'avez pas à creer cette classe manuellement

    Attributes
    ----------
    id : str
        Id du voeu
    name : str
        Nom de la formation
    is_apprentissage : bool
        Est ce que le voeu est un voeu d'apprentissage
    etablissement : dict
        Info sur l'etablissement de la formation
    waitlist_position: Optional[int]
        Votre position dans la liste d'attente
    waitlist_lenght: Optional[int]
        Nombre total de candidats dans la liste d'attente
    nb_place: Optional[int]
        Nombre de places dans le groupe
    ranking_position: Optional[int]
        Votre position dans le classement
    last_place: Optional[int]
        Position dans le classement du dernier candidat qui a reçu une proposition d’admission
    last_place_previous_year: Optional[int]
        Position dans le classement du dernier candidat qui a reçu une proposition d’admission l'annee precedente
    """

    def __init__(self, json_dict: dict) -> None:
        super().__init__(json_dict)

        self.waitlist_position: Optional[int]
        self.waitlist_lenght: Optional[int]
        self.nb_place: Optional[int]
        self.ranking_position: Optional[int]
        self.last_place: Optional[int]
        self.last_place_previous_year: Optional[int]

        if json_dict.get("autresInformations"):
            soup = BeautifulSoup(
                json_dict["autresInformations"][0]["texte"], features="html.parser")
            strongs = [s for s in soup.findAll("strong") if s.text.isnumeric()]
            if len(strongs) == 6:
                self.waitlist_position = int(strongs[0].text)
                self.waitlist_lenght = int(strongs[1].text)
                self.nb_place = int(strongs[2].text)
                self.ranking_position = int(strongs[3].text)
                self.last_place = int(strongs[4].text)
                self.last_place_previous_year = int(strongs[5].text)
            elif len(strongs) == 2:
                self.waitlist_position = None
                self.waitlist_lenght = None
                self.last_place = None
                self.last_place_previous_year = None

                self.ranking_position = int(strongs[0].text)
                self.nb_place = int(strongs[1].text)
            else:
                self.waitlist_position = None
                self.waitlist_lenght = None
                self.nb_place = None
                self.ranking_position = None
                self.last_place = None
                self.last_place_previous_year = None


class RefusedWish(_Wish):
    """
    Represente un voeu refusé. Vous n'avez pas à creer cette classe manuellement

    Attributes
    ----------
    id : str
        Id du voeu
    name : str
        Nom de la formation
    is_apprentissage : bool
        Est ce que le voeu est un voeu d'apprentissage
    etablissement : dict
        Info sur l'etablissement de la formation
    reason: str
        Raison pour laquelle le voeu a ete refuse
    """

    def __init__(self, json_dict: dict) -> None:
        super().__init__(json_dict)

        self.reason: str = json_dict["situation"]["libelle"]


class Parcoursup_Client:
    """
    Un client Parcoursup

    Parametres
    ----------
    username : str
    password : str
    """

    def __init__(self, username: Union[int, str], password: str) -> None:
        self.username: Union[int, str] = username
        self.password: str = password

        self.desktop_session = requests.Session()
        self.__connect_desktop()

        self.mobile_session = requests.Session()
        self.__connect_mobile()

    @no_type_check
    def __connect_desktop(self) -> None:
        global parcoursup_url
        r = self.desktop_session.get(f"{parcoursup_url}authentification")
        r = self.__try_onload(self.desktop_session, r)

        soup = BeautifulSoup(r.text, features="html.parser")

        form = soup.find('form', attrs={"name": "accesdossier"})
        if not form:
            return

        data = {input_.get("name"): input_.get("value")
                for input_ in form.findAll('input')}
        data["usermobile"] = False
        data["g_cn_cod"] = self.username
        data["g_cn_mot_pas"] = self.password

        parcoursup_url = r.url.replace('authentification', '')

        post_url = f"{parcoursup_url}{form.get('action')}"
        self.desktop_session.post(post_url, data=data)

    def get_html(self, to_file: bool = False, path: Optional[str] = None) -> str:
        """
        Retourne l'HTML de la page des résultats d'admission

        to_file : bool
            Si on souhaite enregistrer l'HTML vers un fichier
        path : Optional[str]
            Chemin vers lequel enregistrer le fichier

        Retours
        -------
        str
            HTML de la page ou chemin du fichier HTML
        """
        dossier = self.desktop_session.get(f"{parcoursup_url}admissions")

        if not to_file:
            return dossier.text

        if not path:
            path = fr"{datetime.now().isoformat()}.html".replace(":", "-")

        with open(path, "w", encoding="utf-8") as f:
            f.write(dossier.text)
        return path

    def __connect_mobile(self) -> None:
        data = {
            "appVersion": "2.2.1",
            "plateforme": "android",
            "plateformeVersion": "12",
            "session": datetime.now().year,
            "token": "".join(random.choices(list(string.ascii_letters + string.digits + string.punctuation), k=128))
        }

        token = self.mobile_session.post(f"{parcoursup_mobile}token",
                                         data=json.dumps(data), headers=JSON_HEADERS)
        if not token:
            raise Exception(f"{token.status_code} {token.reason}")

        data = {
            "code": self.password,
            "login": self.username,
            "tokenId": token.json()["tokenId"]
        }
        login = self.mobile_session.post(f"{parcoursup_mobile}login",
                                         data=json.dumps(data), headers=JSON_HEADERS)
        self.mobile_session.headers.update({"X-Auth-Token": login.headers["X-Auth-Token"],
                                            "Authorization": login.headers["Authorization"],
                                            "X-Token-Id": str(token.json()["tokenId"]),
                                            "X-Auth-Login": login.headers["X-Auth-Login"]
                                            })
        if not login:
            raise Exception(f"{login.status_code} {login.reason}")

    def get_wishes(self) -> list[_Wish]:
        """Retourne les voeux"""
        r = self.mobile_session.get(f"{parcoursup_mobile}voeux?liste=tous")
        if not r:
            raise Exception(f"{r.status_code} {r.reason}")
        return [_Wish(w) for w in r.json()["voeux"]]

    def get_wish(self, id: str) -> _Wish:
        """
        Retourne le voeu correspondant à l'id

        id : str
            Id du voeu

        Retours
        -------
        Wish
            Voeu correspondant à l'id
        """
        r = self.mobile_session.get(f"{parcoursup_mobile}voeux/{id}")
        if not r:
            raise Exception(f"{r.status_code} {r.reason}")
        return _Wish(r.json()["voeu"])

    @classmethod
    @no_type_check
    def __try_onload(cls, s: requests.Session, r: requests.Response) -> requests.Response:
        soup = BeautifulSoup(r.text, features="html.parser")
        onload = soup.find('body').get("onload")
        if not onload:
            return r
        match = re.search(r"window.location='(?P<url>[^']*)'", onload)
        url = match.group('url')
        return cls.__try_onload(s, s.get(url))

    @classmethod
    def is_open(cls) -> bool:
        """Retourne True si le site parcoursup est ouvert"""
        r = requests.get(f"{parcoursup_url}authentification")
        r = cls.__try_onload(requests, r)
        soup = BeautifulSoup(r.text, features="html.parser")
        return bool(soup.find('form', attrs={"name": "accesdossier"}))
