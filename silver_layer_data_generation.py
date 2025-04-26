#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json

# 目录路径
directory_path = "data/result_10-K_0001808834_IPRG"

# 获取目录下所有文件
for filename in os.listdir(directory_path):

    filing_type = directory_path.split("_")[1]
    cik_number = directory_path.split("_")[2]

    # check file is JSON file
    if filename.endswith(".json"):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)  # load JSON file
            print(f"Data from {filename}:")
            filing_date = filename.replace(".json", "")
            # print(json.dumps(data, ensure_ascii=False, indent=4))
            introduction = data['document']['introduction'] #TODO: generate summary
            risk_factors_origin = data['document']['parti']['item1a'] #TODO: generate risk_factors

            financial_statements = data['document']['partii']['item8'] #TODO: generate float attribute

            fund_validation_risk_factor_origin = data['document']['partii']['item7a'] #TODO: generate fund_validation_risk_factor
            print("aaa")
