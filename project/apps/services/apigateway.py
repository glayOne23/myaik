# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlparse, urlencode
import requests, ssl, socket, json, jwt, os, logging


logger = logging.getLogger(__name__)

class API_GATEWAY:
    url         = settings.API_GATEWAY_URL
    key_path    = settings.API_GATEWAY_KEY
    algorithms  = settings.API_GATEWAY_ALGO
    verify      = settings.API_GATEWAY_VERIFY
    username    = ''
    password    = ''
    access      = ''
    refresh     = ''
    filename    = ''



    def __init__(self, username, password, filename=None):
        self.username = username
        self.password = password
        self.filename = 'token/{0}.json'.format(filename) if filename else 'token/{0}.json'.format(username)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)



    def check_ssl_validity(self):
        '''
            Melakukan validasi SSL dari URL atau Domain Api-Gateway
        '''

        parsed_url = urlparse(self.url)
        hostname = parsed_url.hostname
        context = ssl.create_default_context()
        try:
            # Menghubungkan ke server dan mengambil sertifikat
            with socket.create_connection((hostname, 443)) as sock:
                sock.settimeout(5)
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    # Melakukan verifikasi nama host
                    if ssl.match_hostname(cert, hostname):
                        return True
        except (ssl.SSLError, socket.error, ssl.CertificateError) as e:
            logger.warning(e)
        return False



    # =====================================================================================================
    #                                             AUTHENTICATION
    # =====================================================================================================
    
    def getNewToken(self):
        '''
            Mendapatkan token baru
        '''

        url     = '%stoken/' % (self.url)
        body    = { 'username' : self.username, 'password' : self.password }
        response= requests.post(url, data=body, verify=True)

        if response.status_code == 200:
            responsejson    = response.json()
            access_token    = responsejson.get('access')
            refresh_token   = responsejson.get('refresh')

            if access_token and refresh_token:
                self.access = access_token
                self.refresh= refresh_token

                token = { 'access' : access_token, 'refresh': refresh_token }

                with open(self.filename,'w') as file:
                    json.dump(token, file, indent=4)
            
                return { 
                    'status'    : True,
                    'message'   : 'Token successfully obtained!',
                    'data'      : token
                }
            else:
                return { 
                    'status'    : False,
                    'message'   : 'Token not available in response.',
                }
        else:
            return { 
                'status'    : False,
                'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
            }



    def getRefreshToken(self, refresh):
        '''
            Mendapatkan refresh token
        '''

        url     = '%stoken/refresh/' % (self.url)
        body    = { 'refresh' : refresh }
        response= requests.post(url, data=body, verify=True)
        
        if response.status_code == 200:
            responsejson = response.json()
            access_token = responsejson.get('access')

            if access_token:
                self.access = access_token
                self.refresh= refresh

                token = { 'access' : access_token, 'refresh': refresh }

                with open(self.filename,'w') as file:
                    json.dump(token, file, indent=4)

                return { 
                    'status'    : True,
                    'message'   : 'Token successfully obtained!',
                    'data'      : token
                }
            else:
                return { 
                    'status'    : False,
                    'message'   : 'Token not available in response.',
                }
        else:
            return { 
                'status'    : False,
                'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
            }



    def getToken(self):
        '''
            Mendapatkan token. Secara default mengambil token lama jika expired maka ambil token baru
        '''

        try:
            with open(self.key_path, 'r') as f:
                public_key = f.read()

            with open(self.filename) as file:
                data = json.load(file)

            decode_refresh = jwt.decode(data['refresh'], key=public_key, algorithms=self.algorithms, options={"verify_signature": self.verify})
            decode_access = jwt.decode(data['access'], key=public_key, algorithms=self.algorithms, options={"verify_signature": self.verify})

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
                return {
                    'status'    : True,
                    'message'   : 'Managed to retrieve the old token',
                    'data'      : data,
                }

        except Exception as e:
            print('\n[ERROR] : getToken()', e, '\n')
            return self.getNewToken()



    # =====================================================================================================
    #                                            SIHRD ENDPOINT
    # =====================================================================================================

    def getProfile(self, username:str):
        '''
            Mengambil data profile dari SIHRD berdasarkan username
        '''
        gettoken = self.getToken()

        if gettoken['status']:
            params  = {'uniid': username}
            url     = self.url + 'umar/v3/profil'
            url     = f"{url}?{urlencode(params)}"

            access_token= gettoken['data']['access']
            header      = { 'Authorization' : 'Bearer %s' % (access_token) }
            response    = requests.get(url, headers=header, verify=True)

            if response.status_code == 200:
                responsejson = response.json()

                if responsejson['success']:
                    return { 
                        'status'    : True, 
                        'message'   : 'Success',
                        'data'      : responsejson['rows'],  
                    }
                else:
                    return { 
                        'status'    : False, 
                        'message'   : responsejson['message'],
                    }   
            else:
                return { 
                    'status'    : False,
                    'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
                }
        else:
            return gettoken



    def getKaryawan(self, kepeg:str=None):
        '''
            Mengambil list data karyawan dari SIHRD berdasarkan kepeg
        '''
        gettoken = self.getToken()

        if gettoken['status']:
            url     = self.url + 'umar/v3/karyawan'
            if kepeg:
                params  = {'kepeg': kepeg}
                url     = f"{url}?{urlencode(params)}"
                

            access_token= gettoken['data']['access']
            header      = { 'Authorization' : 'Bearer %s' % (access_token) }
            response    = requests.get(url, headers=header, verify=True)

            if response.status_code == 200:
                responsejson = response.json()

                if responsejson['success']:
                    return { 
                        'status'    : True, 
                        'message'   : 'Success',
                        'data'      : responsejson['rows'],  
                    }
                else:
                    return { 
                        'status'    : False, 
                        'message'   : responsejson['message'],
                    }   
            else:
                return { 
                    'status'    : False,
                    'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
                }
        else:
            return gettoken



    def getLembaga(self, jenis:int=None, uniid:str=None, status:str=None):
        '''
            Mengambil list data lembaga dari SIHRD berdasarkan jenis dan atau uniid
        '''
        gettoken = self.getToken()

        if gettoken['status']:
            url     = self.url + '/umar/v4/lembaga'

            params  = {}
            if jenis:
                params['jenis']  = jenis
            if uniid:
                params['uniid']  = uniid
            if status:
                params['status']  = status
            
            if params:
                url = f"{url}?{urlencode(params)}"
                

            access_token= gettoken['data']['access']
            header      = { 'Authorization' : 'Bearer %s' % (access_token) }
            response    = requests.get(url, headers=header, verify=True)

            if response.status_code == 200:
                responsejson = response.json()

                if responsejson['success']:
                    return { 
                        'status'    : True, 
                        'message'   : 'Success',
                        'data'      : responsejson['rows'],  
                    }
                else:
                    return { 
                        'status'    : False, 
                        'message'   : responsejson['message'],
                    }   
            else:
                return { 
                    'status'    : False,
                    'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
                }
        else:
            return gettoken



    def getJabatan(self, uniid:str=None, kode_lembaga:str=None):
        '''
            Mengambil data jabatan dari SIHRD berdasarkan uniid atau username
        '''
        gettoken = self.getToken()

        if gettoken['status']:
            url     = self.url + '/umar/v2/jabatan'
            url     = f'{url}/{uniid}' if uniid else url
            url     = f'{url}?{urlencode({ "kode_lembaga": kode_lembaga })}' if kode_lembaga else url

            access_token= gettoken['data']['access']
            header      = { 'Authorization' : 'Bearer %s' % (access_token) }
            response    = requests.get(url, headers=header, verify=True)

            if response.status_code == 200:
                responsejson = response.json()

                if responsejson['success']:
                    return { 
                        'status'    : True, 
                        'message'   : 'Success',
                        'data'      : responsejson['rows'],  
                    }
                else:
                    return { 
                        'status'    : False, 
                        'message'   : responsejson['message'],
                    }   
            else:
                return { 
                    'status'    : False,
                    'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
                }
        else:
            return gettoken



    def getPejabatLmbg(self, uniid:str):
        '''
            Mengambil list data jabatan dari SIHRD pada lembaga tertentu
        '''
        gettoken = self.getToken()

        if gettoken['status']:
            url     = self.url + f"/umar/v2/pejabatlbg/{uniid}"

            access_token= gettoken['data']['access']
            header      = { 'Authorization' : 'Bearer %s' % (access_token) }
            response    = requests.get(url, headers=header, verify=True)

            if response.status_code == 200:
                responsejson = response.json()

                if responsejson['success']:
                    return { 
                        'status'    : True, 
                        'message'   : 'Success',
                        'data'      : responsejson['rows'],  
                    }
                else:
                    return { 
                        'status'    : False, 
                        'message'   : responsejson['message'],
                    }   
            else:
                return { 
                    'status'    : False,
                    'message'   : 'There is an error {0}. Please contact the system admin'.format(response.status_code),
                }
        else:
            return gettoken



    # =====================================================================================================
    #                                            OTHER ENDPOINT
    # =====================================================================================================
        
    # ======================================================================
    # Silahkan buat fungsi untuk tiap endpoint apigateway yang anda butuhkan
    # Karena setiap endpoint memiliki response json yang berbeda-beda
    # sehingga sangat sulit untuk membuat satu fungsi yang general
    # ======================================================================
        
    # def YourFunction(self):
    #     gettoken = self.getToken()
    #     if gettoken['status']:
    #         return True
    #     else:
    #         return gettoken
    

    

apigateway = API_GATEWAY(settings.API_GATEWAY_USERNAME, settings.API_GATEWAY_PASSWORD, 'apigateway')