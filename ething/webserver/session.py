# coding: utf-8

import time
import re
import hmac,hashlib
import jwt

def uniqid(prefix = ''):
    return prefix + hex(int(time.time()))[2:10] + hex(int(time.time()*1000000) % 0x100000)[2:7]

class Session(object):
    
    def __init__(self, core):
        self.core = core
        

    def authenticate(self, login, password, request, response):
        #if self.core.config['auth']['localonly']:
        #    pass
        
        if login == self.core.config['auth']['username'] and password == self.core.config['auth']['password']:
            
            # set session cookie (httponly)
            expireAt = int(time.time() + self.core.config['session']['expiration'])
            
            path = re.sub('/auth/.*$', '', str(request.url_rule))
            if not path:
                path = '/'
            
            secure = bool(request.url.startswith('https://'))
            
            sessionData = {
                'sessionId' : uniqid(''),
                'iat' : time.time(),
                'exp' : expireAt
            }
            
            csrf_token = hmac.new(self.core.config['session']['secret'].encode('utf8'), sessionData['sessionId'].encode('utf8'), hashlib.md5).hexdigest()
            
            token = jwt.encode(sessionData, self.core.config['session']['secret'])
            
            response.set_cookie(self.core.config['session']['cookie_name'], token, expires = expireAt, domain = request.host, path = path, secure = secure, httponly = True)
            response.set_cookie('Csrf-token', csrf_token, expires = expireAt, domain = request.host, path = path, secure = secure, httponly = False)
            
            return True
            
        
        return False

    
    def checkCsrf(self, request):
        # Csrf control
        
        csrfToken = request.cookies.get('Csrf-token')
        
        if csrfToken:
            # check in the query string
            csrfToken2 = request.args.get('Csrf-token')
            if not csrfToken2:
                csrfToken2 = request.headers.get('HTTP_X_CSRF_TOKEN')
            
            return csrfToken == csrfToken2
        
        return False
        
        
    
    
    def isAuthenticated(self, request, checkCsrf = None):
        
        token = request.cookies.get(self.core.config['session']['cookie_name'])
        csrfToken = request.cookies.get('Csrf-token')
        
        if token and ((not checkCsrf) or self.checkCsrf(request)):
            # ok decode the JWT token !
            
            try:
                sessionData = jwt.decode(token, self.core.config['session']['secret'])
                
                if 'sessionId' in sessionData:
                    return sessionData
                
            except:
                # invalid JWT
                pass
        
        return False
        
    
    

    def unauthenticate(self, request, response):
        
        path = re.sub('/auth/.*$', '', str(request.url_rule))
        if not path:
            path = '/'
        
        # remove the session cookie
        response.set_cookie(self.core.config['session']['cookie_name'], '', expires = 0, path = path)
        response.set_cookie('Csrf-token', '', expires = 0, path = path)
        
    