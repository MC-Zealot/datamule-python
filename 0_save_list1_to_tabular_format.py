#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

# Step 1: Read the CSV file
csv_file_path = 'apollo-contacts-export.csv'
df = pd.read_csv(csv_file_path)

# Step 2: Display the loaded data
print("Data read from CSV:")
print(df.head())  # Print only the first 5 rows to quickly check the content

# Step 3: Save the data in tabular format (as a new CSV file)
# tabular_file_path = '/mnt/data/apollo_contacts_tabular.csv'
# df.to_csv(tabular_file_path, index=False)

# Optional: If you want to double-check the saved file, you can reload it
# df_check = pd.read_csv(tabular_file_path)
# print("Saved tabular file:")
# print(df_check)
