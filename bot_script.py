import botometer
from twython import Twython, TwythonRateLimitError
import sys
import time
from credentials import *


def writeCSVFile_index(path, dic):
	file = open(path, 'w')
	for user in dic.keys():
		line = str(user) + ';' 
		sub_dic = dic[user]
		for key in sub_dic:
			line = line + str(key) + "-->" + str(sub_dic[key]) + ";"

		file.write(line)
		file.write('\n')

	file.close()
	return 0;


path = sys.argv[1]

twitter_app_auth = {
    'consumer_key': twitter_auth['consumer_key'],
    'consumer_secret': twitter_auth['consumer_secret'],
    'access_token': twitter_auth['access_token'],
    'access_token_secret': twitter_auth['access_token_secret']
  }
mashape_key = twitter_auth['mashape_key'] 

bom = botometer.Botometer(mashape_key=mashape_key, **twitter_app_auth)

accounts_to_query = [int(i) for i in open(path)]
accounts_to_query = sorted(accounts_to_query)
batch_size = 1000
batch_number = int(len(accounts_to_query)*1.0/batch_size)

bot_scores={}
start=time.time()
print('Start querying botometer API')
for b in range(batch_number+1):
	print('Querying batch n ', b+1, ' on ', batch_number+1)
	iterator = bom.check_accounts_in(accounts_to_query[batch_size*b:batch_size*(b+1)])
	count=0
	for i in iterator:
		count+=1
		print(count)
		try:
			bot_scores[i[0]]=i[1]['categories']
		except Exception as e: 
			print(e)
			pass;

print('Finished querying botometer API, took ', time.time()-start, ' seconds')
print('Writing results in csv file')
writeCSVFile_index('botometer_scores_' + str(start) + '.csv',bot_scores)
print('Results available in csv file botometer_scores_' + str(start) + '.csv')

		

