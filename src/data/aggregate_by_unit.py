import pandas as pd
import math


def create_text_duration_column(df):
    df['text_duration'] = df['word_count'].apply(calculate_text_duration)
    return df


def calculate_text_duration(word_count):
    if word_count == 0:
        return 0
    else:
        # reading speed of 160 wpm is assumed
        return math.ceil(word_count / 150) * 60


def create_media_duration_column(df):
    df['media_duration'] = df['audio_duration'] + df['video_duration'] + df['text_duration']
    return df


def filter_building_blocks(string):
    chars = list(string)
    filtered = []

    for char in chars:
        if len(filtered) == 0 or filtered[-1] != char:
            filtered.append(char)

    result = ''.join(filtered)
    return result


def filter_unique_building_blocks(string):
    chars = list(string)
    filtered = []

    for char in chars:
        if len(filtered) == 0 or char not in filtered:
            filtered.append(char)

    result = ''.join(sorted(filtered))
    return result


def classify_combination(s):
    media_count = sum([1 for char in s if char in ['v', 'a', 't']])
    interaction_count = sum([1 for char in s if char in ['d', 'e', 'p']])
    return f"{media_count}-media-{interaction_count}-interaction"


def create_building_block_columns(df):
    # Find unique building blocks
    building_blocks = ['v', 'a', 't', 'e', 'd', 'p', 'h']

    # Create a new column for each building block and count appearance
    for building_block in building_blocks:
        column = building_block + '_count'
        df[column] = df['unit_structure'].apply(lambda x: x.count(building_block))

    # Count building blocks
    df['building_block_count'] = df['unit_structure'].apply(len)

    # Filter unit structure
    df['unit_structure_filtered'] = df['unit_structure'].apply(filter_building_blocks)

    # Count building block changes
    df['building_block_changes_count'] = df['unit_structure_filtered'].apply(lambda x: len(x) - 1)

    # Filter unique building blocks
    df['building_block_unique'] = df['unit_structure'].apply(filter_unique_building_blocks)

    # Determine media interaction combination on a high level
    df['media_interaction_combination'] = df['building_block_unique'].apply(classify_combination)

    # Get unique media_interaction_combination values
    combinations = df['media_interaction_combination'].unique()

    # Create a new column for each combination and count occurrence
    for combination in combinations:
        column = combination.replace('-', '_')  # Replace '-' with '_' to create valid column names
        df[column + '_count'] = df['media_interaction_combination'].apply(lambda x: x.count(combination))

    # Count unique building blocks
    df['building_block_unique_count'] = df['building_block_unique'].apply(len)

    return df


def calculate_exercise_duration(df):
    # Define mapping from task_type to time factor
    time_factor = {
        'Essay': 1800,
        'Coding': 1800,
        'Mapping': 300,
        'Choice': 300,
        'ShortAnswer': 120
    }

    # Calculate 'exercise_duration' where 'building_block' is 'Exercise'
    df.loc[df['building_block'] == 'Exercise', 'exercise_duration'] = df['question_count'] * df['task_type'].map(time_factor)

    # Fill NaN values in 'exercise_duration' column with 0
    df['exercise_duration'] = df['exercise_duration'].fillna(0)

    return df


def create_exercise_position_columns(df):
    s = df['unit_structure_filtered']

    df['has_exercises'] = s.str.contains('e', regex=False)
    df['only_exercises'] = s == 'e'
    df['multiple_exercise_blocks'] = df['has_exercises'] & (s.str.count('e') > 1)
    df['starts_with_exercise'] = df['has_exercises'] & ~df['only_exercises'] & s.str.startswith('e')
    df['ends_with_exercise'] = df['has_exercises'] & ~df['only_exercises'] & s.str.endswith('e')
    df['exercises_in_middle'] = df['has_exercises'] & ~df['only_exercises'] & s.str.slice(1, -1).str.contains('e', regex=False)

    return df


def calculate_interaction_duration(df):
    df['poll_duration'] = df['p_count'] * 120
    df['discussion_duration'] = df['d_count'] * 300
    df['interaction_duration'] = df['exercise_duration'] + df['poll_duration'] + df['discussion_duration']

    return df


def calculate_unit_duration(df):
    df['unit_duration'] = df['media_duration'] + df['interaction_duration']
    return df


def calculate_estimated_completion_time(df):
    df['completion_time'] = df['text_duration'] + 2 * (df['video_duration'] + df['audio_duration']) + df['interaction_duration']
    return df


def group_and_aggregate(df):
    df_agg = df.groupby(['provider_name', 'course_name', 'unit']).agg(
        unit_structure=('building_block_short', lambda x: ''.join(x.astype(str))),
        video_duration=('video_duration', 'sum'),
        audio_duration=('audio_duration', 'sum'),
        word_count=('word_count', 'sum'),
        choice_count=('question_count', lambda x: x[df['task_type'] == 'Choice'].sum()),
        coding_count=('question_count', lambda x: x[df['task_type'] == 'Coding'].sum()),
        mapping_count=('question_count', lambda x: x[df['task_type'] == 'Mapping'].sum()),
        essay_count=('question_count', lambda x: x[df['task_type'] == 'Essay'].sum()),
        short_answer_count=('question_count', lambda x: x[df['task_type'] == 'ShortAnswer'].sum()),
        exercise_duration=('exercise_duration', 'sum'),
        graphics_count=('graphics_count', 'sum'),
        code_rows_count=('code_rows_count', 'sum'),
        table_count=('table_count', 'sum'),
        multi_codal=('multi_codal', lambda x: (x > 0).any())
    ).reset_index()
    return df_agg


def calculate_video_proportion(df):
    """
    Calculate the proportion of video content for each row in the DataFrame.
    The proportion is calculated as 'video_duration' divided by 'media_duration'.
    If 'media_duration' is 0, the proportion is set to NaN.
    If 'video_duration' is 0, the proportion is set to 0.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing course data.
                           It must have 'video_duration' and 'media_duration' columns.

    Returns:
    pandas.DataFrame: The same DataFrame passed as input, but with an additional 'video_proportion' column.
    """
    df['video_proportion'] = df.apply(lambda row: float('nan') if row['media_duration'] == 0 else (
        0 if row['video_duration'] == 0 else row['video_duration'] / row['media_duration']), axis=1)
    return df


def calculate_media_proportion(df):
    """
    Calculate the proportion of media content for each row in the DataFrame.
    The proportion is calculated as 'media_duration' divided by 'completion_time'.
    If 'media_duration' is 0, the proportion is set to 0.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing course data.
                           It must have 'media_duration' and 'completion_time' columns.

    Returns:
    pandas.DataFrame: The same DataFrame passed as input, but with an additional 'media_proportion' column.
    """
    df['media_proportion'] = df.apply(lambda row: (row['text_duration'] + 2 * (row['audio_duration'] + row['video_duration'])) / row['completion_time'] if row['media_duration'] > 0 else 0, axis=1)
    return df


def reorder_columns(df):
    """
    Reorders the columns in the DataFrame according to a defined order.
    The columns are ordered by identifiers, unit structure, building block counts, durations, and proportions.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing course data.

    Returns:
    pandas.DataFrame: The same DataFrame passed as input, but with columns reordered.
    """
    columns_order = ['provider_name', 'course_name', 'unit', 'chapter', 'section', 'unit_structure',
                     'unit_structure_filtered', 'building_block_unique', 'media_interaction_combination',
                     'building_block_count', 'building_block_changes_count', 'building_block_unique_count',
                     'has_exercises', 'only_exercises', 'multiple_exercise_blocks', 'starts_with_exercise',
                     'exercises_in_middle', 'ends_with_exercise', 'v_count', 'a_count', 't_count', 'e_count', 'd_count',
                     'p_count', 'h_count', 'choice_count', 'coding_count', 'mapping_count',
                     'essay_count', 'short_answer_count', 'video_duration', 'audio_duration', 'word_count',
                     'text_duration',
                     'exercise_duration', 'poll_duration',  'discussion_duration', 'interaction_duration',
                     'media_duration', 'unit_duration', 'completion_time', 'video_proportion', 'media_proportion',
                     'interaction_count', 'interaction_density', 'interaction_density_other',
                     '0_media_1_interaction_count',
                     '0_media_2_interaction_count',
                     '1_media_0_interaction_count',
                     '1_media_1_interaction_count',
                     '1_media_2_interaction_count',
                     '1_media_3_interaction_count',
                     '2_media_0_interaction_count',
                     '2_media_1_interaction_count',
                     '2_media_2_interaction_count',
                     '2_media_3_interaction_count',
                     'graphics_count', 'code_rows_count', 'table_count', 'multi_codal']

    df_reordered = df.reindex(columns=columns_order)

    return df_reordered


def create_unit_parts_columns(df):
    """
    Splits the column 'unit' into the columns 'chapter' and 'section'.

    Parameters:
    df (pandas.DataFrame): A Dataframe containing course data.
                           It must have the 'unit' column.

    Returns:
    pandas.DataFrame: The same DataFrame passed as input, but with additional 'chapter' and 'section' column.
    """
    df['unit'] = df['unit'].astype(str)
    df['chapter'] = df['unit'].str.split('_').str[0]
    df['section'] = df['unit'].str.split('_').str[1]
    return df


def create_interaction_columns(df):
    """
    Calculates 'interaction_count' and 'interaction_density' for each learning unit.

    Parameters:
    df (pandas.DataFrame): A Dataframe containing course data.
                           It must have the 'e_count', 'd_count', and 'p_count' column.

    Returns:
    pandas.DataFrame: The same DataFrame passed as input, but with additional 'interaction_count' and
                      'interaction_density' column.
    """

    df['interaction_count'] = df[['choice_count', 'coding_count', 'essay_count', 'short_answer_count', 'mapping_count',
                                  'd_count', 'p_count']].sum(axis=1)
    df['interaction_density'] = df['interaction_duration'] / df['unit_duration']
    df['interaction_density_other'] = df['interaction_count'] / (df['unit_duration'] / 60)

    return df


def aggregate_data(input_filepath, output_filepath):
    df = pd.read_csv(input_filepath, dtype={
        'provider_name': 'str',
        'course_name': 'str',
        'unit': 'str',
        'estimated_completion_time': 'int',
        'building_block': 'str',
        'building_block_short': 'str',
        'video_duration': 'int',
        'word_count': 'int',
        'task_type': 'str',
        'question_count': 'int',
        'answer_count': 'int',
        'audio_duration': 'int',
        'code_rows_count': 'int',
        'graphics_count': 'int',
        'table_count': 'int'
    })

    df['multi_codal'] = (df['code_rows_count'] + df['graphics_count'] + df['table_count']) > 0

    # Calculate exercise duration
    df = calculate_exercise_duration(df)

    # Group data by unit
    df_agg = group_and_aggregate(df)

    # Calculate text duration
    df_agg = create_text_duration_column(df_agg)

    # Calculate media duration
    df_agg = create_media_duration_column(df_agg)

    # Count building block appearance
    df_agg = create_building_block_columns(df_agg)

    # Calculate interaction duration
    df_agg = calculate_interaction_duration(df_agg)

    # Calculate unit duration
    df_agg = calculate_unit_duration(df_agg)

    # Calculate estimated completion time
    df_agg = calculate_estimated_completion_time(df_agg)

    # Calculate video proportion
    df_agg = calculate_video_proportion(df_agg)

    # Calculate media proportion
    df_agg = calculate_media_proportion(df_agg)

    # Create exercise position columns
    df_agg = create_exercise_position_columns(df_agg)

    # Create 'chapter' and 'section' columns
    df_agg = create_unit_parts_columns(df_agg)

    # Create 'interaction_count' and 'interaction_density' columns
    df_agg = create_interaction_columns(df_agg)

    # Reorder columns
    df_agg = reorder_columns(df_agg)

    # Save the grouped data
    df_agg.to_csv(output_filepath, index=False)


def create_type_transition_summary(input_filepath, output_filepath):
    df = pd.read_csv(input_filepath)

    filtered_df = df[df['unit_structure'].str.len() > 0]

    characters = ['S','v', 't', 'a', 'd', 'p', 'e', 'E']
    matrix = [[0] * len(characters) for _ in range(len(characters))]

    for string in filtered_df['unit_structure']:  # Iterate over each unit_structure individually
        # Add 'S' at the beginning and 'E' at the end of the string
        string = 'S' + string + 'E'

        for i in range(len(string) - 1):
            current_char = string[i]
            next_char = string[i + 1]

            if current_char in characters and next_char in characters:
                current_index = characters.index(current_char)
                next_index = characters.index(next_char)
                matrix[current_index][next_index] += 1

    transitions = []
    probabilities = []
    counts = []

    for i, current_char in enumerate(characters):
        for j, next_char in enumerate(characters):
            transition = current_char + next_char
            probability = 0

            if sum(matrix[i]) > 0:
                probability = matrix[i][j] / sum(matrix[i])

            # probability = matrix[i][j] / sum(matrix[i])
            count = matrix[i][j]
            transitions.append(transition)
            probabilities.append(probability)
            counts.append(count)

    result_df = pd.DataFrame({'transition': transitions, 'probability': probabilities, 'count': counts})
    result_df = result_df.sort_values(by='probability', ascending=False).reset_index(drop=True)

    #result_df.to_csv(output_filepath, index=False)


    # # Convert counts to probabilities
    for i in range(len(characters)):
         row_sum = sum(matrix[i])
         if row_sum > 0:
             matrix[i] = [count / row_sum for count in matrix[i]]
         # Add a 'Sum' column that totals the probabilities for each state (should equal 1 if there are no rounding errors)
         matrix[i].append(sum(matrix[i]))

    # # Create a DataFrame from the matrix
    matrix_df = pd.DataFrame(matrix, columns=characters + ['Sum'], index=characters)
    #
    # # Save to CSV
    matrix_df.to_csv(output_filepath)


def create_type_transition_summary_provider(input_filepath, provider, output_filepath):
    df = pd.read_csv(input_filepath)
    df = df[df['provider_name'] == provider]

    filtered_df = df[df['unit_structure'].str.len() > 0]

    characters = ['S','v', 't', 'a', 'd', 'p', 'e', 'E']
    matrix = [[0] * len(characters) for _ in range(len(characters))]

    for string in filtered_df['unit_structure']:  # Iterate over each unit_structure individually
        # Add 'S' at the beginning and 'E' at the end of the string
        string = 'S' + string + 'E'

        for i in range(len(string) - 1):
            current_char = string[i]
            next_char = string[i + 1]

            if current_char in characters and next_char in characters:
                current_index = characters.index(current_char)
                next_index = characters.index(next_char)
                matrix[current_index][next_index] += 1

    transitions = []
    probabilities = []
    counts = []

    for i, current_char in enumerate(characters):
        for j, next_char in enumerate(characters):
            transition = current_char + next_char
            probability = 0

            if sum(matrix[i]) > 0:
                probability = matrix[i][j] / sum(matrix[i])

            # probability = matrix[i][j] / sum(matrix[i])
            count = matrix[i][j]
            transitions.append(transition)
            probabilities.append(probability)
            counts.append(count)

    result_df = pd.DataFrame({'transition': transitions, 'probability': probabilities, 'count': counts})
    result_df = result_df.sort_values(by='probability', ascending=False).reset_index(drop=True)


    # # Convert counts to probabilities
    for i in range(len(characters)):
         row_sum = sum(matrix[i])
         if row_sum > 0:
             matrix[i] = [count / row_sum for count in matrix[i]]
         # Add a 'Sum' column that totals the probabilities for each state (should equal 1 if there are no rounding errors)
         matrix[i].append(sum(matrix[i]))

    # # Create a DataFrame from the matrix
    matrix_df = pd.DataFrame(matrix, columns=characters + ['Sum'], index=characters)
    #
    # # Save to CSV
    matrix_df.to_csv(output_filepath)


if __name__ == '__main__':
    aggregate_data('data/processed/cleaned_data.csv', 'data/processed/aggregated_by_unit_data.csv')
    #create_type_transition_summary('data/processed/aggregated_by_unit_data.csv', 'data/processed/type_transition.csv')
    #create_type_transition_summary_provider('data/processed/aggregated_by_unit_data.csv', 'IxDF',
    #                                        'data/processed/type_transition_idf.csv')
    #create_type_transition_summary_provider('data/processed/aggregated_by_unit_data.csv', 'Udacity',
    #                                        'data/processed/type_transition_uda.csv')
    #create_type_transition_summary_provider('data/processed/aggregated_by_unit_data.csv', 'FutureLearn',
    #                                        'data/processed/type_transition_fut.csv')
    #create_type_transition_summary_provider('data/processed/aggregated_by_unit_data.csv', 'edX',
    #                                        'data/processed/type_transition_edx.csv')
