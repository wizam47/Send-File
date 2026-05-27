@echo off
cd /d "%~dp0"
python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); ip=s.getsockname()[0]; s.close(); import webbrowser; webbrowser.open('http://'+ip+':5000')" 
python app.py