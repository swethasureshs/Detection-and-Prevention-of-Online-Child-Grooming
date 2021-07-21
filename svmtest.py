#testing svm
import joblib
import pandas as pd
import numpy as np

# Loading the model from the pickle file
clf = joblib.load('svm.pkl')
fname = pd.read_csv("C:\\Users\\Kripa\\Desktop\\ipclssf(test).csv")
#predicting
op = clf.predict(fname)
np.savetxt("C:\\Users\\Kripa\\Desktop\\opclssf(test).csv", op, delimiter=",")