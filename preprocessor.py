import re
import pandas as pd


def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create DataFrame with message and date
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean up the date format (if needed, ensure it's a string first)
    # Make sure 'message_date' is a string before calling str.strip()
    df['message_date'] = df['message_date'].astype(str).str.strip(" - ")

    # Convert the 'message_date' to datetime
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M', errors='coerce')

    # Rename 'message_date' to 'date'
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Prepare lists for users and messages
    users = []
    msg_contents = []

    # Split the messages by user and content
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if len(entry) > 2:
            users.append(entry[1])
            msg_contents.append("".join(entry[2:]))
        else:
            users.append('group_notification')
            msg_contents.append(entry[0])

    # Add the 'user' and 'message' columns
    df['user'] = users
    df['message'] = msg_contents

    # Drop 'user_message' column
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional date-time components
    df['Day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Efficiently create the 'period' column
    df['period'] = df['Hour'].apply(lambda x: f"{x:02d}-{(x + 1) % 24:02d}")

    return df
