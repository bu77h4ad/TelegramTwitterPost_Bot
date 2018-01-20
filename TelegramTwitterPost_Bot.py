import requests
import time
import json
from bs4 import BeautifulSoup
import APItelegram
import pprint
import configparser

#f = open ('TelegramTwitterPost_Bot.ini','r')
#configure = json.load(f)
#f.close

cfg = configparser.ConfigParser()

cfg.read('TelegramTwitterPost_Bot.ini')
last_post = cfg.get('Twitter', 'last_post').split(' ')
account = cfg.get('Twitter', 'account').split(' ')
chat_id = cfg.get ('Telegram','chat_id')

# Установка токена для бота в телеграм
bot = APItelegram.telegram (cfg.get('Telegram', 'token_bot'))
pprint.pprint(bot.getMe())
print ("Бот запущен ...")

while True:
	
	# Проверка всех новых твитов по очереди
	for x in range(0,len( account )):
		time.sleep(1)
		try:
			r = requests.get('https://twitter.com/' + account[x] )			
		except:
			print ('Ошибка при подключении : ', account[x] )
			time.sleep(3)
			continue
		soup = BeautifulSoup(r.text,'lxml')

		# Ищет в посте 
		try:
			post = soup.findAll('li', attrs={"class" : "js-stream-item stream-item stream-item "})[0] 
			data_item_id = post.find().get('data-item-id')
		except:
			print("Ошибка при поиске поста в ",  account[x])
			continue
		#print ('data_item_id',data_item_id)
		if len (last_post )-1 < x: 
			last_post.append('xxx') 
			
		if data_item_id ==  last_post[x]  : 
			continue
		else:
			last_post[x] = data_item_id
		#print (post.find('span', attrs = {"class" : "js-pinned-text"}), data_item_id )

		# Автор твита и т п
		header = post.find('strong', attrs = {"class" : "fullname show-popup-with-id u-textTruncate "}) 

		# Текст твита
		content = post.find('div', attrs = {"class" : "js-tweet-text-container"})

		try:
			a = post.findAll('a' )[-1]
			aHref = a.get('href')
			index = str(a).find('twitter-hashtag pretty-link js-nav')
			#print ('index',index)
			if index == -1:
				content.findAll('a')[-1].decompose()
			else:
				aHref = ' '
		#attrs={'target' : '_blank'} twitter-hashtag pretty-link js-nav
		except:	
			aHref = ' '
		if aHref[0] == '/': 
			aHref = 'https://twitter.com' + aHref
		else:
			aHref = ' '+ aHref
		content = content.text.strip()
		#print(post.text)
		print ("\nНайден новый пост: \n",content, aHref )
		bot.sendMessage(chat_id = chat_id, text = header.text +'\n\n'+content + '\n'+ aHref)
	string = ''		
	for i in range (0,len(last_post)):
		string = string + ' ' + last_post[i]

	cfg.set('Twitter', 'last_post', string)
	with open('TelegramTwitterPost_Bot.ini', 'w') as configfile:
		cfg.write(configfile)
	

