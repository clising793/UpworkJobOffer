import time
import requests
import json

OPENAI_API_KEY = "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"
ASSISTANT_ID = "asst_w0uZz63NyeiLwhvyG6IFj9Kf"
REQUEST_MESSAGE = "Use profile_data.txt file and to create me a proposal using the key words provided and highlight experience and benefits for this job description. Provide the proposal only no additional text"
# REQUEST_MESSAGE = "Create a proposal for this job description and use my name as author. Use profile_data.txt file and provide with no explanation just the response"

def check_status(thread_id, run_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v1"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch the thread run status.")

    status = response.json().get('status')

    if status == "completed":
        print("Process completed successfully.")
        return response.json()  # or any other action
    elif status in ["queued", "in_progress"]:
        print("Process is still in progress... waiting 5 seconds to check again.")
        time.sleep(5)
        return check_status(thread_id, run_id)  # Recursive call
    else:
        raise Exception(f"Unexpected status: {status}")

def create_thread(description):
    url = "https://api.openai.com/v1/threads/runs"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v1"
    }

    # Data payload for the POST request
    data = {
        "assistant_id": ASSISTANT_ID,
        "thread": {
            "messages": [
                {"role": "user", "content": f"{REQUEST_MESSAGE} {description}", "file_ids": ["file-TSMH4bxz92Lp9uwvPmWtr4Ta"]}
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        # Assuming the API returns the thread ID and run ID in the expected fields
        thread_id = response_data.get('thread_id')
        run_id = response_data.get('id')
        return thread_id, run_id
    else:
        raise Exception("Failed to create thread. Status code:", response.status_code)
def get_latest_assistant_message(thread_id):
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "assistants=v1"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        messages = response.json().get('data', [])

        # Filter messages to those where role is 'assistant' and sort by 'created_at'
        assistant_messages = [msg for msg in messages if msg['role'] == 'assistant']
        if not assistant_messages:
            return "No assistant messages found."

        # Assuming the API returns messages in chronological order,
        # the last message in the list should be the most recent.
        # If not, sort them by 'created_at' timestamp.
        latest_message = assistant_messages[-1]

        # Extract the content text value from the latest assistant message
        latest_content = latest_message['content'][0]['text']['value']
        return extract_text_between_markers(latest_content)
    else:
        raise Exception("Failed to fetch messages. Status code:", response.status_code)

def get_proposal(description):
    print('Creating Thread')
    thread_id, run_id = create_thread(description)
    print(f"Thread ID: {thread_id}, Run ID: {run_id}")
    check_status(thread_id,run_id)
    return get_latest_assistant_message(thread_id)

def extract_text_between_markers(file_content):
    # Checking if the delimiter "---" is in the file content
    if '---' in file_content:
        # Splitting the file content at each "---" and getting the second part (index 1)
        # This assumes that the desired content is the first section enclosed by "---"
        print("Extracting from message content between ---")
        split_segments = file_content.split('---')
        extracted_text = split_segments[1].strip() if len(split_segments) > 1 else split_segments[0].strip()
        return extracted_text
    else:
        return file_content