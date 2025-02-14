import re
import pandas as pd


def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s'


    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    print("EXTRACTED DATES:", dates[:5])  # Print first 5 timestamps
    print("EXTRACTED MESSAGES:", messages[:5])  # Print first 5 messages

    # Create DataFrame with message and date
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean up the date format
    df['message_date'] = df['message_date'].astype(str).str.strip(" - ")
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p')


    # Rename 'message_date' to 'date'
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Prepare lists for users and messages
    users = []
    messages = []

    # Split the messages by user and content
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if len(entry) > 2:
            users.append(entry[1])
            messages.append("".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    # Add the 'user' and 'message' columns
    df['user'] = users
    df['message'] = messages

    # Drop 'user_message' column
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional date-time components
    df['Day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for _, Hour in df[['Day_name', 'Hour']].values:
        if Hour == 23:
            period.append(str(Hour) + "-00")
        elif Hour == 0:
            period.append("00-01")
        else:
            period.append(str(Hour) + "-" + str(Hour + 1))

    df['period'] = period

    return df
