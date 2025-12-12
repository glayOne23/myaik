# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.conf import settings
from django.utils import timezone

import requests
import json
import jwt
import os

class API_WHATSAPP:
    url         = settings.API_WHATSAPP_URL
    secret      = ''
    access      = ''
    refresh     = ''
    filename    = ''

    def __init__(self, secret, filename=None):
        self.secret = secret
        self.filename = 'token/{0}.json'.format(filename) if filename else 'token/{0}.json'.format(secret)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)



    def getNewToken(self):
        url = '%stoken/create/' % (self.url)
        body = { 'secret' : self.secret }
        response = requests.post(url, data=body)
        response = response.json()

        if response['status'] == 'success':
            with open(self.filename,'w') as file:
                json.dump(response['data'], file, indent=4)

            self.access = response['data']['access']
            self.refresh = response['data']['refresh']

            return response
        else:
            return response
        
    
    
    def getVerifyToken(self, token:str):
        url = '%stoken/verify/' % (self.url)
        body = { 'token' : self.secret }
        response = requests.post(url, data=body)
        response = response.json()

        return response



    def getRefreshToken(self, refresh):
        url = '%stoken/refresh/' % (self.url)
        body = { 'refresh' : refresh }
        response = requests.post(url, data=body)
        response = response.json()

        if response['status'] == 'success':
            token = { "refresh": response['data']['refresh'], "access": response['data']['access'] }

            with open(self.filename,'w') as file:
                json.dump(token, file, indent=4)

            self.refresh = response['data']['refresh']
            self.access = response['data']['access']

            return response
        else:
            return response



    def getToken(self):
        try:
            with open(self.filename) as file:
                data = json.load(file)

            decode_refresh = jwt.decode(data['refresh'], options={"verify_signature": False})
            decode_access = jwt.decode(data['access'], options={"verify_signature": False})
            exp_refresh = decode_refresh['exp']
            exp_access = decode_access['exp']

            # If the token has expired then take a new token
            timezonenow = timezone.now().timestamp()
            if exp_access <= timezonenow:
                if exp_refresh <= timezonenow:
                    return self.getNewToken()
                else:
                    return self.getRefreshToken(data['refresh']) 
            else:
                self.access = data['access']
                self.refresh = data['refresh']

                checktoken = self.getVerifyToken(exp_access)
                if checktoken['status'] != 'success':
                    return self.getNewToken()
                
                return { 'code' : 200, 'status' : 'success', 'message' : 'Success', 'data' : data, }

        except:
            return self.getNewToken()

    

    def send_text(self, json:json):
        gettoken = self.getToken()

        if gettoken['status'] == 'success':
            url = self.url + 'sendtext'
            header = { 'Authorization' : 'Bearer %s' % (self.access) }
            response = requests.post(url, headers=header, json=json)
            response = response.json()

            return response
        else:
            return gettoken



apiwhatsapp = API_WHATSAPP(settings.API_WHATSAPP_SECRET, 'apiwhatsapp')