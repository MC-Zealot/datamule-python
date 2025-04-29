#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

# Step 1: Read the CSV file
csv_file_path = 'apollo-contacts-export.csv'
apollo_lead_df = pd.read_csv(csv_file_path)

# Step 2: Display the loaded data
print("Data read from CSV:")
print(apollo_lead_df.head())  # Print only the first 5 rows to quickly check the content

