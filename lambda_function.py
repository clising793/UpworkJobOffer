import json
import re
import traceback

import psycopg2
from psycopg2.extras import DictCursor
from upwork_helper import get_active_proposals, search_contracts, get_proposal, AuthTokenFailedException, \
    get_archived_proposals, get_job_details
from auth import refresh_token
import boto3
import random
import time

# import json
# from datetime import datetime, timedelta, timezone
# import pytz

db_host = 'database-1.c05cmttqad2g.eu-west-1.rds.amazonaws.com'
db_user = 'postgres'
db_password = 'GWtxSGM4swxxhN3fMHRH'
db_name_transaction = 'scraper_db'

# Function to sleep for a random duration
def sleep_random(min_duration, max_duration):
    sleep_duration = random.uniform(min_duration, max_duration)
    time.sleep(sleep_duration)

def lambda_handler(event, context):
    conn = psycopg2.connect(host=db_host, user=db_user, password=db_password, dbname=db_name_transaction)
    cursor = conn.cursor(cursor_factory=DictCursor)
    client = boto3.client("ses")
    # job_id = event.get("job_id", None)

    try:
        # SQL statement to select all job_id values from upwork_job_proposals
        sql_query = "SELECT job_id FROM upwork_job_proposals ORDER BY RANDOM() LIMIT 5;"

        # Execute the SQL statement
        cursor.execute(sql_query)

        # Fetch all results
        job_ids_tuples = cursor.fetchall()
        #
        job_ids = [job_id_tuple[0] for job_id_tuple in job_ids_tuples]

        # Print or process the list of job_ids
        for job_id in job_ids:
            if job_id == '' or job_id is None:
                continue
            print(f"PROCESSING JOB_ID {job_id}")
            try:
                job_details = get_job_details(job_id)
            except Exception:
                continue
            print(job_details)
            total_applicants = job_details.get("job").get("clientActivity").get("totalApplicants")
            total_hired = job_details.get("job").get("clientActivity").get("totalHired")
            total_invited_to_interview = job_details.get("job").get("clientActivity").get("totalInvitedToInterview")
            invitations_sent = job_details.get("job").get("clientActivity").get("invitationsSent")
            try:
                application_id = job_details.get("currentUserInfo", {}).get("freelancerInfo", {}).get("application", {}).get("vjApplicationUid", "")
                application = get_proposal(application_id)
                viewed = application.get("applicant").get("viewedByClientDate") is not None
                hired = application.get("jobDetails").get("currentUserInfo").get("freelancerInfo").get("hired") is True
                update_sql = f"""
                                    UPDATE upwork_job_proposals
                                    SET application_id = %s,
                                        viewed = %s, 
                                        contract_offered = %s,
                                        active_proposal = %s,
                                        total_applicants = %s, 
                                        total_hired = %s, 
                                        total_invited_to_interview = %s, 
                                        invitations_sent = %s
                                    WHERE job_id = %s;
                                    """
                cursor.execute(update_sql,
                               (application_id, viewed, hired, True, total_applicants, total_hired, total_invited_to_interview, invitations_sent, job_id))
                conn.commit()
                continue
            except Exception:
                print(traceback.format_exc())
                print("Get application detaills failed")


            # Update the upwork_job_proposals table with the new values
            update_sql = """
                    UPDATE upwork_job_proposals
                    SET  
                        total_applicants = %s, 
                        total_hired = %s, 
                        total_invited_to_interview = %s, 
                        invitations_sent = %s
                    WHERE job_id = %s;
                    """
            cursor.execute(update_sql, (total_applicants, total_hired, total_invited_to_interview, invitations_sent, job_id))
            conn.commit()


    except AuthTokenFailedException as e:
        refresh_token()
        error_message = 'Token Expired. Refresh Successful'
        client.send_email(Source="auto-job-query@marchcroft.com",
                              Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                              Message={"Subject": {"Data": 'Stats Job Failure'},
                                       "Body": {"Html": {"Data": error_message}}})
        raise e
    except Exception as e:
        error_message = str(e)
        client.send_email(Source="auto-job-query@marchcroft.com",
                                     Destination={"ToAddresses": ["contactus@marchcroft.com"]},
                                     Message={"Subject": {"Data": 'Stats Job Failure'},
                                                  "Body": {"Html": {"Data": error_message}}})
        raise e

    conn.close()

    return {
        'statusCode': 200,
        'body': {
            'Message': 'Processed job successfully'
        }
    }
