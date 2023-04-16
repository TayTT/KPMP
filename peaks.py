import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as sc
import numpy as np

def find_peaks_magn(df):
    df.reset_index(inplace=True)
    print(df)
    diff_mag = df["mag_diff"].to_numpy()

    peaks, _ = sc.find_peaks(diff_mag, distance=25, height = 10_000)
    np.diff(peaks)

    mask = diff_mag[peaks] > 15_000
    thrown = peaks[mask]
    print(thrown)
    
    return thrown
