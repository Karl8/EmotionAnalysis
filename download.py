#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import urllib,urllib2
import os  
      
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
                os.mkdir("./dataset/" + f_name[0])
            except:
                print "dir exist"
            cnt = 0
            for lines in f.readlines():
                cnt += 1
                line = lines.split(",");
                imgurl = line[1]
                download_name = "./dataset/" + f_name[0] + "/" + str(cnt) + "_" + line[2] + "_" + line[3].strip() + ".jpg"
                print download_name
                try:
                    urllib.urlretrieve(imgurl, download_name)
                except:
                    print "downloading img error"
        return
        print "fuck!!"
        #f = open()

file_name("./dataset/")


