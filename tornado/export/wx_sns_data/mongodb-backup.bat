mongodump.exe -h 192.168.187.4:37017 -d wx_sns_data -o d:\MongoDB\backup

mongorestore.exe /h 127.0.0.1 /d wx_sns_data /dir d:\MongoDB\backup\wx_sns_data