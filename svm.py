#SVM classifier code for chatroom

import pandas as pd
import joblib
import mysql.connector


##x = pd.read_csv("C:\\Users\\Kripa\\Desktop\\inputclssf.csv")
#y = pd.read_csv("C:\\Users\\Kripa\\Desktop\\opclssf.csv")  # classes having 0 and 1

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Kiru0411",
  database="chatroom"
)
mycursor = mydb.cursor()

#function to check grooming or not
def func(table, sender):

    sql= "SELECT S1,S2,S3,S4,S5,S6 from {0} WHERE Sender=%s".format(table) %sender
    mycursor.execute(sql)
    res=mycursor.fetchall()

    #Load saved model
    clf = joblib.load('svm.pkl')
    op = clf.predict(res)
    #Check if grooming
    if op==[1]:
        sql="UPDATE {0} set Grooming_Not='Yes' WHERE Sender=%s".format(table) %sender
    else:
        sql = "UPDATE {0} set Grooming_Not='No' WHERE Sender=%s".format(table) %sender
    mycursor.execute(sql)
    mydb.commit()

