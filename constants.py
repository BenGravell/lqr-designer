import numpy as np


NUM_STATES = 2
NUM_ACTIONS = 1

DT = 0.01  # time delta, seconds

Ac = np.array([[-2, 13], [4, -3]])
Bc = np.array([[2], [8]])
Q = np.diag([1, 1])
R = np.diag([1])

A = np.eye(NUM_STATES) + DT * Ac
B = DT * Bc

NUM_TIMESTEPS = 100
