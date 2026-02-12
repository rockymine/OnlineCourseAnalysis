# run with: py .\src\data\preprocess.py in the terminal

import pandas as pd
from datetime import datetime


def convert_to_seconds(time_str):
    time_str = str(time_str)
    if time_str == 'nan' or time_str == '':
        return 0
    # Handle timedelta format like "0 days 00:01:29"
    if 'days' in time_str:
        time_str = time_str.split('days')[-1].strip()
    # Handle possible fractional seconds like "00:01:29.000000"
    time_str = time_str.split('.')[0]
    t = datetime.strptime(time_str, "%H:%M:%S")
    return t.hour*3600 + t.minute*60 + t.second


def rename_columns(df):
    df = df.rename(columns={'media_type': 'building_block', 'media_type_short': 'building_block_short',
                            'video_length': 'video_duration', 'code_rows': 'code_rows_count', 'tab_count': 'table_count'})
    return df


def create_building_block_short_column(df):
    df['building_block_short'] = df['building_block'].apply(lambda x: x[0].lower() if pd.notnull(x) else '')
    return df


def process_durations(df):
    df['video_duration'] = df['video_duration'].astype(str).apply(convert_to_seconds)
    df['estimated_completion_time'] = df['estimated_completion_time'].astype(str).apply(convert_to_seconds)
    return df


def split_audio_video_duration(df):
    df['audio_duration'] = df.apply(lambda row: row['video_duration'] if row['building_block'] == 'Audio' else 0, axis=1)
    df['video_duration'] = df.apply(lambda row: row['video_duration'] if row['building_block'] != 'Audio' else 0, axis=1)
    return df


def create_unit_parts_columns(df):
    df['unit'] = df['unit'].astype(str)
    df['chapter'] = df['unit'].str.split('.').str[0]
    df['section'] = df['unit'].str.split('.').str[1]
    return df


def map_building_block(df):
    building_block_mapping = {
        'Aufgabe': 'Exercise',
        'Quiz': 'Exercise',
        'Test': 'Exercise',
        'Diskussion': 'Discussion',
        'Text/Diskussion': 'Text',
        'Umfrage': 'Poll',
        'Video/Audio': 'Video',
        'Selbstlern': 'Homework'
    }
    df['building_block'] = df['building_block'].replace(building_block_mapping)
    return df


def map_task_type(df):
    task_type_mapping = {
        'Nicht möglich Teilzunehmen': 'Unavailable',
        'Zuordnung': 'Mapping',
        'Programmieraufgabe': 'Coding',
        'Programming': 'Coding',
        'Programmieren': 'Coding',
        'Free Text': 'ShortAnswer',
        'Short Answer': 'ShortAnswer',
        'Hausaufgabe': 'Homework',
        'Cloze': 'ShortAnswer'
    }
    df['task_type'] = df['task_type'].replace(task_type_mapping)
    return df


def map_course_name(df):
    course_mapping = {
        'Intro to JavaScript': 'Uda-JS',
        'Classification Models': 'Uda-CM',
        'Responsive Web Design Fundamentals': 'Uda-RWD',
        'Unlocking Information Security I: From Cryptography to Buffer Overflows': 'edX-IS',
        'Agile and Scrum Fundamentals': 'edX-AS',
        'Programming for Everyone - An Introduction to Visual Programming Languages': 'edX-PL',
        'Entrepreneurship: From Business Idea to Action': 'Fut-ENT',
        'Introduction to Encription and Cryptography': 'Fut-EC',
        'Human-Computer Interaction': 'IxDF-HCI',
        'Interaction Design for Usability': 'IxDF-IDU',
        'UI Design Patterns for Successful Software': 'IxDF-UI'
    }
    df['course_name'] = df['course_name'].map(course_mapping)
    return df


def add_leading_zero(unit):
    parts = unit.split(".")
    if len(parts[1]) == 1:
        parts[1] = "0" + parts[1]
    return ".".join(parts)


def fill_missing_values(df):
    fill_values = {'word_count': 0,
                   'question_count': 0,
                   'answer_count': 0,
                   'img_count': 0,
                   'gif_count': 0,
                   'code_rows_count': 0,
                   'table_count': 0,
                   'task_type': 'NA'}
    df = df.fillna(value=fill_values)
    return df


def remove_values(df):
    # Remove entries, where task_type is 'Unavailable' or 'Homework' or 'Todo'
    df = df.loc[~(df['task_type'] == 'Unavailable')]
    df = df.loc[~(df['task_type'] == 'Homework')]
    df = df.loc[~(df['task_type'] == 'Todo')]

    # Remove entries, where building_block is 'Homework'
    df = df.loc[~(df['building_block'] == 'Homework')]
    return df


def preprocess_data(raw_data_filepath, processed_data_filepath):
    # Load course data
    df = pd.read_excel(raw_data_filepath, dtype={'unit': 'str'})

    # modify unit column
    df['unit'] = df['unit'].apply(add_leading_zero)
    df['unit'] = df['unit'].str.replace('.', '_')

    # Rename columns
    df = rename_columns(df)

    # Map the values
    df = map_building_block(df)
    df = map_task_type(df)
    df = map_course_name(df)

    # Remove some entries
    df = remove_values(df)

    # Convert durations into seconds
    df = process_durations(df)

    # Populate the 'building_block_short' column
    df = create_building_block_short_column(df)

    # Create 'audio_duration' column and update 'video_duration' column
    df = split_audio_video_duration(df)

    # Fill missing values
    df = fill_missing_values(df)

    # group images and gifs
    df['graphics_count'] = df['img_count'].astype(int) + df['gif_count'].astype(int)

    # Save the processed data
    df.to_csv(processed_data_filepath, index=False)


def raw_video_data(raw_data_filepath, processed_data_filepath):
    df = pd.read_csv(raw_data_filepath)
    df_filtered = df[df['video_duration'] > 0][['provider_name', 'course_name', 'video_duration']]

    new_df = df_filtered.groupby(['provider_name', 'course_name']).agg({
        'video_duration': [
            ('avg_video_duration', 'mean'),
            ('up_to_six', lambda x: (x <= 360).sum()),
            ('six_to_twelve', lambda x: ((x > 360) & (x <= 720)).sum()),
            ('more_than_twelve', lambda x: (x > 720).sum())
        ]
    }).reset_index()

    # Flatten the column names
    new_df.columns = ['provider', 'course', 'avg_video_duration', 'up_to_six', 'six_to_twelve',
                      'more_than_twelve']

    # Calculate total videos per course
    new_df['total_videos'] = new_df['up_to_six'] + new_df['six_to_twelve'] + new_df['more_than_twelve']

    # Calculate percentages
    new_df['pct_up_to_six'] = new_df['up_to_six'] / new_df['total_videos'] * 100
    new_df['pct_six_to_twelve'] = new_df['six_to_twelve'] / new_df['total_videos'] * 100
    new_df['pct_more_than_twelve'] = new_df['more_than_twelve'] / new_df['total_videos'] * 100

    # Round percentages to two decimal places
    new_df[['pct_up_to_six', 'pct_six_to_twelve', 'pct_more_than_twelve']] = new_df[
        ['pct_up_to_six', 'pct_six_to_twelve', 'pct_more_than_twelve']].round(2)

    new_df['avg_video_duration'] = (new_df['avg_video_duration'] / 60).round(2)

    new_df.to_csv(processed_data_filepath, index=False)


if __name__ == '__main__':
    preprocess_data('data/raw/coursedata.xlsx', 'data/processed/cleaned_data.csv')
    raw_video_data('data/processed/cleaned_data.csv', 'data/processed/raw_video_data.csv')
