# run with: python -m src.visualization.visualize_by_course in the terminal

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from ..constants import BUILDING_BLOCK_COLORS


def create_building_block_proportions_barplot(df, save_path=None):
    """
    Creates a horizontal stacked bar plot of building block proportions for each course.
    The proportions of video, text, audio, exercise, discussion, and poll durations
    in relation to the unit duration are plotted for each course.
    The stacked bar chart provides an overview of the composition of each course
    in terms of the different types of building blocks.

    Parameters:
    df (pandas.DataFrame): DataFrame containing the course data.
                           It should have columns for the course names and
                           the proportions of the different building block types.
    save_path (str, optional): If provided, the plot will be saved to this file path.
                               Default is None.

    Returns:
    fig (matplotlib.figure.Figure): Figure object with the created plot.
    """
    building_block_proportions = df[
        ['video_proportion', 'text_proportion', 'audio_proportion', 'exercise_proportion', 'discussion_proportion',
         'poll_proportion']]

    # Create a Figure and Axes object with adjusted dimensions
    fig, ax = plt.subplots(figsize=(12, 8))

    # Initialize the starting position for each bar segment
    bar_start = np.zeros(len(df))

    # Iterate over the columns to plot
    for i, col in enumerate(building_block_proportions):
        values = df[col].values
        ax.barh(df['course_name'], values, left=bar_start, height=0.8, color=BUILDING_BLOCK_COLORS[col])
        bar_start += values

    # Set the labels and title
    ax.set_xlabel('Media Proportion on Unit Duration', fontsize=20)
    ax.set_ylabel('Course', fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    # Set the legend
    legend_labels = ['v', 't', 'a', 'e', 'd', 'p']
    ax.legend(legend_labels,
              bbox_to_anchor=(0.5, -0.2),
              loc='center',
              ncol=6,
              edgecolor='black',
              fancybox=False,
              prop={'size': 20})

    # Adjust the layout to stretch the plot
    plt.subplots_adjust(bottom=0.2)

    # If a save path is provided, save the figure to this path
    if save_path is not None:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.close(fig)
    return fig


def course_composition_diagram(sequence_str, highlight=True, exercise_distance=True, save_path=None):
    """
    Creates a pearl necklace visualization for a sequence of course elements.

    The function generates a horizontal diagram that visually represents a sequence of course content elements such as
    video, text, discussion, and exercises. Different symbols and colors are used to represent each type of element,
    and optional highlights can be added to indicate specific patterns within the sequence. The visualization also
    includes the ability to draw brackets between exercise blocks to show the gaps between them.

    Parameters:
    sequence_str (str): A string representing the sequence of course elements. Each character corresponds to a
    different type of element.
                        - 'v': Video
                        - 't': Text
                        - 'd': Discussion
                        - 'e': Exercise
                        - '|': Section End
    highlight (bool, optional): If True, highlights specific patterns ('td' and 'ee') in the sequence.
                                'td' highlights the transition from text to discussion, and 'ee' highlights
                                consecutive exercises. Default is True.
    exercise_distance (bool, optional): If True, visualizes the distance between exercise blocks with brackets
                                        beneath the diagram. Default is True.
    save_path (str, optional): If provided, the visualization will be saved to the specified file path. Default is None.

    Returns:
    plt (matplotlib.pyplot): The plot object containing the pearl necklace visualization.
    """

    # Define symbol mapping (shapes and colors)
    symbol_map_updated = {
        'v': ('>', 'red'),  # Video
        't': ('s', 'green'),  # Text
        'd': ('o', 'purple'),  # Discussion
        '|': ('|', 'black'),  # Section End
        'e': ('h', 'blue'),  # Exercise
        'p': ('^', 'gold'),  # Poll
        'a': ('d', 'orange')  # Audio (thin diamond)
    }

    # Convert the string into a list of characters
    custom_sequence_list = list(sequence_str)

    # Identify 'vt' and 'ee' patterns
    pattern_indices_fixed = [i for i in range(len(custom_sequence_list) - 1) if
                             custom_sequence_list[i] == 't' and custom_sequence_list[i + 1] == 'd']
    pattern_ee_indices = [i for i in range(len(custom_sequence_list) - 1) if
                          custom_sequence_list[i] == 'e' and custom_sequence_list[i + 1] == 'e']

    # Identify 'e' blocks (start, end) pairs
    e_blocks = []
    start = None
    for i, symbol in enumerate(custom_sequence_list):
        if symbol == 'e':
            if start is None:
                start = i  # Start of a new 'e' block
        else:
            if start is not None:
                e_blocks.append((start, i - 1))  # End of the 'e' block
                start = None
    if start is not None:
        e_blocks.append((start, len(custom_sequence_list) - 1))

    # Visualization setup
    fig, ax = plt.subplots(figsize=(len(custom_sequence_list) * 0.5, 2.5))
    ax.set_xlim(-0.5, len(custom_sequence_list) -0.5)
    ax.set_ylim(0, 1)
    ax.axis('off')  # Hide axes

    # Add highlights for "vt" and "ee" patterns
    if highlight:
        for idx in pattern_indices_fixed:
            ax.add_patch(plt.Rectangle((idx - 0.5, 0.25), 2, 0.5, color='yellow', alpha=0.3))  # Highlight for "vt"
        for idx in pattern_ee_indices:
            ax.add_patch(plt.Rectangle((idx - 0.5, 0.25), 2, 0.5, color='lightblue', alpha=0.3))  # Highlight for "ee"

    # Draw lines between 'e' blocks and vertical lines for measurement clarity
    if exercise_distance:
        for i in range(len(e_blocks) - 1):
            end_of_first_block = e_blocks[i][1] + 0.5  # Right edge of the first block
            start_of_next_block = e_blocks[i + 1][0] - 0.5  # Left edge of the next block
            ax.plot([end_of_first_block, start_of_next_block], [0.25, 0.25], color='black', lw=2)  # Horizontal line
            ax.plot([end_of_first_block, end_of_first_block], [0.25, 0.35], color='black',
                    lw=2)  # Vertical line at the start
            ax.plot([start_of_next_block, start_of_next_block], [0.25, 0.35], color='black',
                    lw=2)  # Vertical line at the end

    # Plot the symbols in the sequence
    for i, symbol in enumerate(custom_sequence_list):
        if symbol in symbol_map_updated:
            shape, color = symbol_map_updated[symbol]
            ax.scatter(i, 0.5, marker=shape, color=color, s=500)

    # Legend setup
    legend_elements = [
        Line2D([0], [0], marker='|', color='black', label='Unit Start/End', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='>', color='red', label='Video', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='s', color='green', label='Text', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='o', color='purple', label='Discussion', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='h', color='blue', label='Exercise', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='^', color='gold', label='Poll', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='D', color='orange', label='Audio', markersize=15, linestyle='None')
    ]

    ax.legend(
        handles=legend_elements,
        loc='center',
        bbox_to_anchor=(0.5, -0.5),
        ncol=7,
        frameon=True,
        framealpha=0.7,
        facecolor='lightgray',
        edgecolor='none',
        markerscale=1.5,
        borderpad=0.6,
        fontsize=20
    )

    # Adjust layout
    plt.tight_layout(pad=0, w_pad=0, h_pad=0)

    # Save the final visualization
    if save_path is not None:
        plt.savefig(save_path)

    plt.close(fig)
    return plt


SYMBOL_MAP = {
    'v': ('>', 'red'),       # Video
    't': ('s', 'green'),     # Text
    'd': ('o', 'purple'),    # Discussion
    '|': ('|', 'black'),     # Unit separator
    'e': ('h', 'blue'),      # Exercise
    'p': ('^', 'gold'),      # Poll
    'a': ('d', 'orange')     # Audio (thin diamond)
}

LEGEND_ELEMENTS = [
    Line2D([0], [0], marker='|', color='black', label='Unit Start/End', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='>', color='red', label='Video', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='s', color='green', label='Text', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='o', color='purple', label='Discussion', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='h', color='blue', label='Exercise', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='^', color='gold', label='Poll', markersize=15, linestyle='None'),
    Line2D([0], [0], marker='d', color='orange', label='Audio', markersize=15, linestyle='None')
]


def create_full_course_composition_diagram(unit_df, course, max_elements_per_row=30, save_path=None):
    """
    Creates a full course composition diagram with chapters stacked vertically.
    Long chapters are wrapped at unit boundaries when exceeding max_elements_per_row.
    """
    cdf = unit_df[unit_df['course_name'] == course].copy()
    cdf['chapter'] = cdf['chapter'].astype(int)
    cdf['section'] = cdf['section'].astype(int)
    cdf = cdf.sort_values(['chapter', 'section'])

    # Build rows: list of (chapter, label, sequence_string) tuples
    rows = []
    for chapter in sorted(cdf['chapter'].unique()):
        units = cdf[cdf['chapter'] == chapter].sort_values('section')
        unit_structures = units['unit_structure'].tolist()

        current_parts = []
        current_len = 0
        row_index = 0

        for j, structure in enumerate(unit_structures):
            # +1 for the separator '|' if not the first unit in the row
            added_len = len(structure) + (1 if current_parts else 0)

            if current_parts and current_len + added_len > max_elements_per_row:
                # Flush current row
                seq = '|'.join(current_parts)
                label = f"Ch. {chapter}" if row_index == 0 else ""
                rows.append((chapter, label, seq))
                row_index += 1
                current_parts = [structure]
                current_len = len(structure)
            else:
                current_parts.append(structure)
                current_len += added_len

        # Flush remaining
        if current_parts:
            seq = '|'.join(current_parts)
            label = f"Ch. {chapter}" if row_index == 0 else ""
            rows.append((chapter, label, seq))

    # Find the max row width for consistent figure sizing
    max_width = max(len(seq) for _, _, seq in rows)

    # Figure dimensions
    row_height = 0.6
    fig_width = max(max_width * 0.35, 8)
    fig_height = len(rows) * row_height + 1.5

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(-1.5, max_width + 0.5)
    ax.set_ylim(-0.5, len(rows))
    ax.axis('off')

    # Draw each row (bottom-to-top so chapter 1 is at the top)
    for row_idx, (chapter, label, seq) in enumerate(rows):
        y = len(rows) - 1 - row_idx  # flip so ch1 is top

        # Alternating background: light gray for even-numbered chapters
        if chapter % 2 == 0:
            ax.add_patch(plt.Rectangle(
                (-1.5, y - 0.4), max_width + 2, 0.8,
                color='lightgray', alpha=0.3, zorder=0))

        # Chapter label
        if label:
            ax.text(-1.5, y, label, fontsize=12, va='center', ha='left', fontweight='bold')

        # Plot symbols
        symbols = list(seq)
        for x, symbol in enumerate(symbols):
            if symbol in SYMBOL_MAP:
                shape, color = SYMBOL_MAP[symbol]
                ax.scatter(x, y, marker=shape, color=color, s=200, zorder=3)

    # Legend at the bottom
    ax.legend(
        handles=LEGEND_ELEMENTS,
        loc='center',
        bbox_to_anchor=(0.5, -0.02),
        ncol=7,
        frameon=True,
        framealpha=0.7,
        facecolor='lightgray',
        edgecolor='none',
        markerscale=1.2,
        borderpad=0.6,
        fontsize=10
    )

    plt.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.close(fig)
    return fig


def create_all_course_composition_diagrams(unit_df):
    for course in unit_df['course_name'].unique():
        filename = course.replace('-', '_')
        save_path = f'figures/composition/{filename}_course_composition.pdf'
        create_full_course_composition_diagram(unit_df, course, save_path=save_path)


def visualize_data(course_filepath, unit_filepath):
    """
    Create visualizations for the data in the DataFrame located at input_filepath.

    Parameters:
    course_filepath (str): The file path to the course-level aggregated DataFrame.
    unit_filepath (str): The file path to the unit-level aggregated DataFrame.
    """

    # Load the data
    df = pd.read_csv(course_filepath)
    unit_df = pd.read_csv(unit_filepath)

    # Create a stacked bar plot to visualize the distribution of building blocks on the course duration
    create_building_block_proportions_barplot(df, 'figures/composition/building_block_proportions_barplot.pdf')

    # Create a Course Composition Diagram for the given sequence (example section)
    course_composition_diagram("tvte|tvte|tvte|tve|tvee|td|t", False, True, 'figures/composition/idf-hci_course_composition_diagram.pdf')

    # Create full course composition diagrams for all courses
    create_all_course_composition_diagrams(unit_df)


if __name__ == '__main__':
    visualize_data('data/processed/aggregated_by_course_data.csv', 'data/processed/aggregated_by_unit_data.csv')
