# Online Course Analysis: Python Script Documentation

**Author:** Michael Ganske
**Date:** February 2024

## Project Overview

The **OnlineCourseAnalysis** project is a Python-based initiative focused on the analysis of online course structures and content. This documentation provides a detailed overview of the project's organization, crucial for efficient navigation and understanding.

```
OnlineCourseAnalysis/
├── data/
│   ├── processed/
│   └── raw/
│       └── coursedata.xlsx
├── docs/
├── figures/
├── notebooks/
├── src/
│   ├── data/
│   │   ├── aggregate_by_course.py
│   │   ├── aggregate_by_unit.py
│   │   ├── convert_to_excel.py
│   │   └── preprocess.py
│   ├── util/
│   │   └── util.py
│   └── visualization/
│       ├── visualize_by_course.py
│       └── visualize_by_unit.py
```

### Data Directory

The project's `data` directory is divided into two main subdirectories: `raw` and `processed`, each serving a distinct phase in data handling.

#### Raw Data

The `raw` data, sourced from the initial coding phase, is stored in the `coursedata.xlsx` file. This file contains detailed records of presentations and interactive elements within online courses, with rows dedicated to the provider, course, and unit information. This structure facilitates a granular analysis of each learning unit.

#### Processed Data

The `processed` subdirectory houses data in `.csv` and `.xlsx` formats, representing the state after undergoing various processing scripts. These files are prepared for further analysis tasks.

### Source Code

The `src` directory contains Python scripts categorized by their purpose: data manipulation, visualization, and utilities.

#### Data Scripts

Within the `data` folder, scripts focus on preprocessing raw data, aggregating information by learning units and courses, and data format conversion (e.g., from `.csv` to `.xlsx`).

**preprocess.py**

- `convert_to_seconds(time_str)`: time in HMS format is converted to seconds
- `drop_columns(df)`: unnecessary columns are removed from the dataframe
- `rename_columns(df)`: some columns are renamed for easier handling
- `create_building_block_short_column(df)`: a new column is created for easier handling of media elements, e.g. video is renamed to v (allows for later concatenation and analysis of unit structure)
- `process_durations(df)`: application of the `convert_to_seconds(time_str)` function to video duration and estimated completion time
- `split_audio_video_duration(df)`: in the original dataset the duration of videos and audios was stored in the same column. This function creates a new column for audio duration and correctly assigns durations based on media element type
- `create_unit_parts_columns(df)`: the learning unit id was coded as a string (e.g. 2.1) that reflects the position of the learning unit in the course. This function splits this string into the chapter and section and stores the values as integers. This step was necessary as the string based notation did not reflect the true layout of the course when sorting it at later stages.
- `map_building_block(df)`: during the coding phase different names were used for the same element. This function unifies the naming.
- `map_task_type(df)`: during the coding phase different names were used for the same exercise type. This function unifies the naming.
- `map_course_names(df)`: the full names of the courses are abbreviated.
- `add_leading_zero(unit)`: a leading zero is added to the second part of the unit. This makes sure the overall course structure is kept when sorting the units. A unit with the id of 2.1 will now be referenced as 2.01 (2.10 stays 2.10)
- `fill_missing_values(df)`: during the coding phase 0 or null values were not entered to speed up the process. This function fills those missing values
- `preprocess_data(raw_data_filepath, preprocessed_data_filepath)`: the raw course data is loaded and modified using the above functions. The function stores a cleaned version of the data ready for the next analysis steps.
  - some faulty entries are modified and removed here too
  - a new column is added to sum the graphics count

**aggregate_by_unit.py**

- `create_text_duration_column(df)`: a new column is created to store the duration of a text. The `calculate_text_duration(word_count)` function is applied.
- `calculate_text_duration(word_count)`: based on reading speed and word count the text duration is calculated
- `create_media_duration_column(df)`: a new column is created to store the duration of all presentation elements in the learning unit. The duration of video, text, and audio is added up.
- `filter_building_blocks(string)`: a new column is created to store the filtered unit structure. Consecutive media elements of the same type are removed in the string representation. A unit structure of vteeet becomes vtet.
- `filter_unique_building_blocks(string)`: a new column is created to store the unique media elements used in the learning unit. A filtered unit structure of vtet becomes etv. The string output is alphabetically sorted.
- `classify_combinations(s)`: a new column is created to store the ratio of presentation and interactive elements. If a learning unit contains 2 presentation types and 1 interactive element it is stored as 2-presentation-1-interactive.
- `create_building_block_columns(df)`: several new columns are created to analyze the structure of a learning unit in terms of the usage of presentation and interactive elements
  - `{media_element}_count`: a new column is created for each media element that stores how many times it was used in each learning unit
  - `media_element_count`: stores how many media elements were used by the learning unit in total
  - `unit_structure_filtered`: application of the `filter_building_blocks(string)` function
  - `building_block_changes_count`: the length of the filtered structure of the learning unit is used to determine how often media elements change within a learning unit
  - `building_block_unique`: application of the `filter_unique_building_blocks(string)` function
  - `media_interaction_combination`: application of the `classify_combinations(s)` function
  - `{media_interaction_combination}_count`: a new column is created for all possible combinations of presentation and interaction elements. These columns allow for later analysis of the course structure.
  - `building_block_unique_count`: stores how many unique media elements were used by the learning unit
- `calculate_exercise_duration(df)`: the time factors for each exercise type used in the learning unit are applied to calculate the total exercise duration of a learning unit
- `create_exercise_position_columns(df)`: based on the filtered learning unit representation several columns are created to capture the position of exercises within the learning unit.
  - `has_exercises`: true, if the learning unit contains exercises
  - `only_exercises`: true, if the learning unit only contains exercises
  - `multiple_exercise_blocks`: true, if exercises in the learning unit are separated by other media elements
  - `starts_with_exercise`: true, if the first element of a learning unit is an exercise
  - `exercises_in_middle`: true, if there are exercises not at the start or end of a learning unit
  - `ends_with_exercise`: true, if the last element of a learning unit is an exercise
- `calculate_interaction_duration(df)`: a new column is created, to sum up the duration of interactive elements. The duration of polls and discussions is approximated with a time factor and added to the exercise duration.
- `calculate_unit_duration(df)`: the duration of presentation and interaction elements are combined.
- `calculate_estimated_completion_time(df)`: video and audio duration are multiplied with a factor of two. Duration of text and interactive elements are added.
- `group_and_aggregate(df)`: the data is grouped by provider name, course name, and unit. This step ensures that all rows related to the same learning unit in the raw data set are combined in a single row per learning unit. Within this step, the unit structure is determined by joining the media elements' abbreviations.
- `calculate_video_proportion(df)`: calculate the proportion of video within the duration of presentation elements of a unit.
- `calculate_media_proportion(df)`: calculate the proportion of presentation duration of the completion time of a unit.
- `reorder_columns(df)`: columns are ordered by identifiers, unit structure, building block counts, durations, and proportions.
- `create_unit_parts_columns(df)`: the unit column is split into columns for chapter and section.
- `create_interaction_columns(df)`: creates columns for the count of interactions used in the learning unit and their density. The density is the interaction duration divided by the unit duration.
- `aggregate_data(df)`: creates a new file that contains the data aggregated by the learning unit. The above functions are applied to the cleaned data. Additionally, a new column is created to evaluate whether a unit is multi-codal or not.
- `create_type_transition_summary(df)`: creates a new file that captures how often transitions from one to another media element occur in a learning unit.

#### Utility Scripts

The `util` directory's `util.py` script handles general data conversion functions, distinct from direct course content analysis.

#### Visualization Scripts

The `visualization` folder includes scripts for creating plots and visual aids, like `visualize_by_course.py` and `visualize_by_unit.py`, to visually represent analysis findings.

### Constants

A `constants.py` file is included for storing dictionaries crucial for the creation of visualizations. This centralizes the management of constants used across different scripts, ensuring consistency in visual outputs.

## How to Use

1. Put raw data as `.xlsx` file into the `data/raw/` folder (if necessary, change file name in the script)
2. Run the entire pipeline: `python run_all.py`

Or run individual steps:

1. `python src/data/preprocess.py`
2. `python src/data/aggregate_by_unit.py`
3. `python src/data/aggregate_by_course.py`
4. `python src/data/convert_csv_to_excel.py`
5. `python -m src.visualization.visualize_by_unit`
6. `python -m src.visualization.visualize_by_course`
