from types import SimpleNamespace 
from time import sleep 
import requests, json, re  

class User():
    cookie = ""
    csrf = ""
user = User()

def update_csrf():
    user.csrf = requests.post("https://auth.roblox.com/v2/logout", headers={"cookie":user.cookie}).headers["x-csrf-token"]

def set_cookie(cookie):
    user.cookie = ".ROBLOSECURITY="+re.sub("(.*)_", "", cookie.upper())

def to_object(str):
    return json.loads(str, object_hook=lambda d: SimpleNamespace(**d))

def request(method, url, has_cookie=False, has_csrf=False, data={}, to_json=False, content_type="application/json"):
    headers = {"content-type": content_type}
    if has_cookie: headers["cookie"] = user.cookie
    if has_csrf: headers["x-csrf-token"] = user.csrf
    response = requests.request(method, "https://"+re.sub("(.*)://", "", url), data=data, headers=headers)
    if response.status_code == 200:
        result = response.text 
        if to_json: result = to_object(result)
        return result 
    elif response.status_code == 401 and (response.reason == 0 or response.reason.find("Unauthorized") != -1):
        if has_cookie:
            print("Unauthorized request, please enter a valid cookie")
            set_cookie(input("Cookie: "))
        else: has_cookie = True 
        return request(method, url, has_cookie, has_csrf, data, to_json)
    elif response.status_code == 403 and (response.reason == 0 or response.reason.find("Token Validation Failed") != -1):
        if has_csrf:
            print("Request validation failed, updating csrf")
            update_csrf()
        else: has_csrf = True 
        return request(method, url, has_cookie, has_csrf, data, to_json)
    elif response.status_code == 429 or response.status_code == 500:
        print("Getting rate limited, waiting for 60 seconds")
        sleep(60) 
        return request(method, url, has_cookie, has_csrf, data, to_json)
    else:
        print("Request failed:", response.status_code, response.reason) 
        return False 
    
