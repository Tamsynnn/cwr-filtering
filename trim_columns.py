import pandas as pd

# Import csv file to pandas DataFrame
input_file = 'data/collated_data_20230122_uid.csv'
data = pd.read_csv(input_file, dtype=str)

# Read column names to keep, and convert into Python list
column_names = pd.read_excel('data/Column_names.xlsx', header=None).iloc[:,0].values.tolist()

# Drop unwanted columns
data = data[column_names]

# Output to csv
data.to_csv('data/collated_data_20230122_uid_columns.csv')
