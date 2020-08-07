import yagmail

# Sets up yagmail registration with email and password in local text file
def mailSetup():
    file = open('EmailCredentials.txt')
    lines = file.readlines()
    email = lines[0]
    password = lines[1]
    yagmail.register(email, password)
    return yagmail.SMTP(email)

# Sends email to specified address
def sendEmail(title, email, description, wellmap):
    yag = mailSetup()
    attachments = ['History/{}/{}'.format(title, title)]
    if wellmap != None:
        attachments.append('History/{}/{}'.format(title, wellmap))
    yag.send(to=email, subject=title, contents=description, attachments=attachments)

