# CONNECT
```
CONNECT
accept-version:<x.y>
host:asd.qwe.org
[login:]
[passcode:]
[heart-beat:<can>,<want>]

^@
```

# CONNECTED
```
CONNECTED
version:<x.y>
[heart-beat:]
[session:]
[server:name["/"version] *(comment)]


^@
```

# SEND
```
SEND
destination:/queue/a
content-type:text/plain

hello queue a
^@
```