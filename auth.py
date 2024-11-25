import boto3
import requests

username = "ddo.asare@gmail.com"
password = "Marchcroft2024#"
security = "torez"
url = "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir"
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.60.3 (Freelancer)",
    "X-Requested-With": "XMLHttpRequest",
    "Host": "www.upwork.com",
    "Cache-Control": "no-cache",
    "Referer": "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir",
    "Origin": "https://www.upwork.com",
    "X-Odesk-Csrf-Token": "5e621d69c8986412a641863ba93b9857",
}

def do_security_challege(auth_token, challenge_data, cookies):
    print('do_security_challege')
    session = requests.Session()
    update_headers ={
        "Cookie": cookies
    }
    headers.update(update_headers)
    body = {
        "login": {
            "deviceAuthorization": {
                "answer": security
            },
            "mode": "challenge",
            "username": username,
            "rememberme": True,
            "authToken": auth_token,
            "challengeData": challenge_data,
            "elapsedTime": 58410,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1711891476589__UDF43-m4_14ck_tt",
            "deviceType": "mobile"
        }
    }
    try:
        r = session.post(url,
                         headers=headers, json=body)
        r.raise_for_status()
        print(f'SUCCESS=={r.json()}')
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
        return ("Timeout Error:", errt)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
        return ("Error Connecting:", errc)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
        return ("Http Error:", errh)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
        return ("OOps: Something Else", err)
    ssm = boto3.client('ssm')
    cookies = session.cookies.get_dict()
    if cookies:
        ssm.put_parameter(
            Name='/upwork-job/proposal/cookies',
            Value="; ".join([str(x) + "=" + str(y) for x, y in cookies.items()]),
            Type='String',
            Overwrite=True
        )
def get_cookies():
    print('get_cookies')
    ssm = boto3.client('ssm')
    session = requests.Session()

    body = {
        "login": {
            "mode": "password",
            "iovation": "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;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",
            "username": f"{username}",
            "rememberme": True,
            "elapsedTime": 24145,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1711891476589__UDF43-m4_14ck_tt",
            "deviceType": "mobile",
            "password": f"{password}",
            "biometricEligible": True
        }
    }
    try:
        r = session.post(url,
                         headers=headers, json=body)
        r.raise_for_status()
        print('success')
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
        return ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
        return ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
        return ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
        return ("OOps: Something Else", err)
    cookies = session.cookies.get_dict()
    if cookies:
        ssm.put_parameter(
            Name='/upwork-job/proposal/cookies',
            Value="; ".join([str(x) + "=" + str(y) for x, y in cookies.items()]),
            Type='String',
            Overwrite=True
        )

def refresh_token():
    ssm = boto3.client('ssm')
    get_cookies()
    cookies = ssm.get_parameter(Name='/upwork-job/proposal/cookies', WithDecryption=True)['Parameter']['Value']
    print("getCookies(): " + cookies)
    print('refresh_token')
    session = requests.Session()

    update_headers = {
        "Cookie": cookies
    }
    headers.update(update_headers)
    print(headers)
    body = {
        "login": {
            "mode": "password",
            "iovation": "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;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",
            "username": "ddo.asare@gmail.com",
            "elapsedTime": 45720,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1711891476589__UDF43-m4_14ck_tt",
            "deviceType": "mobile",
            "password": "Marchcroft2024#",
        }
    }
    try:
        r = session.post(url,
                         headers=headers, json=body)
        r.raise_for_status()
        response = r.json()
        oauth_token = session.cookies.get_dict().get('oauth2_global_js_token')
        print(f'SUCCESS BODY:{response}')
        if response.get('success') == 0 and response.get('mode') == 'challenge':
            challenge_data = response.get('challengeData')
            auth_token = response.get('authToken')
            do_security_challege(auth_token, challenge_data, cookies)
    except requests.exceptions.HTTPError as errh:
        print(errh)
        return ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
        return ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
        return ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print(err)
        return ("OOps: Something Else", err)

    # cookies = session.cookies.get_dict()
    print("------- Refresh Method")
    print(r.status_code)
    print(r.reason)
    print(oauth_token)

    # print(cookies)
    if oauth_token:
        ssm.put_parameter(
            Name='/upwork-job/proposal/oAuthtoken',
            Value=oauth_token,
            Type='String',
            Overwrite=True
        )

