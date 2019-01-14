import numpy as np
from os import listdir
from os.path import isfile, join
import datetime


def readCSVFile(path):
	file = open(path, 'r').read().split('\n')
	res = []
	for line in file:
		if(len(line) >0):
			res.append(line)
	return res;

def writeCSVFile(path, list):
	file = open(path, 'w')
	for i in list:
		line = str(i)
		print(line)
		file.write(line)
		file.write('\n')
	file.close()
	return 0;


def readCustomDic_index(path):
	file = open(path, 'r').read().split('\n')
	res = {}
	for line in file[:-1]:
		temp = line.split(';')
		user = int(temp[0]) 
		sub_dic={}
		for i in temp[1:-1]:
			key=i.split("-->")[0]
			value=i.split("-->")[1]
			sub_dic[key] = value
		res[user]=sub_dic
	return res;

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



