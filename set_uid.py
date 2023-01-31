import pandas as pd

# Import csv file to pandas DataFrame
input_file = 'data/collated_data_20230122.csv'
data = pd.read_csv(input_file, dtype=str)


# Define a function to add 'uuid_' to the front of each row number
def format_uid(uid):
    return f'uid_{uid}'


# Add row numbers to 'Unique-ID' field, then apply format_iud
data['Unique_ID'] = data.index
data['Unique_ID'] = data['Unique_ID'].apply(format_uid)

# Output DataFrame to csv
output_file = 'data/collated_data_20230122_uid.csv'
data.to_csv(output_file)