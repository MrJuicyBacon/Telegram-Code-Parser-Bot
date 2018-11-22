from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from ftplib import FTP
import config
import getpass

selected_phone = eval('config.' + config.user_default + '_phone')
username = config.user_default

client = TelegramClient('session_' + username, eval('config.' + username + '_api_id'), eval('config.' + username + '_api_hash'), update_workers=4)
client.connect()

if not client.is_user_authorized():
	client.sign_in(selected_phone)
	try:
		client.sign_in(code=input('Enter code: '))
	except SessionPasswordNeededError:
		client.sign_in(password=getpass.getpass())
		
client.disconnect()
		
ip = input('ip:')
login = input('username:')
password = input('password:')
try:
	ftp = FTP(ip)
	ftp.login(login, password)
	ftp.cwd('bot')
	file = open('session_' + username + '.session','rb')
	ftp.storbinary('STOR session_' + username + '.session', file)
	file.close()
	ftp.quit()
	print('Session sent successfully')
except Exception as e:
	print('Error sending session: ' + str(e))