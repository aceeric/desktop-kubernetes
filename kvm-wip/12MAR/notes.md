Successfully created a VM
ability to SSH in from the desktop
ability to yum install bind-utils
ability to then nslookup google.com

[root@cloneme ~]# ifconfig
enp1s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.122.88  netmask 255.255.255.0  broadcast 192.168.122.255
        inet6 fe80::5054:ff:fe46:c600  prefixlen 64  scopeid 0x20<link>
        ether 52:54:00:46:c6:00  txqueuelen 1000  (Ethernet)
        RX packets 32901  bytes 65351755 (62.3 MiB)
        RX errors 0  dropped 163  overruns 0  frame 0
        TX packets 19052  bytes 1291726 (1.2 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 2  bytes 78 (78.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2  bytes 78 (78.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
