import numpy as np


def draw_hline(image: np.array, begin: float, end: float, row: float, line_width: int, color, draw_separator=False):
    height, width, channels = image.shape
    begin, end = int(np.round(begin)), int(np.round(end))

    # Clip begin and end within the image
    begin = np.clip(begin, 0, width)
    end = np.clip(end, 0, width)
    row = np.clip(row, 0, height)

    # Check if drawing in reverse
    if begin > end:
        begin, end = end, begin

    if draw_separator:
        image[row:(row + line_width - 1), begin:end, :] = color
        image[row + line_width - 1, begin:end, :] = (color[0], color[1], color[2], color[3] // 2)
    else:
        image[row:(row + line_width), begin:end, :] = color


def draw_vline(image: np.array, begin: float, end: float, col: float, line_width: int, color, draw_separator=False):
    height, width, channels = image.shape
    begin, end = int(np.round(begin)), int(np.round(end))

    # Clip begin and end within the image
    begin = np.clip(begin, 0, height)
    end = np.clip(end, 0, height)
    col = np.clip(col, 0, width)

    # Draw vlines by default from bottom to top
    begin, end = height - begin, height - end

    # Check if drawing in reverse
    if begin > end:
        begin, end = end, begin

    if draw_separator:
        image[begin:end, col:(col + line_width - 1), :] = color
        image[begin:end, col + line_width - 1, :] = (color[0], color[1], color[2], color[3] // 2)
    else:
        image[begin:end, col:(col + line_width), :] = color
