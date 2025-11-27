from dotenv import load_dotenv
from datetime import datetime,timedelta
import requests
import os
import json

def lambda_handler(event=None, context=None):

    # Load environment variables
    load_dotenv()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("DATABASE_ID")
    DATASOURCE_ID = os.getenv("DATASOURCE_ID")

    url = f"https://api.notion.com/v1/data_sources/{DATASOURCE_ID}/query"

    payload = { 
        "filter": { 
            "timestamp": "created_time",
            "created_time": {
                "past_week": {}
            }
        } 
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2025-09-03"
    }

    response = requests.post(url, json=payload, headers=headers)

    json_data = json.loads(response.text)

    entries = json_data.get("results", [])

    for entry in entries:
        if entry['properties']['Status']['checkbox'] is True:
            # print('Success. checking to add reps or weight')
            if entry['properties']['Reps']['number'] == 12:
                entry['properties']['Reps']['number'] = 8
                entry['properties']['lbs']['number'] += 5
            elif entry['properties']['Reps']['number'] in (8,10):
                entry['properties']['Reps']['number'] += 2
        
        current_entry_date = datetime.strptime(entry['properties']['Date']['date']['start'],'%Y-%m-%d')
        new_entry_date = current_entry_date + timedelta(weeks=1)
        entry['properties']['Date']['date']['start'] = new_entry_date.strftime('%Y-%m-%d')
        entry['properties']['Status']['checkbox'] = False

        url = "https://api.notion.com/v1/pages"

        payload = { 
            "parent": {
                "type": "data_source_id",
                "data_source_id": DATASOURCE_ID
            },
            "properties": entry['properties']
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2025-09-03"
        }

        response = requests.post(url, json=payload, headers=headers)

        json_data = json.loads(response.text)

        print(f"{json_data['properties']['Date']['date']['start']},{json_data['properties']['Exercise']['title'][0]['plain_text']},{json_data['properties']['Person']['select']['name']}")

if __name__ == "__main__":
    lambda_handler()
