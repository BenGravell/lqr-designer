import numpy as np

import utils


def test_matrix_to_latex():
    A = np.array([[1, 2], [3, 4]])
    assert utils.matrix_to_latex(A) == r"\begin{bmatrix}1 & 2\\3 & 4\end{bmatrix}"
