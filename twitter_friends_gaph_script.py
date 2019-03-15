import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,json,re,datetime,sys,http.cookiejar
from pyquery import PyQuery
from operator import itemgetter
from ioHELPER import *
import time
import sys

batch_number=int(sys.argv[1])
users_to_query = sys.argv[2]


batch_size=5000
thr_friends=3000

cookieJar = http.cookiejar.CookieJar()
today=datetime.datetime.now()


date=today.strftime('%d_%m_%Y__%H_%M')

index=open(users_to_query).read().split('\n')[:-1]
toquery=sorted([(int(i.split(';')[0]),i.split(';')[1],int(i.split(';')[2]),int(i.split(';')[3])) for i in index],key=itemgetter(0))

toquery_sn = [i[1] for i in toquery]
toquery_sn=toquery_sn[(batch_number-1)*batch_size:batch_number*batch_size]

mapper = dict(zip([i[1] for i in toquery],[i[0] for i in toquery]))
API=[]
INACCESSIBLE=[]
start =time.time()
count=0
for user in toquery_sn:
	keepgoing=True
	accessible=True
	count+=1
	print("at user number ", count)
	ufriends=[]
	oufriends=[]
	url='https://mobile.twitter.com/'+user+'/following'

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

	try :

		response = opener.open(url)   
		jsonResponse = response.read()  
		res=jsonResponse.decode().split('\n')
		try :
			nfriends=[int(''.join(i.split('"count">')[1].split('</span>')[0].split('.'))) for i in res if '<td class="info"><span class="count">' in i ][0]
		except Exception as e: ##protected or suspended user
			print('Error occcured: ', e)
			accessible=False
			INACCESSIBLE.append(toquery[count-1])
		
		if(accessible):
			if(nfriends>=thr_friends):
				API.append(toquery[count-1])
				keepgoing = False
				cnext=[]
			else:
				ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
				cnext=[i.split('cursor=')[1].split('"')[0] for i in res if user+'/following?cursor=' in i]
				print('already got ', len(ufriends), ' friends')

	except Exception as e:
	
		if(accessible):
			if(e.code==404):
				keepgoing=False
				
		
	if (len(cnext)>0 and keepgoing and accessible):
		cursor=cnext[0]


		while True:

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

	if(keepgoing):

		with open('./brexit_friends/friends_collected_'+str(date)+'_'+str(batch_number)+'.csv', 'a') as fr:
			line = user
			if(len(ufriends) > 0):
				line += ';'
				line += ';'.join(ufriends)
			else:
				line += ';'
			fr.write(line)
			fr.write('\n')
		fr.close()

		oufriends=[str(mapper[i]) for i in ufriends if i in mapper]
		with open('./brexit_friends/friends_collected_'+str(date)+'_'+str(batch_number)+'_IDS.csv', 'a') as fri:
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
print('remains to query ', len(API), ' via the API')
writeCSVFile([i[0] for i in API],'toquery_viaAPI.csv')
print('inaccesible because suspended or protected ', len(INACCESSIBLE))
writeCSVile([i[0] for i in INACCESSIBLE],'impossible_toquery_viaAPI.csv')




