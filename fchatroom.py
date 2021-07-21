from flask import Flask, request, render_template
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kiru0411",
    database="chatroom"
)
mycursor = mydb.cursor()
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import nltk
import liwc
import mail
import os
from collections import Counter
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import re
import enchant
from googletrans import Translator
from datetime import date

translator = Translator()
pwl = enchant.request_pwl_dict("C:\\Users\\Kripa\\Desktop\\englang.txt")

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

tokenizer = RegexpTokenizer(r'\w+')

en_stop = get_stop_words('en')
en_stop.extend(['from', 'subject', 're', 'edu', 'use'])

lemmatizer = WordNetLemmatizer()
texts = []


# Parts of speech
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def tokenize(text):
    for match in re.finditer(r'\w+', text, re.UNICODE):
        yield match.group(0)


def listtostring(s):
    str1 = " "
    return (str1.join(s))

app = Flask(__name__)
from flask_socketio import SocketIO
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def my_form_post():

    if request.method == 'POST':
       id = request.form['id']
       pid = request.form['pid']
       #print(id,pid)
       if id == pid:
           return render_template('login.html')
       else:
           idcheck = "SELECT User_ID from user WHERE User_ID=%s" % int(id)
           mycursor.execute(idcheck)
           idresult1 = mycursor.fetchall()

           if idresult1 == []:
               return render_template('login.html')
           pidcheck = "SELECT User_ID from user WHERE User_ID=%s" % int(pid)
           mycursor.execute(pidcheck)
           idresult2 = mycursor.fetchall()

           if idresult2 == []:
               return render_template('login.html')
           global id1,pid1
           id1 = id
           pid1 = pid

           return render_template('session.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
global message,name
message=""
name=""
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    global id1,pid1



    socketio.emit('my response', json, callback=messageReceived)

    v = list(json.values())

    i = 0
    while i < len(v):
        global message, name
        if i == 0:
            name = v[i]

        if i == 1:
            message = v[i]

        i += 1

    if message!="":
        uname = int(id1)
        pname = int(pid1)
        cid = 0
        sql = "SELECT Chat_ID from chat where (Participant1= %s && Participant2= %s) || (Participant1= %s && Participant2=%s)" %(uname,pname,pname,uname)
        mycursor.execute(sql)
        cid1 = mycursor.fetchone()
        cid = cid1[0]
        # Age Detection
        diff = -1
        # Check if the user is a female

        sql = "SELECT Age_Check FROM user WHERE User_ID=%s" % uname

        mycursor.execute(sql)
        ch1 = mycursor.fetchall()
        sql1 = "SELECT Age_Check FROM user WHERE User_ID=%s" % pname
        mycursor.execute(sql1)
        ch2 = mycursor.fetchall()
        if ch1 == [('No',)] and ch2 == [('No')]:
            c1 = 0
            c2 = 0
            sqll = "SELECT Age_Entered FROM user WHERE User_ID= %s" % uname
            mycursor.execute(sqll)
            age = mycursor.fetchone()
            if age[0] < 18:  # Server(name) is underage so update in monitor table and create user_name table

                sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % uname
                mycursor.execute(sql)
                d = date.today()
                y = int(d.year)
                sql = "INSERT INTO monitor VALUES(%s,%s,%s)" % (uname, age[0], y)
                mycursor.execute(sql)
                tbl = "user_" + str(uname)
                sql = "create table {0} as select Chat_ID,Participant1 as Sender from chat inner join user on user.User_ID=chat.Participant2 where User_ID=%s UNION select Chat_ID,Participant2 as Sender from chat inner join user on user.User_ID=chat.Participant1 where User_ID=%s".format(tbl) % (uname, uname)
                mycursor.execute(sql)
                sql = "alter table {0} add S1 decimal default 0, add S2 decimal default 0, add S3 decimal default 0, add S4 decimal default 0, add S5 decimal default 0, add S6 decimal default 0, add Grooming_Not varchar(3) default 'No'".format(tbl)
                mycursor.execute(sql)
                sql = "alter table {0} add primary key(Chat_ID), add foreign key(Sender) references user(User_ID)".format(tbl)
                mycursor.execute(sql)
            sqll = "SELECT Age_Entered FROM user WHERE User_ID= %s" % pname
            mycursor.execute(sqll)
            age = mycursor.fetchone()
            if age[0] < 18:  # Client(s_name) is underage so update in monitor table and create user_s_name table

                sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % pname
                mycursor.execute(sql)
                d = date.today()
                y = int(d.year)
                sql = "INSERT INTO monitor VALUES(%s,%s,%s)" % (pname, age[0], y)
                mycursor.execute(sql)
                tbl = "user_" + str(pname)
                sql = "create table {0} as select Chat_ID,Participant1 as Sender from chat inner join user on user.User_ID=chat.Participant2 where User_ID=%s UNION select Chat_ID,Participant2 as Sender from chat inner join user on user.User_ID=chat.Participant1 where User_ID=%s".format(
                    tbl) % (pname, pname)
                mycursor.execute(sql)
                sql = "alter table {0} add S1 decimal default 0, add S2 decimal default 0, add S3 decimal default 0, add S4 decimal default 0, add S5 decimal default 0, add S6 decimal default 0, add Grooming_Not varchar(3) default 'No'".format(
                    tbl)
                mycursor.execute(sql)
                sql = "alter table {0} add primary key(Chat_ID), add foreign key(Sender) references user(User_ID)".format(
                    tbl)
                mycursor.execute(sql)
                c2 = 1
            if c1 == 0 or c2 == 0:  # Either participant is above age
                vic_id = 0
                both_vic = 0
                resp = 0
                if c1 == 0 and c2 == 0:  # If both participants are above age
                    both_vic = 1
                if c1 == 0:  # If server(name) is above age
                    vic_id = uname
                    resp = pname
                else:  # If client(s_name) is above age
                    vic_id = pname
                    resp = uname
                sql = "SELECT Start_Date FROM chat WHERE Chat_ID=%s" %cid
                mycursor.execute(sql)
                d = mycursor.fetchone()
                d1 = d[0]
                today = date.today()
                diff = today - d1
                cname = ""


                cname = "C:\\Users\\Kripa\\Desktop\\"+str(cid)+".txt"

                if diff.days < 15:  # Number of days they have been chatting less than 15, write message into chat_id file

                    newsent = ""
                    for word in message.split():
                        d = enchant.DictWithPWL("en_US", "C:\\Users\\Kripa\\Desktop\\englang.txt")
                        if not d.check(word):
                            x = translator.translate(word)
                            newsent += x.text
                        else:
                            newsent += word

                        newsent += " "
                    newsent = newsent.lower()
                    f = open(cname, "a")
                    f.write(str(name))
                    f.write(",")
                    f.write(newsent)
                    f.write("\n")
                    f.close()
                if diff.days >= 15:  # Number of days they have been chatting greater than or equal to 15, call age classifier
                    import age1
                    if both_vic == 1:  # Both participants are above age

                        age1.age_check(cname, uname, pname)
                        age1.age_check(cname, pname, uname)
                        sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % uname
                        mycursor.execute(sql)
                        sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % pname
                        mycursor.execute(sql)
                    else:  # One participant is above age
                        age1.age_check(cname, vic_id, resp)
                        sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % vic_id
                        mycursor.execute(sql)

                    os.remove(cname)


        elif ch1 == [('No',)] or ch2 == [('No',)]:  # One participant is a female
            vic_id = 0
            resp = 0
            if ch1 == [('No',)]:  # Server(name) is female

                vic_id = uname
                resp = pname
            elif ch2 == [('No',)]:  # Client(s_name) is female

                vic_id = pname
                resp = uname
            sqll = "SELECT Age_Entered FROM user WHERE User_ID= %s" % vic_id
            mycursor.execute(sqll)
            age = mycursor.fetchone()
            if age[0] < 18:  # If the female user is underage

                sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % vic_id
                mycursor.execute(sql)
                d = date.today()
                y = int(d.year)
                sql = "INSERT INTO monitor VALUES(%s,%s,%s)" % (vic_id, age[0], y)
                mycursor.execute(sql)
                tbl = "user_" + str(vic_id)
                sql = "create table {0} as select Chat_ID,Participant1 as Sender from chat inner join user on user.User_ID=chat.Participant2 where User_ID=%s UNION select Chat_ID,Participant2 as Sender from chat inner join user on user.User_ID=chat.Participant1 where User_ID=%s".format(
                    tbl) % (vic_id, vic_id)
                mycursor.execute(sql)
                sql = "alter table {0} add S1 decimal default 0, add S2 decimal default 0, add S3 decimal default 0, add S4 decimal default 0, add S5 decimal default 0, add S6 decimal default 0, add Grooming_Not varchar(3) default 'No'".format(
                    tbl)
                mycursor.execute(sql)
                sql = "alter table {0} add primary key(Chat_ID), add foreign key(Sender) references user(User_ID)".format(
                    tbl)
                mycursor.execute(sql)
            else:  # If the female user is above age
                sql = "SELECT Start_Date FROM chat WHERE Chat_ID=%s" %cid
                mycursor.execute(sql)
                d = mycursor.fetchone()
                d1 = d[0]
                today = date.today()
                diff = today - d1
                cname = ""



                cname = "C:\\Users\\Kripa\\Desktop\\" + str(cid) + ".txt"
                if diff.days < 15:  # Number of days they have been chatting less than 15, write message into chat_id file
                    date_ch = 1
                    newsent = ""
                    for word in message.split():
                        d = enchant.DictWithPWL("en_US", "C:\\Users\\Kripa\\Desktop\\englang.txt")
                        if not d.check(word):
                            x = translator.translate(word)
                            newsent += x.text
                        else:
                            newsent += word

                        newsent += " "
                    newsent = newsent.lower()

                    f = open(cname, "a")
                    f.write(str(name))
                    f.write(",")
                    f.write(newsent)
                    f.write("\n")
                    f.close()
                if diff.days >= 15:  # Number of days they have been chatting greater than or equal to 15, call age classifier
                    import age1
                    age1.age_check(cname, vic_id, resp)
                    sql = "UPDATE user SET Age_Check='Yes' WHERE User_ID= %s" % vic_id
                    mycursor.execute(sql)
                    os.remove(cname)




        mydb.commit()
        sql = ("SELECT * FROM monitor WHERE User_ID=%s" % uname)
        sql1 = ("SELECT * FROM monitor WHERE User_ID=%s" % pname)
        mycursor.execute(sql)
        mon = mycursor.fetchall()
        mycursor.execute(sql1)
        mon1 = mycursor.fetchall()
        mon_check = 0
        vic = 0
        pred = 0
        if (mon == [] and mon1 == []):
            mon_check = 1
        elif (mon != [] and mon1 != []):
            mon_check = 1
        else:
            # Pre-processing

            if mon != []:
                vic = uname
                pred = pname
                table = "user_"
                table += str(vic)

            elif mon1 != []:
                pred = uname
                vic = pname
                table = "user_"
                table += str(vic)
            message = message.lower()
            newsent = ""
            print(newsent)
            x = ""
            for word in message.split():
                d = enchant.DictWithPWL("en_US", "C:\\Users\\Kripa\\Desktop\\englang.txt")
                if not d.check(word):
                    x = translator.translate(word)
                    newsent += x.text
                else:
                    newsent += word

                newsent += " "
            newsent = newsent.lower()  # Convert to lowercase
            lemmatizer = WordNetLemmatizer()
            lemr = ""
            for word in newsent.split():  # Lemmatisation
                lem = (lemmatizer.lemmatize(word, pos="v"))
                lem = (lemmatizer.lemmatize(lem))
                lemr = lemr + lem + " "

            no_punct = ""
            for char in lemr:  # Remove punctuation
                if char not in punctuations:
                    no_punct = no_punct + char

            data = word_tokenize(no_punct)

            stopWords = set(stopwords.words('english'))
            wordsFiltered = []

            for w in data:  # Remove stopwords
                if w not in stopWords:
                    wordsFiltered.append(w)
            print(wordsFiltered)

            # liwc
            parse, category_names = liwc.load_token_parser("C:\\Users\\Kripa\\Desktop\\bigdic.dic")

            j = 0

            p = wordsFiltered.copy()

            p1 = listtostring(p).lower()

            p_token = tokenize(p1)

            op1 = Counter(category for token in p_token for category in parse(token))

            op = dict(op1)

            l = list(op.keys())
            l.sort(reverse=True)
            # Store highest stage
            if l:
                j = l[0]

            # Update stage in db
            if j != 0:
                sql = ("UPDATE {1} SET {0}={0}+1 WHERE Sender=%s".format(j, table)) % pred

                mycursor.execute(sql)

                mydb.commit()

            sql = ("SELECT Grooming_Not from {0} WHERE Sender=%s".format(table)) % pred
            mycursor.execute(sql)
            res = mycursor.fetchall()
            check = [('No',)]
            mydb.commit()
            if res == check:
                import svm

                svm.func(table, pred)

                sql = ("SELECT Grooming_Not from {0} WHERE Sender=%s".format(table)) % pred
                mycursor.execute(sql)
                res = mycursor.fetchall()
                check = [('Yes',)]

                # Check if conversation is grooming
                if res == check:
                    mydb.commit()
                    # Alert via mail

                    mail.main_func(vic, pred)

            # If user's age exceeds limit and does not need monitoring
            cur = date.today()
            cur_y = int(cur.year)
            sql = "SELECT Monitor_Year FROM monitor WHERE User_ID = %s" % vic
            mycursor.execute(sql)
            y_ch = mycursor.fetchone()
            if int(y_ch[0]) < cur_y:
                sql = "UPDATE monitor SET Monitor_Year=Monitor_Year+1, Age = Age+1 WHERE User_ID = %s" % vic
                mycursor.execute(sql)
            if mon_check == 0:
                sql = ("SELECT Age from monitor where User_ID=%s" % vic)
                mycursor.execute(sql)
                agech = mycursor.fetchone()
                if int(agech[0]) > 18:
                    # Remove user from monitoring table
                    sql1 = ("DELETE FROM monitor WHERE User_ID=%s" % vic)
                    mycursor.execute(sql1)
                    # Drop the stages table for that user
                    sql1 = "DROP TABLE {0}".format(table)
                    mycursor.execute(sql1)

        mydb.commit()

if __name__ == '__main__':
    app.run()
    socketio.run(app, debug=True)
mycursor.close()
mydb.close()