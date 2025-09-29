import smtplib, ssl

# on rentre les renseignements pris sur le site du fournisseur
smtp_address = 'localhost'
smtp_port = 25

# on rentre les informations sur notre adresse e-mail
email_address = 'morel.l@free.fr'



def send_verification_mail(email, link_password_reset):
    with smtplib.SMTP(smtp_address, smtp_port) as server:
        server.sendmail(email_address, email, f""" Hello, {email} \n here is your password reset link: https://{link_password_reset}""")
