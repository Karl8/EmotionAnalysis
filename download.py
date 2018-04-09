#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import urllib,urllib2
import os  

d = dict()

d["amusement"] = 1
d["anger"] = 2
d["awe"] = 3
d["contentment"] = 4
d["disgust"] = 5
d["excitement"] = 6
d["fear"] = 7
d["sadness"] = 8

cnt = dict()

cnt[1] = 1
cnt[2] = 1
cnt[3] = 1
cnt[4] = 1
cnt[5] = 1
cnt[6] = 1
cnt[7] = 1
cnt[8] = 1


def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
        print(files) #当前路径下所有非目录子文件
        for ff in files:
            f_name = ff.split(".");
            if f_name[1] != "csv":
                continue
            print "file_name:", ff
            f = open("./dataset/" + ff, "r")
            try:
                os.mkdir("./dataset/" + "img")
            except:
                print "dir exist"
            haha = 0

            for lines in f.readlines():
                haha += 1
                line = lines.split(",");
                if (int(line[2]) != 1 and int(line[2]) != 0):
                    continue
                imgurl = line[1]
                download_name = "./dataset/" + "img" + "/" + str(d[line[0]]) + "_" + str(cnt[d[line[0]]]) + ".jpg"
                print download_name
                cnt[d[line[0]]] += 1
                if os.path.exists(download_name):
                    print "file_exist"
                    continue
                try:
                    print "downloading file", haha, "of", f_name[0]
                    urllib.urlretrieve(imgurl, download_name)
                except:
                    print "downloading img error"
        return
        print "fuck!!"
        #f = open()

file_name("./dataset/")


