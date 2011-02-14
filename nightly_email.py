#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, platform, smtplib
from email.mime.text import MIMEText

host = platform.node().split('.')[0]

if host == 'winxp': me = 'rawlins@sci.utah.edu'
else: me = 'scirun-tester@sci.utah.edu'
os.chdir("C:/FEBio/Testing")
fp = open("nightly_compare.txt", 'r')
msg = MIMEText(fp.read())
fp.close()
msg['Subject'] = 'Cron Nightly test: ' + host
you = 'febio-test@sci.utah.edu'
msg['From'] = me
msg['To'] = you
s = smtplib.SMTP('mail.sci.utah.edu')
s.sendmail(me, [you], msg.as_string())
s.quit()

