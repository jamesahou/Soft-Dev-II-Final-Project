import smtplib, ssl

def readCredentials(root="../settings.txt"):
    file = open(root, 'r')
    for line in file:
        if "emailer" in line:
            line = line.split(',')
            return line[1], line[2] # email, user


if __name__ == "__main__":
    port = 465
    sender_address, password = readCredentials()
    receiver_address = sender_address
    message = """\
    Subject: Hi there

    This message is sent from Python."""

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_address, password)
        server.sendmail(sender_address, receiver_address, message)