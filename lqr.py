import numpy as np
import scipy as sp
import pandas as pd

import constants


def compute_gain(A, B, Q, R):
    X = sp.linalg.solve_discrete_are(A, B, Q, R)
    K = -np.linalg.solve(R + B.T @ X @ B, B.T @ X @ A)
    return K


def compute_system_response(A, B, Q, R):
    K = compute_gain(A, B, Q, R)

    x = np.ones(constants.NUM_STATES)
    xs = [np.copy(x)]
    us = []
    for i in range(constants.NUM_TIMESTEPS):
        u = K @ x
        x = A @ x + B @ u
        xs.append(np.copy(x))
        us.append(u)
    xs = np.array(xs[:-1])
    us = np.array(us)

    time_dict = {"t": constants.DT * np.arange(constants.NUM_TIMESTEPS)}
    state_dict = {f"state_{i}": xs[:, i] for i in range(constants.NUM_STATES)}
    action_dict = {f"action_{i}": us[:, i] for i in range(constants.NUM_ACTIONS)}

    df = pd.DataFrame({**time_dict, **state_dict, **action_dict})

    return df


def create_matrix_A():
    return np.copy(constants.A)


def create_matrix_B():
    return np.copy(constants.B)


def create_matrix_Q(state_penalty_0, state_penalty_1):
    Q_here = np.copy(constants.Q)
    if state_penalty_0 is not None:
        Q_here[0, 0] = np.copy(state_penalty_0)
    if state_penalty_1 is not None:
        Q_here[1, 1] = np.copy(state_penalty_1)
    return Q_here


def create_matrix_R(action_penalty_0):
    R_here = np.copy(constants.R)
    if action_penalty_0 is not None:
        R_here[0, 0] = np.copy(action_penalty_0)
    return R_here


def create_system_matrices(state_penalty_0, state_penalty_1, action_penalty_0):
    return (
        create_matrix_A(),
        create_matrix_B(),
        create_matrix_Q(state_penalty_0, state_penalty_1),
        create_matrix_R(action_penalty_0),
    )


def get_df(state_penalty_0, state_penalty_1, action_penalty_0):
    A_here, B_here, Q_here, R_here = create_system_matrices(state_penalty_0, state_penalty_1, action_penalty_0)
    return compute_system_response(A_here, B_here, Q_here, R_here)
