#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, platform, smtplib, sys
from email.mime.text import MIMEText

host = platform.node().split('.')[0]

if host == 'rawlins-PC': me = 'rawlins@sci.utah.edu'
else: me = 'scirun-tester@sci.utah.edu'
os.chdir("C:/Testing/" + sys.argv[1] + "_Logs")
fp = open("nightly_compare.txt", 'r')
msg = MIMEText(fp.read())
fp.close()
msg['Subject'] = 'Cron ' + sys.argv[1] + ' test: ' + host
you = 'febio-test@sci.utah.edu'
#you = 'rawlins@sci.utah.edu'
msg['From'] = me
msg['To'] = you
s = smtplib.SMTP('mail.sci.utah.edu')
s.sendmail(me, [you], msg.as_string())
s.quit()

