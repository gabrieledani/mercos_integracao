# In[] Import libraries
import configparser
import os
import datetime

import processa_file_pdf

import requests
from bs4 import BeautifulSoup
from imap_tools import MailBox, AND

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# In[] Config parsing
config = configparser.ConfigParser()
config.read('config.ini')

dir_pdf = config['CAMINHO_PDF']['dir_pdf']
dir_edi = config['CAMINHO_EDI']['dir_edi']
dir_log = config['LOG']['dir_log']

log_file = open(os.path.join(dir_log,'app_log.txt'),'a')

sender_email = config['E_MAIL']['sender_email']
receiver_email = config['E_MAIL']['receiver_email']

smtp_server = config['E_MAIL']['smtp_server']
smtp_port = int(config['E_MAIL']['smtp_port'])
imap_server = config['E_MAIL']['smtp_server']

login = config['E_MAIL']['login']
password = config['E_MAIL']['password']

# In[] Send
def send_mail(filename,subject,body):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    msgText = MIMEText('<b>%s</b>' % (body), 'html')
    msg.attach(msgText)

    fil = open(os.path.join(dir_edi,filename), "rb")
    
    part = MIMEApplication(fil.read(),Name=os.path.basename(filename))    
    part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filename)
    msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtpObj:
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(login, password)
            smtpObj.sendmail(sender_email, receiver_email, msg.as_string())
            log_file.write(str(datetime.datetime.now())+'--success\n')
            print('Sent Success!')
            return 'success'
    except Exception as e:
        print('Send Error:',e)
        log_file.write(str(datetime.datetime.now())+'--'+str(e)+'\n')
        return e

# In[] Read
def read_mail():
    # get unseen emails sent by vedafil from INBOX folder
    mailbox = MailBox(imap_server).login(login, password, 'INBOX')

    # *mark emails as seen on fetch, see mark_seen arg
    for msg in mailbox.fetch(AND(from_='vendas@vedafil', seen=False)):#,mark_seen=False):  
        subject = msg.subject
        print(subject)
        log_file.write(subject+'\n')
        
        pedido = subject[subject.find('Nº')+3:subject.find('-')-1] 
        print(pedido)
        log_file.write(pedido+'\n')
        
        body = msg.html
        #print(body)

        soup = BeautifulSoup(body, 'html.parser')

        link = soup.find_all('a')
        # URL from which pdfs to be downloaded
        pdf_file_url = link[1].get('href', [])
        #print(link[1].get('href', []))
        
        text = soup.find_all('div')
        content = text[2].text
        att = content.find('Atenciosamente')
        content = content[:att]+'\n'+content[att:]
        if content.find('Hengst / Hengst Indústria de Filtros Ltda')>=0:
            content = ''
        #print(content)

        # Requests URL and get response object
        response = requests.get(pdf_file_url)

        # Parse text obtained
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all hyperlinks present on webpage
        links = soup.find_all('a')
        i = 0

        # From all links check for pdf link and if present download file
        #for link in links:
        link = links[0]
        error = 0
        edi_filename = ''
        if ('.pdf' in link.get('href', [])):
            i += 1
            print("Downloading file: ", i)
            log_file.write("Downloading file: "+ str(i)+'\n')

            # Get response object for link
            response = requests.get(link.get('href'))

            # Write content in pdf file
            file = pedido+".pdf"
            pdf = open(os.path.join(dir_pdf,file), 'wb')
            pdf.write(response.content)
            pdf.close()
            print("PDF File ", os.path.join(dir_pdf,pedido+".pdf"), " downloaded")
            log_file.write("File "+ os.path.join(dir_pdf,pedido+".pdf")+ " downloaded\n")

            #Generate EDI from PDF
            edi_filename = ''
            edi_filename = processa_file_pdf.processa_file(file,dir_edi,dir_pdf,dir_log)
            print('EDI File:',edi_filename)
            try:
                os.rename(os.path.join(dir_pdf,file) , os.path.join(dir_pdf,file+'_ok'))
            except:
                os.rename(os.path.join(dir_pdf,file) , os.path.join(dir_pdf,file+'_erro'))
        if edi_filename != '' and edi_filename != 'error':
            #Send EDI file to e-mail
            error = send_mail(edi_filename,subject,content)
            if error == 'success':
                try:
                    os.rename(os.path.join(dir_edi,edi_filename) , os.path.join(dir_edi,edi_filename+'_ok'))
                except:
                    os.rename(os.path.join(dir_edi,edi_filename) , os.path.join(dir_edi,edi_filename+'_erro'))
            else:
                print('Sending error:',edi_filename)
        else:
            print('EDI File converting error:',file)

# In[] Main
if __name__ == '__main__':
    #Read new e-mails
    print('Start')
    log_file.write(str(datetime.datetime.now())+'Start'+'\n')
    read_mail()
    print('End!')
    log_file.write(str(datetime.datetime.now())+'End!'+'\n')
