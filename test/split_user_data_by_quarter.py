import pandas as pd
import os

# base_dir=""
# Step 1: Read test1.csv and generate 'included_quarters'
df1 = pd.read_csv("/Users/zealot/Downloads/ft/Output-1.csv", parse_dates=["last_visit"])

# ✅ Filter out rows with negative days_since_last
df1 = df1[df1["days_since_last"] >= 0]

def get_quarter_with_year_format(date):
    if pd.isnull(date):
        return ""
    quarter = (date.month - 1) // 3 + 1
    year = date.year
    return f"{year}Q{quarter}"

df1["included_quarters"] = df1["last_visit"].apply(get_quarter_with_year_format)

# Build dictionary: loyalty_guest_id → included_quarters
id_to_quarter = dict(zip(df1["loyalty_guest_id"], df1["included_quarters"]))

# Step 2: Read test2.csv and test3.csv, and map quarters
df2 = pd.read_csv("/Users/zealot/Downloads/ft/Output-2.csv")
df3 = pd.read_csv("/Users/zealot/Downloads/ft/Output-3.csv")

df2["included_quarters"] = df2[df2.columns[0]].map(id_to_quarter)
df3["included_quarters"] = df3["guest_profile_id"].map(id_to_quarter)

# Step 2.5: Save unmatched rows to separate CSVs
unmatched_df2 = df2[df2["included_quarters"].isna()]
unmatched_df3 = df3[df3["included_quarters"].isna()]

if not unmatched_df2.empty:
    unmatched_df2.to_csv("/Users/zealot/Downloads/ft/split_all_by_quarter/Output-2_unmatched.csv", index=False)

if not unmatched_df3.empty:
    unmatched_df3.to_csv("/Users/zealot/Downloads/ft/split_all_by_quarter/Output-3_unmatched.csv", index=False)

# Step 3: Save updated full files
# df1.to_csv("/Users/zealot/Downloads/ft/updated_test1.csv", index=False)
# df2.to_csv("/Users/zealot/Downloads/ft/updated_test2.csv", index=False)
# df3.to_csv("/Users/zealot/Downloads/ft/updated_test3.csv", index=False)

# Step 4: Split all 3 files by quarter
output_dir = "/Users/zealot/Downloads/ft/split_all_by_quarter"
os.makedirs(output_dir, exist_ok=True)

quarters = sorted(set(df1["included_quarters"].dropna()))

for q in quarters:
    df1_q = df1[df1["included_quarters"] == q]
    df2_q = df2[df2["included_quarters"] == q]
    df3_q = df3[df3["included_quarters"] == q]

    df1_q.to_csv(f"{output_dir}/Output-1_{q}.csv", index=False)
    df2_q.to_csv(f"{output_dir}/Output-2_{q}.csv", index=False)
    df3_q.to_csv(f"{output_dir}/Output-3_{q}.csv", index=False)
