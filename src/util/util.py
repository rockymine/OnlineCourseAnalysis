import numpy as np
import matplotlib.colors as mcolors


def format_string(s):
    s = s.replace('_', ' ')  # Replace all underscores with spaces
    s = s.split(' ')  # Split the string into a list of words
    s = [word.capitalize() for word in s]  # Capitalize the first letter of each word
    s = ' '.join(s)  # Join the words back together into a single string
    return s


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    name = f'trunc({minval},{maxval}){cmap.name}'
    new_cmap = mcolors.LinearSegmentedColormap.from_list(name,cmap(np.linspace(minval, maxval, n)))
    return new_cmap
