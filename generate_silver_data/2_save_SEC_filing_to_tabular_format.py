#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import json
import pandas as pd
pd.set_option('display.max_colwidth', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

# Step 1: Read the CSV file
csv_file_base_path = '/Users/zealot/Documents/SECv3/output/'

# Initialize a list to store the JSON contents
records = []

for root, dirs, files in os.walk(csv_file_base_path):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    records.append({
                        "form_type": "10-K",
                        "summary_text": "",  # Optionally save the file path
                        "sec_raw_content": data          # Save the whole JSON as one field
                    })
                print(f"Successfully read {file_path}")
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
# Convert the list into a DataFrame
df = pd.DataFrame(records)

# Show the result
print(df.head())