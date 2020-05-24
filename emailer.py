import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import app
import datetime
import os
import sys


def readCredentials(name, root=os.path.dirname(sys.argv[0]) + "\\..\\settings.txt"):
    file = open(root, 'r')
    for line in file:
        if name in line:
            line = line.split(',')
            file.close()
            return line[1], line[2] # email, pword or name


if __name__ == "__main__":
    port = 465
    sender_address, password = readCredentials("emailer")
    receiver_address, name = readCredentials("receiver")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Upcoming Tests"
    message["From"] = sender_address
    message["To"] = receiver_address

    testCatalog = app.TestCatalog(doThread=False, root=os.path.dirname(sys.argv[0]) + "\\database.txt")
    upcoming = []
    for test in testCatalog.tests:
        if 24 > (test.date - datetime.datetime.now()).total_seconds() // 3600 > 0: # divide seconds to convert to hours
            upcoming.append(test)

    display = ""
    for test in upcoming:
        display += """\n
           <p><b> Test Name: </b> %s <br>
           <b> Test Time: </b> %s <br>
           <b> Test Description: </b> %s <br>
           </p>
        """ % (test.name, test.date_string, test.description)

    html = """\
    <html>
      <body>
        <p>Hi %s,<br>
           In the next 24 hours you will have %d test(s)<br>
        </p>
        %s
        <p>Happy Studying! :)
      </body>
    </html>
   """ % (name, len(upcoming), display)

    text = MIMEText(html, "html")

    message.attach(text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_address, password)
        server.sendmail(sender_address, receiver_address, message.as_string())
