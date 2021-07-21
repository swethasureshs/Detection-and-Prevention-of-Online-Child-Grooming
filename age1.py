import urllib3
import csv
import numpy as np
from array import *
import mysql.connector
from tensorflow import keras
import os
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import liwc
import mysql.connector
import logging
from datetime import date

logging.basicConfig(filename="chat.log", format='%(asctime)s %(message)s')

# Creating an object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kiru0411",
    database="chatroom"
)
mycursor = mydb.cursor()
cntt = array('i',[0,0,0,0,0,0,0,0,0])

subid = ""
def age_check(path,id,id1):

    sql = "SELECT Chat_ID FROM chat WHERE (Participant1 = %s && Participant2 = %s) || (Participant1 = %s && Participant2 = %s)" % (id, id1, id1, id)
    mycursor.execute(sql)
    cid = mycursor.fetchone()

    subid = str(cid[0])
    file_name = path
    file_name1 = "C:\\Users\\Kripa\\Desktop\\"+subid+"1.txt"
    #f = open(file_name1,"w", encoding="utf8")
    with open(file_name, encoding="utf8") as chat:
        chat_text = chat.read()
    sr=""
    for ch in chat_text:
        file1 = open('C:\\Users\\Kripa\\Desktop\\emo.txt', 'r',encoding="utf8")
        Lines = file1.readlines()
        check=0

        # Strips the newline character
        for line in Lines:
            #print(.format(count, line.strip()))
            if ch==line.strip():

                check=1

        if check==0:

            sr+=ch
        else:
            sr+="~"


    f=open(file_name1,"w", encoding="utf8")
    f.write(sr)
    f.close()

    with open(file_name1, 'r') as in_file:
        stripped = (line.strip() for line in in_file)
        lines = (line.split(",") for line in stripped if line)

        with open('C:\\Users\\Kripa\\Desktop\\'+subid+'1.csv', 'w', newline='') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(('name', 'msg'))
            writer.writerows(lines)


    line=0
    punct= '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

    with open("C:\\Users\\Kripa\\Desktop\\"+subid+"1.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:

            if row[0] == str(id):


                line += 1
                cntt[0] += len(row[1].split())
                x=0
                sr = ""
                for val in row[1]:
                    if val=='~':
                        cntt[5]+=1
                    if val in punct:
                        cntt[2]+=1
                    else:
                        sr+=val
                    x+=1
                cntt[1]+=int(x/len(row[1].split()))

                for word in sr.split():
                    with open('C:\\Users\\Kripa\\Desktop\\slangdic.csv') as csv_file1:
                        csv_reader1 = csv.reader(csv_file1, delimiter=',')

                        for row1 in csv_reader1:

                            if word == row1[0]:

                                cntt[4] += 1

                    duplicates = []

                    for char in word:
                    ## checking whether the character have a duplicate or not
                    ## str.count(char) returns the frequency of a char in the str
                        if word.count(char) > 2:
                        ## appending to the list if it's already not present
                            if char not in duplicates:
                                duplicates.append(char)
                    cntt[3]+=len(duplicates)



    cntt[0]=int(cntt[0]/line)
    cntt[1]=int(cntt[1]/line)
    cntt[2]=cntt[2]-cntt[5]


    sql = "SELECT Posts, Followers, Following FROM user WHERE User_ID=%s" %id
    mycursor.execute(sql)
    res = mycursor.fetchone()
    cntt[6] = res[0]
    cntt[7] = res[1]
    cntt[8] = res[2]

    cn = np.asarray([cntt])
    cn = cn.astype('float64')


    model = keras.models.load_model("dnn21")
    predictions = model.predict_classes(cn)
    if predictions == [[1]]:
        logger.info("Female is underage")


        lst = []
        line_count = 0
        lt = 0
        with open('C:\\Users\\Kripa\\Desktop\\age_ask.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                lst.append(row[0])
        with open('C:\\Users\\Kripa\\Desktop\\'+subid+'1.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                #print(row[0], id1)
                line_count = line_count + 1
                if row[0] == str(id1):
                    for ele in lst:

                        if ele in row[1]:

                            lt = line_count
                            break

        range = 0
        ag_ch = 0
        ln_ct = 0
        age_final = 0
        with open('C:\\Users\\Kripa\\Desktop\\'+subid+'1.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if ln_ct >= lt:
                    ln_ct = ln_ct + 1
                    if row[0] == str(id) and range < 10:
                        range = range + 1

                        for word in row[1].split():

                            if word.isnumeric():

                                a = int(word)

                                if a >= 12 and a <= 18:
                                    age_final = a
                                    ag_ch = 1
                else:
                    ln_ct = ln_ct + 1

                if ag_ch == 1:
                    logger.info("Obtained age of female")
                    break
        if age_final == 0:
            age_final = 14
        d = date.today()
        y = int(d.year)
        sql = "INSERT INTO monitor VALUES(%s,%s,%s)" % (id,age_final,y)
        mycursor.execute(sql)
        tbl = "user_" + str(id)
        sql = "create table {0} as select Chat_ID,Participant1 as Sender from chat inner join user on user.User_ID=chat.Participant2 where User_ID=%s UNION select Chat_ID,Participant2 as Sender from chat inner join user on user.User_ID=chat.Participant1 where User_ID=%s".format(tbl) % (id, id)
        mycursor.execute(sql)
        sql = "alter table {0} add S1 decimal default 0, add S2 decimal default 0, add S3 decimal default 0, add S4 decimal default 0, add S5 decimal default 0, add S6 decimal default 0, add Grooming_Not varchar(3) default 'No'".format(tbl)
        mycursor.execute(sql)
        sql = "alter table {0} add primary key(Chat_ID), add foreign key(Sender) references user(User_ID)".format(tbl)
        mycursor.execute(sql)
        with open('C:\\Users\\Kripa\\Desktop\\'+subid+'1.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                row[1] = row[1].lower()
                lemmatizer = WordNetLemmatizer()
                lemr = ""
                for word in row[1].split():
                    lem = (lemmatizer.lemmatize(word, pos="v"))
                    lem = (lemmatizer.lemmatize(lem))
                    lemr = lemr + lem + " "
                no_punct = ""
                for char in lemr:
                    if char not in punctuations:
                        no_punct = no_punct + char

                data = word_tokenize(no_punct)
                line_count += 1
                stopWords = set(stopwords.words('english'))
                wordsFiltered = []

                for w in data:
                    if w not in stopWords:
                        wordsFiltered.append(w)
                pred = "C:\\Users\\Kripa\\Desktop\\" + subid + "2.csv"
                with open(pred, 'a+', newline='') as out_file:
                    writer = csv.writer(out_file, delimiter=' ')
                    writer.writerow(wordsFiltered[:20])

        def tokenize(text):
            for match in re.finditer(r'\w+', text, re.UNICODE):
                yield match.group(0)

        def listtostring(s):
            str1 = " "
            return (str1.join(s))

        parse, category_names = liwc.load_token_parser("C:\\Users\\Kripa\\Desktop\\bigdic.dic")
        cnt = array('i', [0, 0, 0, 0, 0, 0])
        predator = "C:\\Users\\Kripa\\Desktop\\" + subid + "2.csv"
        with open(predator) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            j = 0
            for row in csv_reader:

                p = row.copy()

                p1 = listtostring(p).lower()
                p_token = tokenize(p1)
                from collections import Counter
                op1 = Counter(category for token in p_token for category in parse(token))
                op = dict(op1)
                l = list(op.keys())
                l.sort(reverse=True)
                if l:
                    j = l[0]

                if j == "S1":
                    cnt[0] = cnt[0] + 1
                if j == "S2":
                    cnt[1] = cnt[1] + 1
                if j == "S3":
                    cnt[2] = cnt[2] + 1
                if j == "S4":
                    cnt[3] = cnt[3] + 1
                if j == "S5":
                    cnt[4] = cnt[4] + 1
                if j == "S6":
                    cnt[5] = cnt[5] + 1

        sql = ("UPDATE {0} SET S1=%s, S2=%s, S3=%s, S4=%s, S5=%s, S6=%s WHERE Sender=%s".format(tbl)) %(cnt[0], cnt[1], cnt[2], cnt[3], cnt[4], cnt[5], id1)
        mycursor.execute(sql)
        logger.info("Grooming stages updated")
        mydb.commit()
        import svm

        svm.func(tbl, id1)

        sql = ("SELECT Grooming_Not from {0} WHERE Sender=%s".format(tbl)) % id1
        mycursor.execute(sql)
        logger.info("Grooming characteristics checked")
        ress = mycursor.fetchall()
        check = [('Yes',)]

        # Check if conversation is grooming
        if ress == check:
            mydb.commit()
            # Alert via mail
            import mail
            mail.main_func(id, id1)
            logger.info("Grooming detected. Mail sent")
        os.remove('C:\\Users\\Kripa\\Desktop\\' + subid + '2.csv')

    os.remove(file_name1)
    os.remove('C:\\Users\\Kripa\\Desktop\\'+subid+'1.csv')





'''''
cntt[0] avg no of words per sentence
cntt[1] avg no of charac per word
cntt[2] no of punctuations used
cntt[3] occurrence of duplicate charac in word
cntt[4] slang,abbr,acronym
cntt[5] no of emoji
cntt[6] no of posts
cntt[7] no of followers
cntt[8] no of following
'''''