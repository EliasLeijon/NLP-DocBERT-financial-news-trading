#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# Using readlines()
file1 = open('rawData/uniqNeutralNews.csv', 'r')
Lines = file1.readlines()

f = open("processed_data.txt", "a")

count = 0
# Strips the newline character
for line in Lines:
    count += 1
    s = line.strip()

    # s = 'Axolot Solutions Holding AB: Axolot Solutions signs an agreement with Borås Energi och Miljö:	 NewsItem  NewsEnvelope  TransmissionId 20221108BIT02640 /TransmissionId  DateAndTime 20221108T110241+0100 /DateAndTime  SentFrom  Party FormalName=Axolot Solutions Holding AB/  /SentFrom  /NewsEnvelope  ContentItem  MimeType FormalName=text/vndMillistream/  DataContent  head  hedline  hl1 Axolot Solutions Holding AB Axolot Solutions signs an agreement with Borås Energi och Miljö /hl1  /hedline  distributor Cision /distributor  pubdata ex-ref=https//newscisioncom/axolot-solutions-holding-ab/r/axolot-solutions-signs-an-agreement-with-boras-energi-och-miljoc3663264/  abstract  p Axolot Solutions has signed a rental agreement with Borås Energi och Miljö The customer will rent a container based AxoPur[®] equipment to clean their washing water /p  /abstract  /head  body  p The startup is expected to take place around year end Initially it will be washing water that will be cleaned but going forward other waters such as contaminated leachate could come in question The unit to be rented is the first out of Axolot&aposs upgraded mobile standard system for flows between 1 and 15 m[3] /h /p  p &quotThe unit in Borås is the first one out of what we think might result in a number of container-based standard AxoPur systems and as such it is an important reference case for Axolot We believe that the market for cost efficient and mobile water purification systems handling a wide range of contaminants is big and growing Additionally we believe that our rental concept in itself can become an attractive business model for many of our potential customers&quot says Lennart Holm President and CEO of Axolot Solutions /p  /body  footer  hl2 For further information please contact /hl2  p Lennart Holm President and CEO Axolot Solutions Holding AB tel +46 70 630 85 62 mail  virtloc lennartholm@axolotsolutionscom  /virtloc  br/    /p  /footer  CompanyInfo  hl2 About Axolot Solutions /hl2  p Axolot Solutions Holding AB is a Swedish environmental technology company providing systems for industrial water purification The company offers a holistic solution based upon a proprietary technology Axolot&aposs water purification concept is cost efficient and enables a high degree of purification as well as recirculation of the water This leads to a reduced environmental footprint Axolot Solutions also has business activities in Norway and Finland with affiliated companies in each of the countries More information about the Company and its business activities can be found at wwwaxolotsolutionscom /p  p Axolot Solutions Holding AB is based in Helsingborg Sweden and its shares (ticker Axolot) are listed at Nasdaq First North Growth Market Stockholm since November 21 2018 FNCA Sweden AB is the Certified Adviser of Axolot Solutions FNCA Sweden AB can be reached at  virtloc info@fncase /virtloc  /p  /CompanyInfo  /DataContent  /ContentItem  ContentItem Href=https//newscisioncom/axolot-solutions-holding-ab/r/axolot-solutions-signs-an-agreement-with-boras-energi-och-miljoc3663264  MimeType FormalName=text/html/  /ContentItem  ContentItem Href=https//mbcisioncom/Main/17479/3663264/1655306pdf  MimeType FormalName=application/pdf/  /ContentItem  /NewsItem '

    result = re.findall('.*/p ', s)[0][:-1]
    result = re.sub('\/SentFrom.*?hl1', '', result)
    result = re.sub('NewsItem.*?FormalName=', '', result)
    result = re.sub('\/hl1.*?(abstract|body)', '', result)
    result = re.sub('( \/)\w*', '', result)
    result = re.sub('\w*(\/ )', '', result)
    # new word is not only divided by ' ' as we want but caught by '/' etc.
    result = re.sub('href\S*', '', result)
    # new word is not only divided by ' ' as we want but caught by '/' etc.
    result = re.sub('http\S*', '', result)
    # new word is not only divided by ' ' as we want but caught by '/' etc.
    result = re.sub('\S*@\S*', '', result)
    result = re.sub('\S*&\S*', '', result)
    result = re.sub('\S*=\S*', '', result)
    result = re.sub('\S*www\S*', '', result)
    result = re.sub(' p ', '. ', result)

    # utf-8 encoding verkar inte fungera som väntat, åäö är fuckat
    f.write(result + "\n")

    print("Line{}: {}".format(count, result))
f.close()
