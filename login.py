import boto3
import requests

def getCookies():
    ssm = boto3.client('ssm')
    session = requests.Session()
    url = "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Referer": "https://www.upwork.com/en-gb/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir",
        "Origin": "https://www.upwork.com",
        "X-Odesk-Csrf-Token": "8dc920fbc45e70f062aed0e80c23fb16",
        "X-Requested-With": "XMLHttpRequest"
    }

    body = {
        "login": {
            "mode": "password",
            "username": "danielsos1017@gmail.com",
            "rememberme": True,
            "elapsedTime": 24145,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1699371165849__UDF43-m4_14ck_tt",
            "deviceType": "mobile",
            "password": "PasswordChange2",
            "biometricEligible": True
        }
    }
    try:
        r = session.post(url,
                         headers=headers, json=body)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    cookies = session.cookies.get_dict()
    if cookies:
        ssm.put_parameter(
            Name='/upwork-job/proposal/cookies',
            Value="; ".join([str(x) + "=" + str(y) for x, y in cookies.items()]),
            Type='String',
            Overwrite=True
        )


def refreshToken():
    ssm = boto3.client('ssm')
    getCookies()
    cookies = ssm.get_parameter(Name='/upwork-job/proposal/cookies', WithDecryption=True)['Parameter']['Value']
    print("getCookies(): " + cookies)
    session = requests.Session()
    url = "https://www.upwork.com/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir"
    # print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.55.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Referer": "https://www.upwork.com/en-gb/ab/account-security/login?redir=%2Fab%2Faccount-security%2Foauth2%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3Dcf45a282f124094d49066172e6eaf5da%26redirect_uri%3Dhttps%253A%252F%252Fwww.upwork.com%252Foauth2redir",
        "Origin": "https://www.upwork.com",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookies
    }

    body = {
        "login": {
            "mode": "password",
            "username": "danielsos1017@gmail.com",
            "rememberme": True,
            "elapsedTime": 24145,
            "forterToken": "2f09b55628884328b8f105d5ed24191e_1699371165849__UDF43-m4_14ck_tt",
            "deviceType": "mobile",
            "password": "PasswordChange2",
            "authToken": "ef8d7afb64c4be78724fe76fe81ab12e4e30477e06917e51c3b078925d548943",
            "securityCheckCertificate": "eyJraWQiOiJyZWdpc3RyYXRpb24ua2V5LnJzYTUxMi5wdWJsaWMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJhdXRoRFMiLCJzdWIiOiI4YTE0YjNmOSIsImlzcyI6ImF1dGhEUyIsInZuZF9lb190eXBlIjoiU0VDVVJJVFlfQ0hFQ0siLCJ2ZW5kb3JJZCI6IklPVkFUSU9OIiwiZXhwIjoxNjk5MzcyNjI1LCJpYXQiOjE2OTkzNzI2MTV9.N7RhtgRj6M8DmHB3OGVw7CgHJI8aK-Gf52tDCEQ5nVXpAiY0sklULo8KHpLcAco2r5tF44k3Gxg8GXXLBFkkDg"
        }
    }
    try:
        r = session.post(url,
                         headers=headers, json=body)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)

    oauth_token = session.cookies.get_dict().get('oauth2_global_js_token')
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

