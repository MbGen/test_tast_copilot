from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

import numpy as np


# takes array which act like training data
# X -> indexes
# Y -> values
# for_how_long -> how many indexes we have to add and predict
# Example we have X -> [0, 1, 2, 3, 4]
# Y -> [15, 30, 45, 60, 75]
# Prediction will be from [5, 6, 7] or whatever n
def predict_by_linear_regression(x: list[int], for_how_long: int = 3):
    x_train = np.arange(len(x)).reshape(-1, 1)
    y_train = np.array(x).reshape(-1, 1)
    steps = [('scaler', StandardScaler()), ('linear_regression', LinearRegression())]
    pipeline = Pipeline(steps)
    pipeline.fit(x_train, y_train)
    prediction = pipeline.predict(np.arange(len(x), len(x) + for_how_long).reshape(-1, 1))
    return prediction
