import smtplib, ssl

# on rentre les renseignements pris sur le site du fournisseur
smtp_address = 'localhost'
smtp_port = 25

# on rentre les informations sur notre adresse e-mail
email_address = 'morel.l@free.fr'



# on rentre les informations sur le destinataire
email_receiver = 'morel.l@ecomail.fr'

# on crée la connexion

with smtplib.SMTP(smtp_address, smtp_port) as server:
  print('connexion OK')
  # envoi du mail
  server.sendmail(email_address, email_receiver, 'contenu')
