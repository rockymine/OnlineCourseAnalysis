\documentclass{article}
\usepackage{graphicx} % Required for inserting images
\usepackage{dirtree}

\title{Online Course Analysis: Python Script Documentation}
\author{Michael Ganske}
\date{February 2024}

\begin{document}

\maketitle

\section{Project Overview}
The \textbf{OnlineCourseAnalysis} project is a Python-based initiative focused on the analysis of online course structures and content. This documentation provides a detailed overview of the project's organization, crucial for efficient navigation and understanding.\\

\dirtree{%
.1 OnlineCourseAnalysis/.
.2 data.
.3 processed.
.3 raw/.
.4 \texttt{coursedata.xlsx}.
.2 docs/.
.2 figures/.
.2 notebooks/.
.2 src/.
.3 data/.
.4 \texttt{aggregate\_by\_course.py}.
.4 \texttt{aggregate\_by\_unit.py}.
.4 \texttt{convert\_to\_excel.py}.
.4 \texttt{preprocess.py}.
.3 util/.
.4 \texttt{util.py}.
.3 visualization/.
.4 \texttt{visualize\_by\_course.py}.
.4 \texttt{visualize\_by\_unit.py}.
}

\subsection{Data Directory}
The project's \texttt{data} directory is divided into two main subdirectories: \texttt{raw} and \texttt{processed}, each serving a distinct phase in data handling.

\subsubsection*{Raw Data}
The \texttt{raw} data, sourced from the initial coding phase, is stored in the \texttt{coursedata.xlsx} file. This file contains detailed records of presentations and interactive elements within online courses, with rows dedicated to the provider, course, and unit information. This structure facilitates a granular analysis of each learning unit.

\subsubsection*{Processed Data}
The \texttt{processed} subdirectory houses data in \texttt{.csv} and \texttt{.xlsx} formats, representing the state after undergoing various processing scripts. These files are prepared for further analysis tasks.

\subsection{Source Code}
The \texttt{src} directory contains Python scripts categorized by their purpose: data manipulation, visualization, and utilities.

\subsubsection*{Data Scripts}
Within the \texttt{data} folder, scripts focus on preprocessing raw data, aggregating information by learning units and courses, and data format conversion (e.g., from \texttt{.csv} to \texttt{.xlsx}).

\textbf{preprocess.py}

\begin{itemize}
    \item convert\_to\_seconds(time\_str): time in HMS format is converted to seconds
    \item drop\_columns(df): unnecessary columns are removed from the dataframe
    \item rename\_columns(df): some columns are renamed for easier handling
    \item create\_building\_block\_short\_column(df): a new column is created for easier handling of media elements, e.g. video is renamed to v (allows for later concatenation and analysis of unit structure)
    \item process\_durations(df): application of the convert\_to\_seconds(time\_str) function to video duration and estimated completion time
    \item split\_audio\_video\_duration(df): in the original dataset the duration of videos and audios was stored in the same column. This function creates a new column for audio duration and correctly assigns durations based on media element type
    \item create\_unit\_parts\_columns(df): the learning unit id was coded as a string (e.g. 2.1) that reflects the position of the learning unit in the course. This function splits this string into the chapter and section and stores the values as integers. This step was necessary as the string based notation did not reflect the true layout of the course when sorting it at later stages.
    \item map\_building\_block(df): during the coding phase different names were used for the same element. This function unifies the naming.
    \item map\_task\_type(df): during the coding phase different names were used for the same exercise type. This function unifies the naming.
    \item map\_course\_names(df): the full names of the courses are abbreviated.
    \item add\_leading\_zero(unit): a leading zero is added to the second part of the unit. This makes sure the overall course structure is kept when sorting the units. A unit with the id of 2.1 will now be referenced as 2.01 (2.10 stays 2.10)
    \item fill\_missing\_values(df): during the coding phase 0 or null values were not entered to speed up the process. This function wills those missing values
    \item preprocess\_data(raw\_data\_filepath, preprocessed\_data\_filepath): the raw course data is loaded and modified using the above functions. The function stores a cleaned version of the data ready for the next analysis steps.
    \begin{itemize}
        \item some faulty entries are modified and removed here too
        \item a new column is added to sum the graphics count (
    \end{itemize}
\end{itemize}

\textbf{aggregate\_by\_unit.py}

\begin{itemize}
    \item create\_text\_duration\_column(df): a new column is created to store the duration of a text. The calculate\_text\_duration(word\_count) function is applied.
    \item calculate\_text\_duration(word\_count): based on reading speed and word count the text duration is calculated
    \item create\_media\_duration\_column(df): a new column is created to store the duration of all presentation elements in the learning unit. The duration of video, text, and audio is added up.
    \item filter\_building\_blocks(string): a new column is created to store the filtered unit structure. Consecutive media elements of the same type are removed in the string representation. A unit struture of vteeet becomes vtet.
    \item filter\_unique\_building\_blocks(string): a new column is created to store the unique media elements used in the learning unit. A filtered unit structure of vtet becomes etv. The string output is alphabetically sorted.
    \item classify\_combinations(s): a new column is created to store the ratio of presentation and interactive elements. If a learning unit contains 2 presentation types and 1 interactive element it is stored as 2-presentation-1-interactive.
    \item create\_building\_block\_columns(df): several new columns are created to analyze the structure of a learning unit in terms of the usage of presentation and interactive elements
    \begin{itemize}
        \item \{media\_element\}\_count: a new column is created for each media element that stores how many times it was used in each learning unit
        \item media\_element\_count: stores how many media elements were used by the learning unit in total
        \item unit\_structure\_filtered: application of the filter\_building\_blocks(string) function
        \item building\_block\_changes\_count: the length of the filtered structure of the learning unit is used to determine how often media elements change within a learning unit
        \item building\_block\_unique: application of the filter\_unique\_building\_blocks(string) function
        \item media\_interaction\_combination: application of the classify\_combinations(s) function
        \item \{media\_interaction\_combination\}\_count: a new column is created for all possible combinations of presentation and interaction elements. These columns allow for later analysis of the course structure.
        \item building\_block\_unique\_count: stores how many unique media elements were used by the learning unit
    \end{itemize}
    \item calculate\_exercise\_duration(df): the time factors for each exercise type used in the learning unit are applied to calculate the total exercise duration of a learning unit
    \item create\_exercise\_position\_columns(df): based on the filtered learning unit representation several columns are created to capture the position of exercises within the learning unit.
    \begin{itemize}
        \item has\_exercises: true, if the learning unit contains exercises
        \item only\_exercises: true, if the learning unit only contains exercises
        \item multiple\_exercise\_blocks: true, if exercises in the learning unit are separated by other media elements
        \item starts\_with\_exercise: true, if the first element of a learning unit is an exercise
        \item exercises\_in\_middle: true, if there are exercises not at the start of end of a learning unit
        \item ends\_with\_exercise: true, if the last element of a learning unit is an exercise
    \end{itemize}
    \item calculate\_interaction\_duration(df): a new column is created, to sum up the duration of interactive elements. The duration of polls and discussions is approximated with a time factor and added to the exercise duration.
    \item calculate\_unit\_duration(df): the duration of presentation and interaction elements are combined.
    \item calculate\_estimated\_completion\_time(df): video and audio duration are multiplied with a factor of two. Duration of text and interactive elements are added.
    \item group\_and\_aggregate(df): the data is grouped by provider name, course name, and unit. This step ensures that all rows related to the same learning unit in the raw data set are combined in a single row per learning unit. Within this step, the unit structure is determined by joining the media elements' abbreviations.
    \item calculate\_video\_proportion(df): calculate the proportion of video within the duration of presentation elements of a unit.
    \item calculate\_media\_proportion(df): calculate the proportion of presentation duration of the completion time of a unit. 
    \item reorder\_columns(df): columns are ordered by identifiers, unit structure, building block counts, durations, and proportions.
    \item create\_unit\_parts\_columns(df): the unit column is split into columns for chapter and section.
    \item create\_interaction\_columns(df): creates columns for the count of interactions used in the learning unit and their density. The density is the interaction duration divided by the unit duration.
    \item aggregate\_data(df): creates a new file that contains the data aggregated by the learning unit. The above functions are applied to the cleaned data. Additionally, a new column is created to evaluate whether a unit is multi-codal or not.
    \item create\_type\_transition\_summary(df): creates a new file that captures how often transitions from one to another media element occur in a learning unit. 
\end{itemize}


\subsubsection*{Utility Scripts}
The \texttt{util} directory's \texttt{util.py} script handles general data conversion functions, distinct from direct course content analysis.

\subsubsection*{Visualization Scripts}
The \texttt{visualization} folder includes scripts for creating plots and visual aids, like \texttt{visualize\_by\_course.py} and \texttt{visualize\_by\_unit.py}, to visually represent analysis findings.

\subsection{Constants}
A \texttt{constants.py} file is included for storing dictionaries crucial for the creation of visualizations. This centralizes the management of constants used across different scripts, ensuring consistency in visual outputs.

\section{How to Use?}

\begin{enumerate}
    \item put raw data as .xlsx file into raw folder (if necessary, change file name in line 174)
    \item run preprocess.py using the terminal (py .\/src\/data\/preprocess.py)
    \item run aggregate\_by\_unit.py using the terminal (py .\/src\/data\/aggregate\_by\_unit.py)
    \item run aggregate\_by\_course.py using the terminal (py .\/src\/data\/aggregate\_by\_course.py)
    \item run python -m src.visualization.visualize\_by\_unit using the terminal
\end{enumerate} 

\end{document}
