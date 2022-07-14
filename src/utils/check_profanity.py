import requests
from env import RAPIDAPI_HOST, RAPIDAPI_KEY, RAPIDAPI_URL
from functools import reduce

def checkProfanity(elements):
    text = reduce(lambda fulltext, string: fulltext + ' ' + string, elements) if len(elements) > 1 else elements[0]

    url = RAPIDAPI_URL + '/containsprofanity'

    querystring = {"text": text}

    headers = {
	    "X-RapidAPI-Key": RAPIDAPI_KEY,
	    "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        return True if response.text == 'true' else False
    except Exception as err:
        print(str(err))
        return True

    