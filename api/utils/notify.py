import traceback
import json
import requests
from api.models.notify import Notify
from api.configuration import NOTIFY_SEGMENT, NOTIFY_TOKEN, NOTIFY_URL


headerAuthorization = 'Bearer {0}'.format(NOTIFY_TOKEN)
        
def send_notify(message: Notify):
    try:
        payload = {"segment": NOTIFY_SEGMENT}
        if message.file is None:
            content = {"text": message.message}
        else:
            content = {"text": message.message, "file": {"url": message.file}}
        payload["messages"] = [content] # Send Array 1 Message

        headers = {
			"Content-Type": "application/json",
			"Authorization": headerAuthorization,
			"Accept": "application/json"
			}
        response = requests.request("POST", NOTIFY_URL, data=json.dumps(payload), headers=headers)
        print (response)
        print (response.text)
        return response
    except Exception as e:
        traceback.print_exc()
        return None