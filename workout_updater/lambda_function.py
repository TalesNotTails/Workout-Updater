from dotenv import load_dotenv
from datetime import datetime,timedelta
import requests
import os
import json

def get_pages():
    url = f"https://api.notion.com/v1/data_sources/{os.getenv("DATASOURCE_ID")}/query"

    payload = { 
        "filter": { 
            "property": "Date",
            "date": {
                "past_week": {}
            }
        } 
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {os.getenv("NOTION_TOKEN")}",
        "Notion-Version": "2025-09-03"
    }

    response = requests.post(url, json=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data

def create_pages(entry):
    url = "https://api.notion.com/v1/pages"

    payload = { 
        "parent": {
            "type": "data_source_id",
            "data_source_id": os.getenv("DATASOURCE_ID")
        },
        "properties": entry['properties']
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {os.getenv("NOTION_TOKEN")}",
        "Notion-Version": "2025-09-03"
    }

    response = requests.post(url, json=payload, headers=headers)

    json_data = json.loads(response.text)

    return json_data


def lambda_handler(event=None, context=None):

    # Load environment variables
    load_dotenv()

    json_data = get_pages()

    entries = json_data.get("results", [])

    for entry in entries:
        if entry['properties']['Rep Range']['select']['name'] == "Standard":
            max_reps = 12 
            min_reps = 8
        else:
            max_reps = 16
            min_reps = 12
        if entry['properties']['Status']['checkbox'] is True:
            if entry['properties']['Reps']['number'] >= max_reps:
                entry['properties']['Reps']['number'] = min_reps
                entry['properties']['lbs']['number'] += 5
            elif int(entry['properties']['Reps']['number']) < max_reps:
                entry['properties']['Reps']['number'] += 2
        
        current_entry_date = datetime.strptime(entry['properties']['Date']['date']['start'],'%Y-%m-%d')
        new_entry_date = current_entry_date + timedelta(weeks=1)
        entry['properties']['Date']['date']['start'] = new_entry_date.strftime('%Y-%m-%d')
        entry['properties']['Status']['checkbox'] = False

        json_data = create_pages(entry)

        print(f"{json_data['properties']['Date']['date']['start']},{json_data['properties']['Exercise']['title'][0]['plain_text']},{json_data['properties']['Person']['select']['name']}")

if __name__ == "__main__":
    lambda_handler()
