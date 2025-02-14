import re
import pandas as pd
from dateutil import parser


def preprocess(data):
    # Regex pattern to match multiple date formats
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:AM\s|PM\s|am\s|pm\s)?-\s'


    # Extract messages and timestamps
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    print("EXTRACTED DATES:", dates[:5])  # Debugging timestamps
    print("EXTRACTED MESSAGES:", messages[:5])  # Debugging messages

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean up date format
    df['message_date'] = df['message_date'].astype(str).str.strip(" -").str.replace("\u202F", " ", regex=True)

    # Auto-detect and convert datetime
    df['date'] = df['message_date'].apply(lambda x: parser.parse(x) if x else pd.NaT)

    # Convert to datetime (in case there are any parsing issues)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])

    df.drop(columns=['message_date'], inplace=True)

    # Extract user and message content
    users, messages = [], []
    for message in df['user_message']:
        entry = re.split(r'([^:]+):\s', message, maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1].strip())
            messages.append(entry[2].strip())
        else:
            print("Skipping unrecognized format:", message)  # Debugging
            users.append('group_notification')
            messages.append(entry[0].strip())

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date-time components
    df['Day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Define time periods
    df['period'] = df['Hour'].apply(lambda h: f"{h}-00" if h == 23 else ("00-01" if h == 0 else f"{h}-{h + 1}"))

    return df
