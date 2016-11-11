set compare=C:\Testing\Logs\%1_Logs\nightly_compare.txt
cd C:\Testing\code
nightly.py %* > %compare%
