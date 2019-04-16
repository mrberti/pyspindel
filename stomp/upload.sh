#!rshell -f
# Connect to the serial com port
connect serial com9
# Upload the main files
cp main.py /pyboard/main.py
cp wemos.py /pyboard/wemos.py
# Upload the package
mkdir /pyboard/lib
mkdir /pyboard/lib/stomp
rsync -v stomp/ /pyboard/lib/stomp/
# Go into the REPL
repl