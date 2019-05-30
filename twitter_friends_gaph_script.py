import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,json,re,datetime,sys,http.cookiejar
from pyquery import PyQuery
from operator import itemgetter
import time
import sys

### Set of homemade io read/write methods. File available at same root.
from ioHELPER import *

### This is the name of the csv file where users to be queried are stored
users_to_query = sys.argv[1]

### Each IP address will take care of a batch of size TBD by user
batch_number=int(sys.argv[2])
batch_size=int(sys.argv[3])

### Users with few friends are queried via the scraper. Users with lots of friends are queried via the API. 
### We recommend a threshold of 3,000.
thr_friends=int(sys.argv[4])

### Today's date
today=datetime.datetime.now()
date=today.strftime('%d_%m_%Y__%H_%M')

### CookieJar
cookieJar = http.cookiejar.CookieJar()

### Read file of users_ids, users screen_names to query, with info on their friends and follower counts.
### Transform it to a python list of tuples
index=open(users_to_query).read().split('\n')[:-1]
toquery=sorted([(int(i.split(';')[0]),i.split(';')[1],int(i.split(';')[2]),int(i.split(';')[3])) for i in index],key=itemgetter(0))

### Subselect screen_names for batch under scrutiny
toquery_sn = [i[1] for i in toquery]
toquery_sn=toquery_sn[(batch_number-1)*batch_size:batch_number*batch_size]

### Dicionnary to map screen_names -> users_ids
mapper = dict(zip([i[1] for i in toquery],[i[0] for i in toquery]))

### List to fill up with users to be queried via the API (friends count >  thr_friends)
API=[]

### List to fill up with users for which the query returned a exception.
### Either because private profile, or problem in connection. You want to re-query users in this list in a second round.
INACCESSIBLE=[]

### Start querying batch in a for loop
start =time.time()
count=0
for user in toquery_sn:
	keepgoing=True
	accessible=True
	count+=1
	print("at user number ", count)
	ufriends=[]
	oufriends=[]
	
	### Go via the mobile twitter site instead of twitter.com. This version returns cursors in Json response to 
	### iterate through pages of friends for a user.
	url='https://mobile.twitter.com/'+user+'/following'
	
	### Headers 
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
	headers = [
		('Host', "twitter.com"),
		('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
		('Accept', "application/json, text/javascript, */*; q=0.01"),
		('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
		('X-Requested-With', "XMLHttpRequest"),
		('Referer', url),
		('Connection', "keep-alive")
	]
	opener.addheaders = headers

	## Try querying first 40 friends screen_names
	try :

		response = opener.open(url)   
		jsonResponse = response.read()  
		res=jsonResponse.decode().split('\n')

		### Parse JSON code to uncover latest number of friends of that user
		try :
			nfriends=[int(''.join(i.split('"count">')[1].split('</span>')[0].split('.'))) for i in res if '<td class="info"><span class="count">' in i ][0]
		except Exception as e: ##protected or suspended user
			print('Error occcured: ', e)
			accessible=False
			INACCESSIBLE.append(toquery[count-1])
		
		if(accessible):
			
			### If this number of friends is above the thr, put this user in the API query queue
			if(nfriends>=thr_friends):
				API.append(toquery[count-1])
				keepgoing = False
				cnext=[]
				
			### Else parse JSON responde to get friends and find cursor to next page
			else:
				ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
				cnext=[i.split('cursor=')[1].split('"')[0] for i in res if user+'/following?cursor=' in i]
				print('already got ', len(ufriends), ' friends')

	except Exception as e:
	
		if(accessible):
			if(e.code==404):
				keepgoing=False
				
	
	### Keep iterating through pages as long as we find results
	if (len(cnext)>0 and keepgoing and accessible):
		cursor=cnext[0]

		### Identical to first query
		while True:
			
			### Update url with cursor to return results of new pages 
			url='https://mobile.twitter.com/'+user+'/following?cursor='+cursor
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
			headers = [
				('Host', "twitter.com"),
				('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
				('Accept', "application/json, text/javascript, */*; q=0.01"),
				('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
				('X-Requested-With', "XMLHttpRequest"),
				('Referer', url),
				('Connection', "keep-alive")
			]
			response = opener.open(url)   
			jsonResponse = response.read()  
			res=jsonResponse.decode().split('\n')
			ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
			cnext=[i.split('cursor=')[1].split('"')[0] for i in res if user+'/following?cursor=' in i]
			if (len(cnext)>0):
				cursor=cnext[0]
			else:
				break
			print('already got ', len(ufriends), ' friends')

			### Exited loop, write results in a file
	if(keepgoing):
		
		### Append a line to the output file with user u friends. First element in the line is the user u. 
		### Then all his friends.This file contains only screen_names.
		with open('./friends_collected_'+str(date)+'_'+str(batch_number)+'.csv', 'a') as fr:
			line = user
			if(len(ufriends) > 0):
				line += ';'
				line += ';'.join(ufriends)
			else:
				line += ';'
			fr.write(line)
			fr.write('\n')
		fr.close()

		### Subset of all the friends of user u which are in the mapper, hence in our subset of studied users.
		### Here the output is a file with users_ids, and only users in our dataset. 
		### Hence a subgraph of the friends graph

		oufriends=[str(mapper[i]) for i in ufriends if i in mapper]
		with open('./friends_collected_'+str(date)+'_'+str(batch_number)+'_IDS.csv', 'a') as fri:
			line = str(mapper[user])
			if(len(oufriends) > 0):
				line += ';'
				line += ';'.join(oufriends)
			else:
				line += ';'
			fri.write(line)
			fri.write('\n')
		fri.close()


print('Took ', time.time()-start)

### write files to query via API and Inaccessible users to double check
print('remains to query ', len(API), ' via the API')
writeCSVFile([i[0] for i in API],'toquery_viaAPI_'+str(date)+'_'+str(batch_number)+'.csv')
print('inaccesible because suspended or protected ', len(INACCESSIBLE))
writeCSVile([i[0] for i in INACCESSIBLE],'impossible_toquery_viaAPI_'+str(date)+'_'+str(batch_number)+'.csv')




