import time
import random

import requests
from string import Template
import json
import boto3
import logging

from templates import hp_template, pp_template

ssm = boto3.client('ssm')

def sleep_random(min_duration, max_duration):
    sleep_duration = random.uniform(min_duration, max_duration)
    time.sleep(sleep_duration)
def search_contracts(contracts=None, page=1):
    if contracts is None:
        contracts = []
    print(f"GET_ACTIVE_CONTRACTS")
    url = "https://www.upwork.com/ab/wm/api/freelancer/contracts/search"
    payload = {
      "data": {
        "page": page,
        "perPage": 10,
        "searchText": "",
        "from": {},
        "to": {},
        "orderIsAsc": False,
        "selectedSortBy": "Start date",
        "contractStatus": ["active"],
        "milestoneStatus": ["any"],
        "escrowRefundStatus": ["any"],
        "contractType": "all",
        "contactPerson": "",
        "freelancer": "",
        "team": "",
        "includeEnded": False
      }
    }

    response = upwork_request(url=url, method='POST', data=payload)
    found = contracts + response.get("data", {}).get("result", {}).get("searchResults", [])
    count = response.get("data", {}).get("result", {}).get("searchResultCounts", {}).get("count", 0)
    total = response.get("data", {}).get("result", {}).get("searchResultCounts", {}).get("total", 0)

    if len(found) == count and count < total:
        search_contracts(contracts=contracts, page=page+1)
    return found

def get_proposal(proposal_id):
    print(f"GET_PROPOSAL - {proposal_id}")
    url = "https://www.upwork.com/ab/proposals/api/v3/proposal/%s" % proposal_id
    response = upwork_request(url, method='GET')
    return response

def get_archived_proposals():
    print(f"GET_ARCHIVED_PROPOSALS")
    url = "https://www.upwork.com/ab/proposals/api/proposals/type/archived?page=0"
    response = upwork_request(url, method='GET')
    applications = response.get("applications", [])
    return [app for app in applications if app.get('dashroomUID') is not None]

def get_active_proposals(applications=None, page=0):
    if applications is None:
        applications = []
    print(f"GET_ACTIVE_PROPOSALS")
    url = "https://www.upwork.com/ab/proposals/api/proposals/type/active?page=%s" % page
    response = upwork_request(url, method='GET')
    applications = applications + response.get("applications", [])
    count = response.get("paging", {}).get("count")
    total = response.get("paging", []).get("total")
    if len(applications) == count and count < total:
        get_active_proposals(applications, page+1)
    return applications

def get_job_details(job_id):
    print(f"JOB_ID==={job_id}")
    url = "https://www.upwork.com/job-details/jobdetails/api/job/%s/summary" % (job_id)
    job_details = upwork_request(url, method='GET')
    return job_details

def upwork_request(url, method, data=None):
    sleep_random(2, 5)
    print(f"URL REQUEST:{url}")
    oAuthtokenPayloads = ssm.get_parameter(Name='/upwork-job/proposal/oAuthtoken', WithDecryption=True)['Parameter'][
        'Value']
    cookies = ssm.get_parameter(Name='/upwork-job/proposal/cookies', WithDecryption=True)['Parameter']['Value']
    cookies = cookies + ';XSRF-TOKEN=5d3d1303de92b2dd829a48bfbabf666f;'
    print(f"METHOD:{method}")
    headers = {
        "Authorization": "Bearer %s" % oAuthtokenPayloads,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Upwork iOS/1.60.3 (Freelancer)",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.upwork.com",
        "Cache-Control": "no-cache",
        "Cookie": cookies,
        "X-Odesk-Csrf-Token": "5d3d1303de92b2dd829a48bfbabf666f",
        "Origin": "https://www.upwork.com"
    }
    if data:
        body_str = json.dumps(data)
        content_length = len(body_str.encode('utf-8'))
        updated_headers = {
            "Content-Length": str(content_length)
        }
        headers.update(updated_headers)
    print(f"HEADERS:{headers}")
    if method == 'GET':
        r = requests.get(url,
                         headers=headers)
    elif method == 'POST':
        r = requests.post(url, json=data,
                         headers=headers)
    status_code = r.status_code
    print(f"Status Code - {status_code}")
    # print(f"Response Body - {r.json()}")
    if status_code == 401:
        raise AuthTokenFailedException(f"Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code == 403:
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code == 400:
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    if status_code != 200:
        raise Exception(f"Opps Failed request url (STATUS_CODE=={status_code}) - {url} with data {data}")
    return r.json()

class AuthTokenFailedException(Exception):
    pass

