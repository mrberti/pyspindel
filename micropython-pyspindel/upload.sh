#!rshell -f
# Connect to the serial com port
connect serial com9
# Upload the main files
cp main.py /pyboard/main.py
cp wemos.py /pyboard/wemos.py
# Upload the package
rsync pyspindel/ /pyboard/lib/pyspindel/
# cp pyspindel/__init__.py /pyboard/lib/pyspindel/__init__.py
# cp pyspindel/pyspindel.py /pyboard/lib/pyspindel/pyspindel.py 
# cp pyspindel/mpu6050.py /pyboard/lib/pyspindel/mpu6050.py
# cp pyspindel/filters.py /pyboard/lib/pyspindel/filters.py
# Go into the REPL
repl