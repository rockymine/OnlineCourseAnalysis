import pandas as pd
import numpy as np


def group_and_aggregate(df):
    df_agg = df.groupby(['provider_name', 'course_name']).agg(
        unit_count=('unit', 'nunique'),
        course_structure=('unit_structure', lambda x: '|'.join(x)),
        chapter_count=('chapter', 'nunique'),
        video_count=('v_count', 'sum'),
        text_count=('t_count', 'sum'),
        code_rows_count=('code_rows_count', 'sum'),
        graphics_count=('graphics_count', 'sum'),
        table_count=('table_count', 'sum'),
        audio_count=('a_count', 'sum'),
        discussion_count=('d_count', 'sum'),
        exercise_count=('e_count', 'sum'),
        poll_count=('p_count', 'sum'),
        interaction_count=('interaction_count', 'sum'),
        choice_count=('choice_count', 'sum'),
        coding_count=('coding_count', 'sum'),
        mapping_count=('mapping_count', 'sum'),
        essay_count=('essay_count', 'sum'),
        short_answer_count=('short_answer_count', 'sum'),
        video_duration=('video_duration', 'sum'),
        text_duration=('text_duration', 'sum'),
        audio_duration=('audio_duration', 'sum'),
        discussion_duration=('discussion_duration', 'sum'),
        exercise_duration=('exercise_duration', 'sum'),
        poll_duration=('poll_duration', 'sum'),
        media_duration=('media_duration', 'sum'),
        interaction_duration=('interaction_duration', 'sum'),
        unit_duration=('unit_duration', 'sum'),
        completion_time=('completion_time', 'sum'),
        zero_media_one_interaction=('0_media_1_interaction_count', 'sum'),
        zero_media_two_interaction=('0_media_2_interaction_count', 'sum'),
        one_media_zero_interaction=('1_media_0_interaction_count', 'sum'),
        one_media_one_interaction=('1_media_1_interaction_count', 'sum'),
        one_media_two_interaction=('1_media_2_interaction_count', 'sum'),
        one_media_three_interaction=('1_media_3_interaction_count', 'sum'),
        two_media_zero_interaction=('2_media_0_interaction_count', 'sum'),
        two_media_one_interaction=('2_media_1_interaction_count', 'sum'),
        two_media_two_interaction=('2_media_2_interaction_count', 'sum'),
        two_media_three_interaction=('2_media_3_interaction_count', 'sum'),
        with_video=('video_duration', lambda x: (x > 0).sum()),
        with_text=('text_duration', lambda x: (x > 0).sum()),
        with_audio=('audio_duration', lambda x: (x > 0).sum()),
        with_media=('media_duration', lambda x: (x > 0).sum()),
        with_exercise=('exercise_duration', lambda x: (x > 0).sum()),
        with_discussion=('discussion_duration', lambda x: (x > 0).sum()),
        with_poll=('poll_duration', lambda x: (x > 0).sum()),
        with_interaction=('interaction_duration', lambda x: (x > 0).sum()),
        with_graphics=('graphics_count', lambda x: (x > 0).sum()),
        with_code=('code_rows_count', lambda x: (x > 0).sum()),
        with_table=('table_count', lambda x: (x > 0).sum()),
        multi_codal=('multi_codal', 'sum'),
        only_video=('only_video', 'sum'),
        only_text=('only_text', 'sum'),
        only_text_real=('only_text_real', 'sum'),
        only_audio=('only_audio', 'sum'),
        only_exercise=('only_exercises', 'sum'),
        only_discussion=('only_discussion', 'sum'),
        only_poll=('only_poll', 'sum'),
        video_text=('video_text', 'sum'),
        video_audio=('video_audio', 'sum'),
        text_audio=('text_audio', 'sum'),
        starts_with_video=('starts_with_video', 'sum'),
        starts_with_text=('starts_with_text', 'sum'),
        starts_with_audio=('starts_with_audio', 'sum'),
        starts_with_exercise=('starts_with_exercise', 'sum'),
        exercises_in_middle=('exercises_in_middle', 'sum'),
        ends_with_exercise=('ends_with_exercise', 'sum'),
    ).reset_index()
    return df_agg


def calculate_building_block_proportions(df):
    df['video_proportion'] = df['video_duration'] / df['unit_duration']
    df['text_proportion'] = df['text_duration'] / df['unit_duration']
    df['audio_proportion'] = df['audio_duration'] / df['unit_duration']
    df['exercise_proportion'] = df['exercise_duration'] / df['unit_duration']
    df['discussion_proportion'] = df['discussion_duration'] / df['unit_duration']
    df['poll_proportion'] = df['poll_duration'] / df['unit_duration']
    return df


def calculate_exercise_variables(df):
    df = df.copy()

    # Apply each function to the 'course_structure' column
    df['e_blocks'] = df['course_structure'].apply(find_e_blocks)
    df['e_block_sizes'] = df['e_blocks'].apply(calculate_tuple_sizes)
    df['e_block_count'] = df['e_blocks'].apply(len)
    df['max_e_block_size'] = df['e_block_sizes'].apply(np.max)
    df['avg_e_block_size'] = df['e_block_sizes'].apply(np.mean)
    df['std_e_block_size'] = df['e_block_sizes'].apply(np.std)

    df['distances_between_e_blocks'] = df['e_blocks'].apply(calculate_distances_between_tuples)
    df['max_e_block_distance'] = df['distances_between_e_blocks'].apply(np.max)
    df['avg_e_block_distance'] = df['distances_between_e_blocks'].apply(np.mean)
    df['std_e_block_distance'] = df['distances_between_e_blocks'].apply(np.std)

    df['has_e'] = df['course_structure'].apply(analyze_sections)
    df['gaps_between_e_units'] = df['has_e'].apply(calculate_gaps_between_exercises)
    df['max_sections_without_e'] = df['gaps_between_e_units'].apply(np.max)
    df['avg_sections_without_e'] = df['gaps_between_e_units'].apply(np.mean)
    df['std_sections_without_e'] = df['gaps_between_e_units'].apply(np.std)

    df['e_blocks_per_section'] = df['course_structure'].apply(count_e_blocks_per_section)
    df['max_e_blocks_per_section'] = df['e_blocks_per_section'].apply(max)
    df['avg_e_blocks_per_section'] = df['e_blocks_per_section'].apply(
        lambda x: sum([i for i in x if i != 0]) / len([i for i in x if i != 0]) if len(
            [i for i in x if i != 0]) > 0 else 0)

    df['std_e_blocks_per_section'] = df['e_blocks_per_section'].apply(calculate_std_e_blocks_per_section)

    df['exercise_density'] = df['exercise_duration'] / df['unit_duration']
    df['avg_e_per_unit'] = df['exercise_count'] / df['unit_count']

    non_exercise_time = (df['unit_duration'] - df['exercise_duration']) / 60
    gaps_count = df['e_block_count'] - 1
    df['avg_time_between_e_blocks'] = non_exercise_time.where(gaps_count > 0, 0) / gaps_count.where(gaps_count > 0,
                                                                                                       1)
    return df



def calculate_interaction_variables(df):
    df = df.copy()
    # replace d (discussion), e (exercise), and p (poll) with e
    # (should be i for interaction but the functions are implemented with e)
    df['course_structure'] = df['course_structure'].str.replace(r'[dep]', 'e', regex=True)

    # Apply each function to the 'course_structure' column
    df['i_blocks'] = df['course_structure'].apply(find_e_blocks)
    df['i_block_sizes'] = df['i_blocks'].apply(calculate_tuple_sizes)
    df['i_block_count'] = df['i_blocks'].apply(len)
    df['max_i_block_size'] = df['i_block_sizes'].apply(np.max)
    df['avg_i_block_size'] = df['i_block_sizes'].apply(np.mean)
    df['std_i_block_size'] = df['i_block_sizes'].apply(np.std)

    df['distances_between_i_blocks'] = df['i_blocks'].apply(calculate_distances_between_tuples)
    df['max_i_block_distance'] = df['distances_between_i_blocks'].apply(np.max)
    df['avg_i_block_distance'] = df['distances_between_i_blocks'].apply(np.mean)
    df['std_i_block_distance'] = df['distances_between_i_blocks'].apply(np.std)

    df['has_i'] = df['course_structure'].apply(analyze_sections)
    df['gaps_between_i_units'] = df['has_i'].apply(calculate_gaps_between_exercises)
    df['max_sections_without_i'] = df['gaps_between_i_units'].apply(np.max)
    df['avg_sections_without_i'] = df['gaps_between_i_units'].apply(np.mean)
    df['std_sections_without_i'] = df['gaps_between_i_units'].apply(np.std)

    df['i_blocks_per_section'] = df['course_structure'].apply(count_e_blocks_per_section)
    df['max_i_blocks_per_section'] = df['i_blocks_per_section'].apply(max)
    df['avg_i_blocks_per_section'] = df['i_blocks_per_section'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['std_i_blocks_per_section'] = df['i_blocks_per_section'].apply(calculate_std_e_blocks_per_section)

    df['interaction_density'] = df['interaction_duration'] / df['unit_duration']
    df['avg_i_per_unit'] = df['interaction_count'] / df['unit_count']

    non_interaction_time = (df['unit_duration'] - df['interaction_duration']) / 60
    gaps_count = df['i_block_count'] - 1

    df['avg_time_between_i_blocks'] = non_interaction_time.where(gaps_count > 0, 0) / gaps_count.where(gaps_count > 0, 1)

    df['avg_time_between_i_block_corrected'] = ((df['unit_duration'] - df['interaction_duration']) / 60) / df['gaps_between_i_units'].apply(len)

    # Replace e with i
    df['course_structure'] = df['course_structure'].str.replace('e', 'i')

    return df


def find_e_blocks(s):
    blocks = []
    start = -1
    position = -1 # actual position in the string ignoring |

    for char in s:
        position += 1
        if char == '|':
            if start != -1:
                blocks.append((start, position - 1))
                start = -1
            position -= 1  # Don't count '|' in position
        elif char == 'e':
            if start == -1: # Check if we found a new block
                start = position # Set the starting position of the block
        else:
            if start != -1: # We are currently in an 'e'-block
                blocks.append((start, position - 1)) # Add the blocks start and end position to the list
                start = -1 # Reset

    if start != -1:
        blocks.append((start, position))

    return blocks


def analyze_sections(s):
    sections = s.split('|')
    section_analysis = [('e' in section) for section in sections]
    return section_analysis


def calculate_gaps_between_exercises(boolean_list):
    gaps = []
    current_gap = 0

    for has_exercise in boolean_list:
        if has_exercise:
            gaps.append(current_gap)
            current_gap = 0
        else:
            current_gap += 1

    # If the list ends with False, we do not add the last gap
    return gaps


def count_e_blocks_per_section(s):
    sections = s.split('|')
    e_blocks_count = []

    for section in sections:
        count = 0
        in_e_block = False
        for char in section:
            if char == 'e':
                if not in_e_block:
                    count += 1
                    in_e_block = True
            else:
                in_e_block = False
        e_blocks_count.append(count)

    return e_blocks_count


def calculate_std_e_blocks_per_section(e_blocks_per_section):
    return np.std(e_blocks_per_section) if len(e_blocks_per_section) > 0 else 0


def calculate_e_block_distances(e_blocks):
    if len(e_blocks) < 2:
        return []
    return [e_blocks[i+1][0] - e_blocks[i][1] - 1 for i in range(len(e_blocks) - 1)]


def calculate_std_e_block_distance(e_blocks):
    distances = calculate_e_block_distances(e_blocks)
    return np.std(distances) if distances else 0


def calculate_distances_between_tuples(tuple_list):
    distances = []

    # Distance from the start (0,0) to the first tuple
    if tuple_list:
        distances.append(tuple_list[0][0])

    # Spacing between the tuples
    for i in range(1, len(tuple_list)):
        prev_end = tuple_list[i - 1][1]
        current_start = tuple_list[i][0]
        distance = (current_start - prev_end) - 1
        distances.append(distance)

    return distances


def calculate_tuple_sizes(tuple_list):
    sizes = []
    for start, end in tuple_list:
        size = end - start + 1
        sizes.append(size)
    return sizes


def aggregate_data(input_filepath, output_filepath):
    df = pd.read_csv(input_filepath)

    df['only_video'] = (df['video_duration'] == df['media_duration']) & (df['video_duration'] > 0)
    df['only_text'] = (df['text_duration'] == df['media_duration']) & (df['text_duration'] > 0)
    df['only_audio'] = (df['audio_duration'] == df['media_duration']) & (df['audio_duration'] > 0)
    # no other codal representations
    df['only_text_real'] = (df['only_text'] & df['multi_codal'])

    df['only_discussion'] = (df['building_block_unique'] == 'd')
    df['only_poll'] = (df['building_block_unique'] == 'p')

    df['video_text'] = df['building_block_unique'].str.contains(r'(?=.*v)(?=.*t)(?!.*a)')
    df['video_audio'] = df['building_block_unique'].str.contains(r'(?=.*v)(?=.*a)(?!.*t)')
    df['text_audio'] = df['building_block_unique'].str.contains(r'(?=.*t)(?=.*a)(?!.*v)')

    df['starts_with_video'] = (~df['only_video']) & (df['v_count'] > 0) & df['unit_structure'].str.startswith('v')
    df['starts_with_text'] = (~df['only_text']) & (df['t_count'] > 0) & df['unit_structure'].str.startswith('t')
    df['starts_with_audio'] = (~df['only_audio']) & (df['a_count'] > 0) & df['unit_structure'].str.startswith('a')

    # Group data by course
    df_agg = group_and_aggregate(df)

    # Calculate proportions
    df_agg = calculate_building_block_proportions(df_agg)

    # Calculate distance
    df_agg = calculate_exercise_variables(df_agg)

    # Save the grouped data
    df_agg.to_csv(output_filepath, index=False)

    # Create subset for media usage
    df_media_usage = df_agg[['provider_name', 'course_name', 'unit_count', 'chapter_count', 'video_count', 'text_count',
                             'graphics_count', 'code_rows_count', 'table_count',
                             'audio_count', 'video_duration', 'text_duration', 'audio_duration', 'media_duration',
                             'with_video', 'with_text', 'with_audio', 'with_media', 'only_video', 'only_text',
                             'only_audio', 'video_text', 'video_audio', 'text_audio', 'starts_with_video',
                             'starts_with_text', 'starts_with_audio', 'with_code', 'with_graphics', 'with_table',
                             'multi_codal']]

    # Save subset
    df_media_usage.to_csv('data/processed/media_usage_by_course.csv', index=False)

    # Create subset for interactive usage
    df_interactive_usage = df_agg[['provider_name', 'course_name', 'unit_count', 'chapter_count', 'exercise_count',
                                   'discussion_count', 'poll_count', 'exercise_duration', 'discussion_duration',
                                   'poll_duration', 'interaction_duration', 'with_exercise', 'with_discussion',
                                   'with_poll', 'only_exercise', 'only_discussion', 'only_poll', 'starts_with_exercise',
                                   'exercises_in_middle', 'ends_with_exercise', 'choice_count', 'coding_count',
                                   'mapping_count', 'essay_count', 'short_answer_count', 'with_interaction']]

    # Save subset
    df_interactive_usage.to_csv('data/processed/interactive_usage_by_course.csv', index=False)

    # create subset for exercise usage
    df_exercise_usage = df_agg[['provider_name', 'course_name', 'course_structure', 'unit_count', 'chapter_count',
                                'exercise_count', 'exercise_duration', 'unit_duration']]
    df_exercise_usage = calculate_exercise_variables(df_exercise_usage)
    df_exercise_usage.to_csv('data/processed/exercise_usage_by_course.csv', index=False)

    df_interaction_usage = df_agg[['provider_name', 'course_name', 'course_structure', 'unit_count', 'chapter_count',
                                   'interaction_count', 'interaction_duration', 'unit_duration']]
    df_interaction_usage = calculate_interaction_variables(df_interaction_usage)
    df_interaction_usage.to_csv('data/processed/interaction_usage_by_course.csv', index=False)


def aggregate_video_data(input_filepath):
    df = pd.read_csv(input_filepath)
    df = df[df['video_duration'] > 0]

    video_data = df.groupby(['provider_name', 'course_name']).agg(
        video_count=('v_count', 'sum'),
        video_content_min=('video_duration', 'min'),
        video_content_max=('video_duration', 'max'),
        video_content_mean=('video_duration', 'mean'),
        video_content_median=('video_duration', 'median'),
        video_content_std=('video_duration', 'std'),
        up_to_six=('video_duration', lambda x: (x <= 360).sum()),
        six_to_twelve=('video_duration', lambda x: ((x > 360) & (x <= 720)).sum()),
        more_than_twelve=('video_duration', lambda x: (x > 720).sum())
    ).reset_index()

    video_data.to_csv('data/processed/video_data_by_course.csv', index=False)


def aggregate_text_data(input_filepath):
    df = pd.read_csv(input_filepath)
    df = df[df['text_duration'] > 0]

    video_data = df.groupby(['provider_name', 'course_name']).agg(
        text_count=('t_count', 'sum'),
        text_content_min=('text_duration', 'min'),
        text_content_max=('text_duration', 'max'),
        text_content_mean=('text_duration', 'mean'),
        text_content_median=('text_duration', 'median'),
        text_content_std=('text_duration', 'std'),
        under_five_minutes=('text_duration', lambda x: (x < 300).sum()),
        above_five_under_ten_minutes=('text_duration', lambda x: ((x >= 300) & (x < 600)).sum()),
        above_ten_under_fifteen_minutes=('text_duration', lambda x: ((x >= 600) & (x < 900)).sum()),
        above_fifteen_minutes=('text_duration', lambda x: (x >= 900).sum())
    ).reset_index()

    video_data.to_csv('data/processed/text_data_by_course.csv', index=False)


def aggregate_unit_data(input_filepath):
    df = pd.read_csv(input_filepath)

    unit_data = df.groupby(['provider_name', 'course_name']).agg(
        unit_count=('unit', 'nunique'),
        media_duration_total=('media_duration', 'sum'),
        media_duration_min=('media_duration', 'min'),
        media_duration_max=('media_duration', 'max'),
        media_duration_mean=('media_duration', 'mean'),
        media_duration_median=('media_duration', 'median'),
        media_duration_std=('media_duration', 'std'),
        interaction_duration_total=('interaction_duration', 'sum'),
        interaction_duration_min=('interaction_duration', 'min'),
        interaction_duration_max=('interaction_duration', 'max'),
        interaction_duration_mean=('interaction_duration', 'mean'),
        interaction_duration_median=('interaction_duration', 'median'),
        interaction_duration_std=('interaction_duration', 'std'),
        unit_duration_total=('unit_duration', 'sum'),
        unit_duration_min=('unit_duration', 'min'),
        unit_duration_max=('unit_duration', 'max'),
        unit_duration_mean=('unit_duration', 'mean'),
        unit_duration_median=('unit_duration', 'median'),
        unit_duration_std=('unit_duration', 'std'),
        under_five_minutes=('unit_duration', lambda x: (x < 300).sum()),
        above_five_under_ten_minutes=('unit_duration', lambda x: ((x > 300) & (x < 600)).sum()),
        above_ten_under_fifteen_minutes=('unit_duration', lambda x: ((x > 600) & (x < 900)).sum()),
        above_fifteen_minutes=('unit_duration', lambda x: (x > 900).sum()),
        zero_media_one_interaction=('0_media_1_interaction_count', 'sum'),
        zero_media_two_interaction=('0_media_2_interaction_count', 'sum'),
        one_media_zero_interaction=('1_media_0_interaction_count', 'sum'),
        one_media_one_interaction=('1_media_1_interaction_count', 'sum'),
        one_media_two_interaction=('1_media_2_interaction_count', 'sum'),
        one_media_three_interaction=('1_media_3_interaction_count', 'sum'),
        two_media_zero_interaction=('2_media_0_interaction_count', 'sum'),
        two_media_one_interaction=('2_media_1_interaction_count', 'sum'),
        two_media_two_interaction=('2_media_2_interaction_count', 'sum'),
        two_media_three_interaction=('2_media_3_interaction_count', 'sum')
    ).reset_index()

    unit_data.to_csv('data/processed/unit_data_by_course.csv', index=False)


if __name__ == '__main__':
    aggregate_data('data/processed/aggregated_by_unit_data.csv', 'data/processed/aggregated_by_course_data.csv')
    aggregate_text_data('data/processed/aggregated_by_unit_data.csv')
    aggregate_video_data('data/processed/aggregated_by_unit_data.csv')
    aggregate_unit_data('data/processed/aggregated_by_unit_data.csv')
