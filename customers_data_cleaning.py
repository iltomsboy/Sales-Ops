import pandas as pd
import numpy as np
from datetime import datetime

#Load raw customers data
df = pd.read_csv('C:\\Users\\Toms\\Desktop\\SALES OPS\\Data Cleaning Customers\\raw_customers.csv')
print(df.head())

# Step 1: Identify data quality issues
def data_quality_check(df):
    quality_report = {
        'total_record': len(df),
        'duplicate_rows': df.duplicated().sum(),
        'missing_values': df.isnull().to_dict(),
        'invalid_emails': df[~df['email'].str.contains('@', na = False)].shape[0],
        'invalid_ages': df[(df['age'] < 0) | (df['age'] > 120)].shape[0]
    }
    return quality_report

quality_report = data_quality_check(df)
print(quality_report)

# Step 2: Remove duplicates
df_clean = df.copy()
initial_count = len(df_clean)
df_clean = df_clean.drop_duplicates(subset = ['customer_idd', 'email'], keep = 'first')
duplicates_removed = initial_count - len(df_clean)
print(f'Duplicates removed: {duplicates_removed}')

# Step 3: Standardize text formatting
df_clean['first_name'] = df_clean['first_name'].str.strip().str.title()
df_clean['last_name'] = df_clean['last_name'].str.strip().str.title()
df_clean['email'] = df_clean['email'].str.strip().str.lower()
df_clean['city'] = df_clean['city'].str.strip().str.title()
df_clean['phone'] = df_clean['phone'].str.strip()

print(df_clean[['first_name', 'last_name', 'email']].head())

# Step 4: Handle missing values
df_clean['phone'] = df_clean['phone'].fillna('Not provided!')
df_clean['city'] = df_clean['city'].fillna('Unknown!')
df_clean['age'].fillna(0)

missing_summary = df_clean.isnull().sum()
print(f'Remaining nulls: \n{missing_summary}')

# Step 5: Filter invalid records
initial_count = len(df_clean)
df_clean = df_clean[df_clean['email'].str.contains('@', na = False)]
df_clean = df_clean[(df_clean['age'] >= 0) & (df['age'] <= 120)]
df_clean = df_clean[df_clean['email'].notna()]

invalid_removed = initial_count - len(df_clean)
print(f'Invalid records removed: {invalid_removed}')

# Step 6: Enrich with calculated fields
df_clean['full_name'] = df['first_name'] + ' ' + df_clean['last_name']
df_clean['registration_date'] = pd.to_datetime(df_clean['registration_date'], errors = 'coerce')
df_clean['days_since_registration'] = (datetime.now() - df_clean['registration_date']).dt.days

print(df_clean[['full_name', 'registration_date', 'days_since_registration']].head())

# Step 7:
df_clean['data_quality_flag'] = np.where(
    (df_clean['phone'] == 'Not provided!') | (df_clean['city'] == 'Unknown!'),
    'Incomplete',
    'Complete'
)

quality_distribution = df_clean['data_quality_flag'].value_counts()
print(quality_distribution)

# Validation: before and after comparison
print('\n--- DATA CLEANING SUMMARY ---')
print(f'Original records: {len(df)}')
print(f'Clean records: {len(df_clean)}')
print(f'Records removed: {len(df) - len(df_clean)}')
print(f'Data quality distribution:\n{quality_distribution}')

# Export cleaned data
df_clean.to_csv('clean_customers.csv', index = False)
print('\nCleaned data exported to "clean_customers.csv"')

# Final data preview
print('\n--- CLEANDE DATA PREVIEW ---')
print(df_clean.head(12))

# the end