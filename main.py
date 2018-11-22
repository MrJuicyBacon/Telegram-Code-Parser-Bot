from telethon import TelegramClient, events
from telethon.tl.types import (
    Message, UpdateNewChannelMessage, UpdateEditChannelMessage, UpdateNewMessage, UpdateShortMessage, UpdateShortSentMessage,
    PeerUser, InputPeerUser, InputPeerChat, PeerChannel, InputPeerChannel, MessageEmpty,
    ChatInvite, ChatInviteAlready, Photo, InputPeerSelf, MessageService, MessageEntityUrl )
from telethon.tl.functions.messages import SendMessageRequest
from telethon.utils import get_display_name
from telethon.errors import SessionPasswordNeededError

import os, re, getpass, urllib.request
from time import sleep
from pyzbar.pyzbar import decode
from PIL import Image
import requests

import config

def findInTelegraph(url):
	codes_found = 0
	if ('telegra.ph' in url) and (not '.jpg' in url) and (not url in used_telegraph_urls):
		used_telegraph_urls.append(url)
		if not 'http://' in url:
			url = 'http://' + url
		try:
			f = urllib.request.urlopen(url)
			html_bytes = f.read()
			f.close()
			html_str = html_bytes.decode("utf8")
			codes_found += findCode(html_str)
		except Exception as e:
			print('Error processing telegra.ph url:\n', url, '\n', e)
	return codes_found

def findCode(string):
	codes_found = 0
	if re.search(main_regex, string):
		for bot, code in re.findall(main_regex, string):
			code = code.replace(' ', '')
			
			if not bot in used_strings:
				used_strings[bot] = []
			
			if not code in used_strings[bot]:
				used_strings[bot].append(code)
				
				if (bot == 'first_bot'):
					peer = first_input_entity
				elif (bot == 'second_bot'):
					peer = second_input_entity
				elif (bot == 'third_bot'):
					peer = third_input_entity
				elif (bot == 'fourth_bot'):
					peer = fourth_input_entity
				elif (bot == 'fifth_bot'):
					peer = fifth_input_entity
				elif (bot == 'sixth_bot'):
					peer = sixth_input_entity
				else:
					peer = client.get_input_entity(bot)
					
				client(SendMessageRequest(peer, '/start ' + code))
				
				print('Bot code ' + str(code) + ' for ' + str(bot) + ' sent')
			else:
				print('Bot code ' + str(code) + ' for ' + str(bot) + ' is duplicate')
			
			codes_found += 1
	return codes_found

def ProcessRawUpdate(update):
	if not isinstance(update.message, MessageService) and (hasattr(update.message.to_id, 'channel_id') and not update.message.to_id.channel_id in exception_channels):
		if isinstance(update, (UpdateNewChannelMessage, UpdateEditChannelMessage, UpdateNewMessage)):
			try:
				
				##Get message text and sender
				msg = update.message.message
				who = client.get_entity(update.message.to_id)
				
				if hasattr(who, 'title'):
					who_str = '"' + str(who.title) + '" (' + str(who.id) + ')'
				else:
					who_str = str(who.id)
				
				##Process main message
				codes_found = 0
				
				codes_found += findCode(msg)
				
				session = None
				
				if (who.id in antibot_channels):
					if re.search('пароль (\S+), далее', msg):
						nums = eval(os.environ.get('ANTIBOT_NUMS'))
						
						anti_password = re.findall('пароль (\S+), далее', msg)[0]
						print('Password for antibot channel: ' + anti_password)
						try:
							session = requests.Session()
							session.headers.update({"User-Agent": "runscope/0.1"})
							session.post("https://site.com/wp-login.php?action=postpass", data={"post_password": anti_password})
							for cookie in session.cookies:
								cookie.expires = None
							num = 1
						except Exception as e:
							print("Exception occured in antibot session getter block: ", str(e))
				
				if (update.message.entities):
					for entity in update.message.entities:
						if hasattr(entity, 'url'):
							codes_found += findCode(entity.url)
							if session and re.search('site.com/\S+', entity.url):
								print('URL = ' + str(entity.url))

								if (num in nums):
									x = session.get(entity.url)
									codes_found += findCode(x.text)
								num += 1
							codes_found += findInTelegraph(entity.url)
						elif isinstance(entity, MessageEntityUrl):
							try:
								##Removing all emojis from text
								highpoints = re.compile("["
									u"\U0001F004" u"\U0001F9FA" u"\U000E0062-\U000E0063" u"\U000E0065" u"\U000E0067" u"\U000E006C" u"\U000E006E" u"\U000E0073-\U000E0074" u"\U000E0077" u"\U0001F9EF"
									u"\U000E007F" u"\U0001F9ED" u"\U0001F970" u"\U0001F9FB" u"\U0001F9E6" u"\U0001F0CF" u"\U0001F9FC" u"\U0001F9E7" u"\U0001F9EA" u"\U0001F97E-\U0001F97F"
									u"\U0001F9E8" u"\U0001F910-\U0001F93A" u"\U0001F93C-\U0001F93E" u"\U0001F940-\U0001F945" u"\U0001F947-\U0001F96F" u"\U0001F170-\U0001F171" u"\U0001F973-\U0001F976"
									u"\U0001F994" u"\U0001F97A" u"\U0001F97C-\U0001F97D" u"\U0001F17E-\U0001F17F" u"\U0001F980-\U0001F98D" u"\U0001F18E" u"\U0001F98F-\U0001F990"
									u"\U0001F191-\U0001F19A" u"\U0001F99B-\U0001F99C" u"\U0001F99A" u"\U0001F99E-\U0001F9A2" u"\U0001F99D" u"\U0001F9B0-\U0001F9B9" u"\U0001F9C0-\U0001F9C2"
									u"\U0001F9D0-\U0001F9E5" u"\U0001F1E6-\U0001F1FF" u"\U0001F201-\U0001F202" u"\U0001F9F1" u"\U0001F21A" u"\U0001F22F" u"\U0001F9F2" u"\U0001F232-\U0001F23A"
									u"\U0001F9F0" u"\U0001F9F3" u"\U0001F250-\U0001F251" u"\U0001F9F4" u"\U0001F9FE" u"\U0001F9F5" u"\U0001F991" u"\U0001F9F6-\U0001F9F8" u"\U0001F300-\U0001F321"
									u"\U0001F324-\U0001F393" u"\U0001F9EE" u"\U0001F396-\U0001F397" u"\U0001F399-\U0001F39B" u"\U0001F39E-\U0001F3F0" u"\U0001F3F3-\U0001F3F5" u"\U0001F3F7-\U0001F3FA"
									u"\U0001F9FF" u"\U0001F400-\U0001F4FD" u"\U0001F4FF-\U0001F53D" u"\U0001F549-\U0001F54E" u"\U0001F550-\U0001F567" u"\U0001F56F-\U0001F570" u"\U0001F573-\U0001F57A"
									u"\U0001F587" u"\U0001F58A-\U0001F58D" u"\U0001F590" u"\U0001F595-\U0001F596" u"\U0001F5A4-\U0001F5A5" u"\U0001F5A8" u"\U0001F5B1-\U0001F5B2" u"\U0001F5BC"
									u"\U0001F5C2-\U0001F5C4" u"\U0001F5D1-\U0001F5D3" u"\U0001F5DC-\U0001F5DE" u"\U0001F5E1" u"\U0001F5E3" u"\U0001F5E8" u"\U0001F5EF" u"\U0001F5F3"
									u"\U0001F5FA-\U0001F64F" u"\U0001F98E" u"\U0001F680-\U0001F6C5" u"\U0001F6CB-\U0001F6D2" u"\U0001F6E0-\U0001F6E5" u"\U0001F6E9" u"\U0001F9E9"
									u"\U0001F6EB-\U0001F6EC" u"\U0001F992" u"\U0001F6F0" u"\U0001F6F3-\U0001F6F9" u"\U0001F993" u"\U0001F995" u"\U0001F9EB" u"\U0001F996-\U0001F997"
									u"\U0001F9FD" u"\U0001F9F9" u"\U0001F998-\U0001F999" u"\U0001F9EC"
									u"\U0000200D"
									"]", flags=re.UNICODE
								)
								codes_found += findInTelegraph(re.sub(highpoints, '00', msg)[entity.offset:entity.offset+entity.length])
							except Exception as e:
								print('Error removing emojis:', e)
								
				##Process caption and buttons
				if (update.message.media):
					if hasattr(update.message.media, 'caption') and (update.message.media.caption):
						codes_found += findCode(update.message.media.caption)
				
				if (update.message.reply_markup):
					codes_found += findCode(str(update.message.reply_markup))
				
				##Process qr image
				if (who.id in qr_channels):
					if hasattr(update.message.media, 'photo'):
						c = decode(Image.open(client.download_media(update.message, username + '/')))
					elif hasattr(update.message.media, 'webpage') and hasattr(update.message.media.webpage, 'photo'):
						c = decode(Image.open(client.download_media(update.message.media.webpage.photo, username + '/')))
					else:
						c = None
							
					if c:
						try:
							for code in c:
								print(code.type + ' = ' + code.data.decode())
								codes_found += findCode(code.data.decode())
						except Exception as e:
							print('Error processing qr code from ', who_str, ':\n', e)

				##Display message			
				if (who.id == 1197270181):
					print(update)
					if (msg == '/used'):
						client.send_message('MrJuicyBacon5', str(used_strings))
				
				##Send message if code(s) found
				if codes_found:
					
					used_strings_len_local = 0
					for val in used_strings:
						used_strings_len_local += len(used_strings[val])
	
					global used_strings_len
					duplicates = codes_found - (used_strings_len_local - used_strings_len)
					used_strings_len = used_strings_len_local
					
					message = 'Found {0} code(s)'.format(codes_found)
					if duplicates:
						if duplicates == 1:
							message += ', one of which is duplicate'
						else:
							message += ', {0} of which are duplicates'.format(str(duplicates))
					message += ' from {0}; message_id:{1}.'.format(who_str, update.message.id)
					
					print(message)
					if (duplicates != codes_found):
						client.send_message('MrJuicyBacon5', message)
					
			except Exception as e:
				print('Exception in main block: ' + str(e))

	#$Catch System messages
	elif isinstance(update, UpdateShortMessage) and update.user_id == 777000 or isinstance(update.message, MessageService):
		print(update)

selected_phone = eval('config.' + config.user_default + '_phone')
username = config.user_default
print('Using default username:')
print(username + ' ' + selected_phone)

client = TelegramClient('session_' + username, eval('config.' + username + '_api_id'), eval('config.' + username + '_api_hash'), update_workers=8)
client.connect()

if not client.is_user_authorized():
	print('User not authorized, exiting')
	quit()

used_strings = {'first_bot': ['string1', 'string2', 'string3']}
used_strings_len = 0
for val in used_strings:
	used_strings_len += len(used_strings[val])
used_telegraph_urls = []

exception_channels = [1317498348, 1160477738, 1341931524, 1094942847, 1152120532]
qr_channels = [1197270181, 1322662337, 1256068013, 1374835519]
antibot_channels = [1197270181, 1322662337, 1332912397]

first_input_entity = client.get_input_entity('first_bot')
second_input_entity = client.get_input_entity('second_bot')
third_input_entity = client.get_input_entity('third_bot')
fourth_input_entity = client.get_input_entity('fourth_bot')
fifth_input_entity = client.get_input_entity('fifth_bot')
sixth_input_entity = client.get_input_entity('sixth_bot')

main_regex = '(\w{0,7}_bot)\s{0,3}(?:&|\?)\s{0,3}start\s{0,3}=\s{0,3}(.{20,28})'

client.add_event_handler(ProcessRawUpdate, events.Raw)

##Get user name
name = get_display_name(client.get_me())
print('Current user:' + name)

##Infinite loop
try:
	while True:
		dialogs = client.get_dialogs()
		sleep(60)
		
except KeyboardInterrupt:
	print('Stopped from keyboard')
except Exception as e:
	print('Exception occured: ' + str(e))
finally:
	print('Disconnecting')
	client.disconnect()