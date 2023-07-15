# Import libraries
import imaplib
print('1')
# Set up the IMAP connection
mail = imaplib.IMAP4_SSL('email-ssl.com.br')
print('2')
mail.login('pedidos@vedafil.com.br', 'Vdfil.2022')
print('3')
status, messages = mail.select('inbox')
print('4')
print(messages[0])
    
# Close the connection
mail.close()
mail.logout()