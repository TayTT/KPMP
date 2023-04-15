import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as sc
import numpy as np

data = pd.read_table("./dane3.txt")

def find_peaks_magn(df):
    columns = df.columns
    df.reset_index(inplace=True)

    df = df.iloc[:,:-1]
    df.columns = columns
    df.head()

    diff_mag = df.diff_mag.to_numpy()

    peaks, _ = sc.find_peaks(diff_mag, distance=150, height = 10_000)
    np.diff(peaks)

    mask = diff_mag[peaks] > 20_000
    thrown = peaks[mask]

    plt.plot(diff_mag)
    plt.plot(thrown, diff_mag[thrown], "x", markersize=14)
    plt.plot(peaks, diff_mag[peaks], "o")

    plt.legend(['diff_mag','thrown','peaks'])
    plt.show()
    return thrown

t = find_peaks_magn(data)
print(t)