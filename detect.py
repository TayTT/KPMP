# %% imports
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as sc
import numpy as np

df = pd.read_table("./dane3.txt")
columns = df.columns
df.reset_index(inplace=True)

df = df.iloc[:,:-1]
df.columns = columns
df.head()

df.iloc[:,4:].plot()
# %%
fig, ax1 = plt.subplots()

ax1.plot(df.diff_mag, color = 'r')
ax1.tick_params(axis='y')

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.plot(df.mag)
ax2.tick_params(axis='y')

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

diff_mag = df.diff_mag.to_numpy()

peaks, _ = sc.find_peaks(diff_mag, distance=150, height = 10_000)
np.diff(peaks)

mask = diff_mag[peaks] > 20_000
thrown = peaks[mask]

plt.plot(diff_mag)
plt.plot(thrown, diff_mag[thrown], "x", markersize=14)
plt.plot(peaks, diff_mag[peaks], "o")

plt.legend(['diff_mag', 'thrown', 'peaks'])
plt.show()


mask = x[peaks] > 15_000
# %%
