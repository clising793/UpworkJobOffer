import json
import re

from upwork_helper import get_active_proposals, search_contracts, get_proposal, AuthTokenFailedException, get_archived_proposals
from auth import refresh_token
import boto3
import random
import time

db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'
db_name_transaction = 'scraper_db'

# Function to sleep for a random duration
def sleep_random(min_duration, max_duration):
    sleep_duration = random.uniform(min_duration, max_duration)
    time.sleep(sleep_duration)

def lambda_handler():

    try:
        active_proposals = get_active_proposals()
        contracts = get_archived_proposals()

        for proposal in active_proposals:
            print(f"======PROPOSAL")
            application_id = proposal.get("applicationUID")
            application = get_proposal(application_id)
            job_id = application.get("jobDetails").get("opening").get("job").get("info").get("ciphertext")
            print(f"{job_id}")

        print(f"======")
            # Commit the transaction
        for contract in contracts:
            print(f"======CONTRACT")
            application_id = contract.get("applicationUID")
            application = get_proposal(application_id)
            job_id = application.get("jobDetails").get("opening").get("job").get("info").get("ciphertext")
            print(f"{job_id}")

            # Commit the transaction
    except AuthTokenFailedException as e:
        refresh_token()
        error_message = 'Token Expired. Refresh Successful'
        client = boto3.client("ses")
        client.send_email(Source="auto-job-query@marchcroft.com",
                              Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                              Message={"Subject": {"Data": 'Access Error in Send Proposal - Token Refresh'},
                                       "Body": {"Html": {"Data": error_message}}})
        raise e
    except Exception as e:
        error_message = str(e)
        client.send_email(Source="auto-job-query@marchcroft.com",
                                     Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                                     Message={"Subject": {"Data": 'Error in Send Proposal'},
                                                  "Body": {"Html": {"Data": error_message}}})
        raise e

    return {
        'statusCode': 200,
        'body': {
            'Message': 'Processed job successfully'
        }
    }
