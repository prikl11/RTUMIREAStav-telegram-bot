import requests

def get_group_id(group_name: str):
    url = "https://education-ks.ru/getrasp/ajax-dropdown-style"

    params = {
        "method": "getGroups",
        "idClient": 3,
        "idFac": 0,   
        "FO": 0,
        "idKurs": 0
    }

    response = requests.get(url, params=params)
    groups = response.json()

    for g in groups:
        if g["nameGroup"] == group_name:
            return g["idGroup"]
    return None