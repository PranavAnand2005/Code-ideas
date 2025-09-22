import pandas as pd
import numpy as np

data = pd.read_csv("data.csv")
data.info()

import seaborn as sn
from sklearn import preprocessing

encode = perprocessing.oneHotEncoder()
encode.fit(data[['region']]
encode categories

one_hot = encode.transform(data[['region']]).toarray()

one_hot


