@echo off  
schtasks /create /tn "HotspotStart" /tr "\"C:\Users\elmes\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\startup-hotspot.bat\"" /sc onstart /RL HIGHEST /f
