import numpy as np
import sys
import os

if getattr(sys, 'frozen', False):
    ci_low_before5d = np.loadtxt(os.path.join(sys._MEIPASS, "data\\ci_low_before_5d.txt"))
    ci_high_before5d = np.loadtxt(os.path.join(sys._MEIPASS, "data\\ci_high_before_5d.txt"))
    ci_low_after5d = np.loadtxt(os.path.join(sys._MEIPASS, "data\\ci_low_after_5d.txt"))
    ci_high_after5d = np.loadtxt(os.path.join(sys._MEIPASS, "data\\ci_high_after_5d.txt"))
else:
    ci_low_before5d = np.loadtxt("data\\ci_low_before_5d.txt")
    ci_high_before5d = np.loadtxt("data\\ci_high_before_5d.txt")
    ci_low_after5d = np.loadtxt("data\\ci_low_after_5d.txt")
    ci_high_after5d = np.loadtxt("data\\ci_high_after_5d.txt")

P_low_before5d = np.eye(5, dtype=float)
P_high_before5d = np.eye(5, dtype=float)
P_low_after5d = np.eye(5, dtype=float)
P_high_after5d = np.eye(5, dtype=float)


def generate_trans_probs(comorbidity):
    if comorbidity <= 0:
        P_low_before5d[:3] = ci_low_before5d[:3]
        P_high_before5d[:3] = ci_high_before5d[:3]
        P_low_after5d[:3] = ci_low_after5d[:3]
        P_high_after5d[:3] = ci_high_after5d[:3]
    elif comorbidity <= 3:
        P_low_before5d[:3] = ci_low_before5d[3:6]
        P_high_before5d[:3] = ci_high_before5d[3:6]
        P_low_after5d[:3] = ci_low_after5d[3:6]
        P_high_after5d[:3] = ci_high_after5d[3:6]
    else:
        P_low_before5d[:3] = ci_low_before5d[6:]
        P_high_before5d[:3] = ci_high_before5d[6:]
        P_low_after5d[:3] = ci_low_after5d[6:]
        P_high_after5d[:3] = ci_high_after5d[6:]
    
    random_P_before5d = np.random.uniform(P_low_before5d, P_high_before5d)
    random_P_after5d = np.random.uniform(P_low_after5d, P_high_after5d)
    random_P_before5d[[0, 1, 2], [0, 1, 2]] -= random_P_before5d[:3].sum(axis=1) - 1
    random_P_after5d[[0, 1, 2], [0, 1, 2]] -= random_P_after5d[:3].sum(axis=1) - 1
    return random_P_before5d, random_P_after5d


def count_death_rate(P_before_after, initial_state, duration):
    values = np.array(initial_state, dtype=float)
    P_before5d, P_after5d = P_before_after
    if duration > 5:
        values = np.dot(np.linalg.matrix_power(P_before5d.T, 5), values)
        values = np.dot(np.linalg.matrix_power(P_after5d.T, duration - 5), values)
    else:
        values = np.dot(np.linalg.matrix_power(P_before5d.T, duration), values)
    return values[4]


def bootstrap(comorbidity, initial_state, duration, n_samples=1000, alpha=0.9):
    samples = []
    samples_res = []
    for _ in range(n_samples):
        samples.append(generate_trans_probs(comorbidity))
        samples_res.append(count_death_rate(samples[-1], initial_state, duration))
    samples_res = np.array(samples_res)
    low_res, high_res = np.quantile(samples_res, [(1 - alpha) / 2, (1 + alpha) / 2])
    low_sample_idx = np.argmin(np.abs(samples_res - low_res))
    high_sample_idx = np.argmin(np.abs(samples_res - high_res))
    return samples[low_sample_idx], samples[high_sample_idx]
