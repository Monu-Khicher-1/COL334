# COL334
Computer Networks
## Wireshark 
This is an open source network packet analyser Software tool. Mainly used to troubleshoot or debug network problems.
### Installation Steps

Run following commands in ubuntu terminal:

*  `sudo add-apt-repository ppa:wireshark-dev/stable`
*  `sudo apt update`
*  `sudo apt install wireshark`

To run wireshark after installation run command `sudo wireshark`.

Run following commands to install iperf:
 
 * `sudo apt install iperf3`
 
## ns3
Tool for network setup and running network layer algorithms on local system.

### Installation steps

Run following commands in ubuntu terminal:

* `$ suda apt update`
* `$ sudo apt upgrade`
* `$ sudo apt install g++ python3 python3-dev pkg-config sqlite3 cmake python3-setuptools git qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools gir1.2-goocanvas-2.0 python3-gi python3-gi-cairo python3-pygraphviz gir1.2-gtk-3.0 ipython3 openmpi-bin openmpi-common openmpi-doc libopenmpi-dev autoconf cvs bzr unrar gsl-bin libgsl-dev libgslcblas0 wireshark tcpdump sqlite sqlite3 libsqlite3-dev  libxml2 libxml2-dev libc6-dev libc6-dev-i386 libclang-dev llvm-dev automake python3-pip libxml2 libxml2-dev libboost-all-dev`

Now download the ns3 from website https://www.nsnam.org/releases/ns-3-29/download/ . A file `ns-allinone-3.29.tar.bz2` and run following commands:
* `$ tar jxvf ns-allinone-3.36.1.tar.bz2 `
* `$ cd ns-allinone-3.36.1/ `
* `$ ./waf --run hello-simulator`

If last command runs successfully then ns3 is installed.

Now you can run your program files by following commands:

* For c++ file : `$ ./waf --run scratch/filename`
* For python file : `$ ./waf --pyrun scratch/filename`

### 


## Course Material
* Course website: https://www.cse.iitd.ac.in/~abhijnan/computer-networks-2021.html
* Book: 1. Computer Networks: A Systems Approach [https://book.systemsapproach.org/]


