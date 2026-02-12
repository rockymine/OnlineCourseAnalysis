# run with: python -m src.visualization.visualize_by_unit in the terminal

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.util.util import *


def create_boxplots(df, column, save_path=None, is_duration=True):
    """
    Create boxplots for the given column in the DataFrame, grouped by course.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column (str): The column for which to create boxplots.
    save_path (str, optional): If provided, the plot is saved to this file path.

    Returns:
    matplotlib.Figure: The created Figure object.
    """

    # Exclude 0 values and convert to minutes
    df = df[df[column] != 0].copy()

    if is_duration:
        df[column] = df[column] / 60

    # Create a Figure and Axes object
    fig, ax = plt.subplots(figsize=(10, 7))

    # Create a boxplot for the given column, grouped by course
    sns.boxplot(data=df, x='course_name', y=column,
                flierprops={"marker": "o"},
                boxprops={"facecolor": (.4, .6, .8, .5)},
                medianprops={"color": "coral"})

    # Rotate the x-axis labels for readability
    ax.tick_params(axis='x', rotation=45)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment('right')

    ax.set_xlabel('Course', fontsize=20)
    ax.set_ylabel(format_string(column), fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    ax.yaxis.grid(True)

    # Adjust layout
    plt.tight_layout()

    # If a save path is provided, save the figure to this path
    if save_path is not None:
        fig.savefig(save_path, bbox_inches='tight')

    plt.close(fig)
    return fig


def create_video_proportion_barchart(df, course, save_path=None):
    df = df[df['course_name'] == course].copy()
    df['chapter'] = df['chapter'].astype(int)

    # Group course data by unit and chapter and sum the media duration
    grouped = df.groupby(['chapter', 'unit'])['media_duration'].sum().unstack()
    grouped = grouped.sort_index()
    normalized = grouped.div(grouped.sum(axis=1), axis=0)
    cmap = truncate_colormap(plt.get_cmap('coolwarm'), 0.2, 0.8)

    # Create a Figure and Axes object
    fig, ax = plt.subplots()

    for i, col in enumerate(grouped.columns):
        # Define color for plotting based on 'video_proportion' column
        color = cmap(df.loc[df['unit'] == col, 'video_proportion'].iloc[0])

        # Plot bars for each chapter
        ax.barh(normalized.index,
                normalized[col],
                left=normalized.iloc[:, :i].sum(axis=1),
                color=color,
                label=col,
                edgecolor='black')

    ax.set_xlabel('Normalized Duration', fontsize=20)
    ax.set_ylabel('Chapter', fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    ax.set_xlim([0, 1])

    # Add legend
    sm = plt.cm.ScalarMappable(cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Video Proportion', fontsize=20)
    cbar.ax.tick_params(labelsize=20)  # Set colorbar tick font size

    # Adjust layout
    plt.tight_layout()

    # If a save path is provided, save the figure to this path
    if save_path is not None:
        fig.savefig(save_path)

    plt.close(fig)
    return fig


def create_media_proportion_barchart(df, course, save_path=None):
    df = df[df['course_name'] == course].copy()
    df['chapter'] = df['chapter'].astype(int)

    # Group course data by unit and chapter and sum the media duration
    grouped = df.groupby(['chapter', 'unit'])['completion_time'].sum().unstack()
    grouped = grouped.sort_index()
    normalized = grouped.div(grouped.sum(axis=1), axis=0)
    cmap = truncate_colormap(plt.get_cmap('PiYG'), 0.2, 0.8)

    # Create a Figure and Axes object
    fig, ax = plt.subplots()

    for i, col in enumerate(grouped.columns):
        # Define color for plotting based on 'video_proportion' column
        color = cmap(df.loc[df['unit'] == col, 'media_proportion'].iloc[0])

        # Plot bars for each chapter
        ax.barh(normalized.index,
                normalized[col],
                left=normalized.iloc[:, :i].sum(axis=1),
                color=color,
                label=col,
                edgecolor='black')

    ax.set_xlabel('Normalized Duration', fontsize=20)
    ax.set_ylabel('Chapter', fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    ax.set_xlim([0, 1])

    # Add legend
    sm = plt.cm.ScalarMappable(cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Media Proportion', fontsize=20)  # Set colorbar label font size
    cbar.ax.tick_params(labelsize=20)  # Set colorbar tick font size

    # Adjust layout
    plt.tight_layout()

    # If a save path is provided, save the figure to this path
    if save_path is not None:
        fig.savefig(save_path)

    plt.close(fig)
    return fig


def create_duration_boxplots(df):
    # Create boxplots for duration columns
    create_boxplots(df, column='video_duration', save_path='figures/boxplots/video_duration_boxplot.pdf')
    create_boxplots(df, column='audio_duration', save_path='figures/boxplots/audio_duration_boxplot.pdf')
    create_boxplots(df, column='text_duration', save_path='figures/boxplots/text_duration_boxplot.pdf')
    create_boxplots(df, column='exercise_duration', save_path='figures/boxplots/exercise_duration_boxplot.pdf')
    create_boxplots(df, column='poll_duration', save_path='figures/boxplots/poll_duration_boxplot.pdf')
    create_boxplots(df, column='discussion_duration', save_path='figures/boxplots/discussion_duration_boxplot.pdf')
    create_boxplots(df, column='media_duration', save_path='figures/boxplots/media_duration_boxplot.pdf')
    create_boxplots(df, column='interaction_duration', save_path='figures/boxplots/interaction_duration_boxplot.pdf')
    create_boxplots(df, column='unit_duration', save_path='figures/boxplots/unit_duration_boxplot.pdf')
    create_boxplots(df, column='completion_time', save_path='figures/boxplots/completion_time_boxplot.pdf')


def create_individual_media_and_video_barcharts(df):
    # Create figures for video and media proportions
    for course in df['course_name'].unique():
        # Replace '-' with '_' in course name for the filename
        filename = course.replace('-', '_')

        # Create the save path
        save_path_video = f'figures/proportions/video/{filename}_video_proportion.pdf'
        save_path_media = f'figures/proportions/media/{filename}_media_proportion.pdf'

        # Call the functions
        create_video_proportion_barchart(df, course=course, save_path=save_path_video)
        create_media_proportion_barchart(df, course=course, save_path=save_path_media)


def visualize_data(input_filepath):
    """
    Create visualizations for the data in the DataFrame located at input_filepath.

    Parameters:
    input_filepath (str): The file path to the DataFrame.
    """

    df = pd.read_csv(input_filepath)

    # Create boxplots
    create_duration_boxplots(df)

    # Create barcharts for video and media proportions
    create_individual_media_and_video_barcharts(df)


if __name__ == '__main__':
    visualize_data('data/processed/aggregated_by_unit_data.csv')
