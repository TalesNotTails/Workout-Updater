from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime,timedelta
import os

# Hello from github!

def add_page(props):
    # Update the number field in the database
    notion.pages.create(
        parent={
            'database_id':DATABASE_ID
        },
        properties=props
    )

def lambda_handler(event, context):

    # Load environment variables
    load_dotenv()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DATABASE_ID = os.getenv("DATABASE_ID")

    # Initialize Notion client
    notion = Client(auth=NOTION_TOKEN)

    # Get pages from last week
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Date", 
            "date": {
                "past_week": {}
            }
        }
    )
    
    entries = response.get("results", [])

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

        new_entry = {
            'Split': {
                'type': 'select',
                'select': ''
            },
            'Reps': {

            },
            'lbs': {

            }

        }

        result = notion.pages.create(
            parent={
                "database_id": DATABASE_ID
            },
            properties=entry['properties']
        )

        print(result)
