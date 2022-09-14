import pandas as pd
import numpy as np
import datetime

INT_THEN_STRING_COLUMNS = ['key_mlbam', 'key_fangraphs']
STRING_KEY_COLUMNS = ["key_retro", "key_bbref", "key_bbref_minors"]
DISCARD_COLUMNS = [
    "key_npb", "key_sr_nfl", "key_sr_nhl", "key_sr_nba", 'key_findagrave',
    'pro_managed_first', 'pro_managed_last', 'mlb_managed_first', 'mlb_managed_last', 'col_managed_first', 'col_managed_last',
    'pro_umpired_first', 'pro_umpired_last', 'mlb_umpired_first', 'mlb_umpired_last'
]
INT64_COLUMNS = [
    'birth_year', 'birth_month', 'birth_day',
    'death_year', 'death_month', 'death_day',
    'pro_played_first', 'pro_played_last',
    'mlb_played_first', 'mlb_played_last',
    'col_played_first', 'col_played_last'
]
rename = {
    'key_retro': 'retro_id',
    'key_bbref': 'bbref_id',
    'key_bbref_minors': 'bbref_minors_id',
    'key_mlbam': 'mlb_id',
    'key_fangraphs': 'fangraphs_id',
    'key_uuid': 'register_uuid',
    'key_person': 'register_id',
}


df = pd.read_csv('data/people.csv')

df = df.drop(DISCARD_COLUMNS, axis=1)

# remove players who never played pro ball
df = df[~df['pro_played_first'].isnull()]

# convert floats to truncated strings, replacing nulls with empty string
for column in INT_THEN_STRING_COLUMNS:
    df[column] = df[column].fillna(0)
    df[column] = df[column].astype(int)
    df[column] = df[column].astype(str)
    df[column] = df[column].replace('0', '')


# convert key_retro, key_bbref, key_bbref_minors to string
# replacing null values with empty string
for column in STRING_KEY_COLUMNS:
    df[column] = df[column].fillna('')
    df[column] = df[column].astype(str)

for column in INT64_COLUMNS:
    df[column] = df[column].astype('Int64')


# create birth_date column, and fill in missing values
def create_birth_date(row):
    birth_year = row['birth_year']
    birth_month = row['birth_month']
    birth_day = row['birth_day']

    if pd.isna(birth_year) or pd.isna(birth_month) or pd.isna(birth_day):
        return None
    else:
        return datetime.date(birth_year, birth_month, birth_day)


def combine_name(row):
    first = row['name_first']
    last = row['name_last']
    if pd.isna(first):
        return ""
    if pd.isna(last):
        return ""

    return first + ' ' + last


def set_active(row):
    if row['pro_played_last'] == datetime.date.today().year:
        return True
    else:
        return False


# name info from register seems inaccurate, so we'll assign it to a different property
# may be useful, but we'll prefer the name according to the MLB API.
df['register_name'] = df.apply(combine_name, axis=1)
df.drop(['name_first', 'name_last', 'name_given', 'name_suffix',
        'name_matrilineal', 'name_nick'], axis=1, inplace=True)

# assign birth_date column, returning None if not all values are present
# drop birth_month and birth_day either way - inaccurate data will be lost here
df['birth_date'] = df.apply(create_birth_date, axis=1)
df.drop(['birth_month', 'birth_day'], axis=1, inplace=True)

# assign active column according to pro_played_last
df['register_active'] = df.apply(set_active, axis=1)

# rename columns in df according to rename dict
df.rename(columns=rename, inplace=True)

print(df.head())

df.to_csv('data/people_processed.csv', index=False)

only_active = df[df['pro_played_last'] == datetime.date.today().year]
only_active.to_csv('data/people_processed_active.csv', index=False)
