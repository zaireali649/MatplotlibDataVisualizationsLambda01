#%%

import pandas as pd
import matplotlib.pyplot as plt

#%%

try:    
    data_df = pd.read_csv("raw_data.csv")
    col_name = data_df.columns[0]
    data = data_df[col_name]
    plt.plot(data, label=col_name)
    plt.legend(loc="upper left")
    plt.savefig('offline_plot.png')
    plt.show()
except:
    pass

