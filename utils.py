import numpy as np


def matrix_to_latex(matrix):
    if not isinstance(matrix, np.ndarray):
        raise ValueError("Input must be a numpy array")

    latex_str = "\\begin{bmatrix}"
    rows, cols = matrix.shape

    for i in range(rows):
        row_str = " & ".join(str(matrix[i, j]) for j in range(cols))
        latex_str += row_str
        if i < rows - 1:
            latex_str += "\\\\"

    latex_str += "\\end{bmatrix}"
    return latex_str
