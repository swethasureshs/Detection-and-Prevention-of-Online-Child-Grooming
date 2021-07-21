#DNN training/validation

import csv
from keras.layers import Dense
from keras.models import Sequential
import numpy as np
# For training
X = "C:\\Users\\HP\\Desktop\\iptrain.csv"
y = "C:\\Users\\HP\\Desktop\\optrain.csv"
X_train = []
y_train = []
with open(X) as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # change contents to float
    for row in reader:  # each row is a list
        X_train.append(row)
with open(y) as csvfile1:
    reader1 = csv.reader(csvfile1, quoting=csv.QUOTE_NONNUMERIC)  # change contents to float

    for row in reader1:  # each row is a list
        y_train.append(row)
#For validation


q = "C:\\Users\\HP\\Desktop\\ipvalid.csv"
p = "C:\\Users\\HP\\Desktop\\opvalid.csv"
q_train = []
p_train = []
with open(q) as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # change contents to floats
    for row in reader:  # each row is a list
        q_train.append(row)
with open(p) as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # change contents to floats

    for row in reader:  # each row is a list
        p_train.append(row)


#validation part
X_test = np.array(q_train)
y_test = np.array(p_train)


X_t = np.array(X_train)
y_t = np.array(y_train)


model = Sequential()
model.add(Dense(34, input_dim=9, activation='relu'))
model.add(Dense(4, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# fit the keras model on the dataset
model.fit(X_t, y_t, validation_data=(X_test,y_test), epochs=60, batch_size=10)
#model.fit(X_t, y_t, epochs=70, batch_size=10)
model.save("dnn24")



#Syntax for training along with validation to find max validation accuracy and min validation loss

#model.fit(X_t,y_t, validation_data=(X_test,y_test),epochs=70,batch_size=10)


