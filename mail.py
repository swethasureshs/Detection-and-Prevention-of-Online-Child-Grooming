#send mail to moderator

from string  import Template
import smtplib

#get name and mailid of receiver from contact.txt
def get_contacts(contacts):
    names=[]
    emails=[]
    with open(contacts,mode='r',encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names,emails


#message to be sent(message.txt)
def read_template(message):
    with open(message,'r',encoding='utf-8') as template_file:
        template_file_content=template_file.read()
    return Template(template_file_content)

#main function
def main_func(victim,predator):
    MY_ADDRESS="axkatey@gmail.com"
    MY_PASSWORD="iamaxe#4"
    victim = str(victim)
    predator = str(predator)

    s=smtplib.SMTP(host='smtp.gmail.com',port=587)
    s.starttls() #setting up connection
    s.login(MY_ADDRESS, MY_PASSWORD)

#function calls to get contacts and message from the respective text files
    names,emails=get_contacts(r"C:\Users\kripa\Desktop\contacts.txt")
    message_template=read_template(r"C:\Users\kripa\Desktop\message.txt")

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    for name,email in zip(names, emails):
        msg=MIMEMultipart()  #create message
        message = message_template.substitute(PERSON_NAME=name.title(), VICTIM_NAME=victim.title(), PREDATOR_NAME=predator.title())

        msg['From']=MY_ADDRESS
        msg['To']=email
        msg['Subject']="Possible Grooming Alert!"

    #add message
        msg.attach(MIMEText(message,'plain'))

    #send
        s.send_message(msg)
        del msg

#closing connection
    s.quit()

