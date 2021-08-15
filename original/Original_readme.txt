RAC Based Authentication and Authorization for FTPD
===================================================

As distributed with TK4- Update 07 the ftp daemon doesn't do any authentication
or authorization checking on incoming connections. Each ftp session is granted
full access to all datasets, which is how Jason Winter originally designed it.

While this is very convenient for the typical "single user at home" TK4- system
it is a major security risk for multi user systems being fully exposed to the
internet.

To be able to run the ftp daemon on internet accessible multi user systems at a
reasonable risk, the most critical security weaknesses of Jason's original ftpd
implementation have been hardened through a minimalistic integration into the
MVS Resource Access Control (RAC) framework. To prevent unencrypted passwords
from flowing across the internet it is recommended to use this RAC enhanced
version of the ftp daemon together with a tunneling setup enforcing encryption
on all incoming control connections. The resulting security level is then
roughly comparable to using FTPS with encrypted control and clear text data
paths on *i*x systems, which may well be regarded as conforming to the TCSEC C2
level, if an appropriately configured security package (like IBM's RACF(tm) or
its surrogate RAKF) is active on the MVS system operating the ftp daemon.
Providing an encrypted data path, however, is not within the scope of this
enhancement.



Packaging
+++++++++

This archive contains the following files and folders:

README.txt     -- This file.

ftpd_rac.xmi   -- An XMITted PDS containing six members, each of which in turn
                  being an XMITted PDS:

       ASM     -- Assembler source of the RAC interface modules.
       CNTL    -- JCL to build the FTPD and the FTPDXCTL modules.
       INCLUDE -- C header library holding the RAC enhanced mvsdirs.h.
       LOAD    -- loadlib containing ready to use FTPD and FTPDXCTL modules.
       PROC    -- JCL procedure to execute the FTPD started task.
       SRC     -- C source library holding the RAC enhanced ftpd.c.

ftpd_rac.patch            \ The RAC enhanced version in folder rac can be
ftpd_rac_logout_0C4.patch / created by applying these two patches in sequence
                            to the original version in folder std.

Folder std:
-----------
ftpd.c    \ Source of the ftp daemon without RAC enhancements. This is the TK4-
mvsdirs.h / adaption of Jason's original version.

Folder rac:
-----------
ftpd.c    \ Source of the ..
mvsdirs.h /                 .. RAC enhanced ftp daemon.

Folders rac and std, and the two patch files are provided for documentation
purposes only, to be able to trace the changes between the standard and the
RAC enhanced version of the ftp daemon. Depending on the codepage in use and
the system type (Windows, Linux, Unix) the source versions in folder rac might
differ slightly from downloads of the versions in the INCLUDE and SRC libraries
from ftpd_rac.xmi. If this is the case, the versions from ftpd_rac.xmi are to be
considered the original versions.



Installation
++++++++++++

To install the RAC enhanced ftp daemon on a standard TK4- or comparable MVS 3.8j
system simply receive the LOAD PDS into SYS2.LINKLIB and the PROC PDS into
SYS2.PROCLIB. The ASM, CNTL, INCLUDE and SRC datasets are required only if the
the FTPD or FTPDXCTL module need to be rebuilt due to source changes.



RAC Configuration
+++++++++++++++++

o Create a user named FTPD in group USER. This user must have access to SVC 244
  allowing it to run authorized at any time. On TK4- this is accomplished by
  granting READ access to resource SVC244 in the FACILITY class. With this very
  critical permission this user has a high potential to put the whole system at
  risk. It should by all means be ensured that _no one_ ever can use this user
  to logon or to run batch jobs. So, choose a complex password, you will not
  need to remember it, as it will nowhere be used explicitly. In particular,
  this user does not need to be and thus should not be a TSO user. It must, when
  running unauthorized, be able to read the VTOC of all DASDs holding datasets
  and to list all catalogs containing datasets to be served by the ftp daemon.

o Create a resource named FTPAUTH in the FACILITY class and give all users to
  be authorized to log in to the ftp daemon READ access to this resource. Users
  not having READ access to the FTPAUTH resource will not be allowed to log in
  even if they provide correct credentials.



MVS Configuration and Operation
+++++++++++++++++++++++++++++++

o Create SYS1.PARMLIB(VATLSTFF) using the same format as VATLST00. This list
  must contain the DASD volumes holding datasets to be served by the ftp daemon.
  Datasets on volumes not being in this list can neither be read nor written.
  Keep this list as small as possible in the interest of short root directory
  rebuild times.

o Configure the parameters in SYS2.PROCLIB(FTPD) as described in the TCPIP TSO
  HELP member. Use a portnumber (SRVPORT parameter) above 1024 and set PASVADR
  to the comma separated IP address used by ftp clients to connect to. The SRVIP
  parameter should be set to any or to the same address used as PASVADR (dotted
  decimal format, however).

The ftp daemon can now be started and stopped from the MVS console using the
"S FTPD" and "P FTPD" commands, respectively. User HERC01 can also stop the
ftp daemon from a client session using the "quote term" client command. This
is hardcoded in the source; if another user is to be authorized for the term
command, change the AUTH_USER preprocessor variable accordingly and rebuild
the FTPD module.



Hercules Host Configuration
+++++++++++++++++++++++++++

The ftp daemon will not accept connections originating from interfaces it is
not listening to. That means only connections originating on the host running
the Hercules instance for MVS are possible. This is a security measure to
enforce using tunnels for external connections, given that the ftp daemon itself
isn't able to handle encrypted channels.

To allow external connections an SSLv3 tunnel should be opened, forwarding the
port ftp clients are connecting to to the port the ftp server is listening at.
To accomplish this the freely available socat tool is recommended. Simply have
the following command running in the backgroung on the Hercules host:

socat OPENSSL-LISTEN:<extport>,bind=<address>,reuseaddr,fork, \
                     cert=<certfile>,key=<keyfile>,verify=0,  \
                     nodelay,max-children=0,                  \
                     keepalive,keepcnt=0,keepintvl=900        \
      TCP4:<address>:<intport>,bind=<address>,nodelay,        \
                     keepalive,keepcnt=0,keepintvl=900        \

where:

<address>  is the IP address of a local network interface on the Hercules host.
           All ftp clients will have to connect to this address. It must be
           identical to the address used in the PASVADR configuration parameter
           of the FTPD procedure on MVS.

<extport>  The port ftp clients will connect to. It must be different from the
           SRVPORT configuration parameter of the FTPD procedure.

<intport>  The port to which the tunnel will forward connections coming in
           on <extport>. It must be identical to the SRVPORT configuration
           parameter of the FTPD procedure.

<certfile> Name of the file holding the SSL certificate of the Hercules host.

<keyfile>  Name of the file holding the key to access the certificate.



Usage
+++++

o The control connection (aka the "ftp session") must be made using an SSLv3
  tunnel to port <extport> at address <address> as configured in the tunnel
  on the Hercules host.

o Incoming connections must authenticate using the username and the password of
  a user having READ access to the FTPAUTH resource in the FACILITY class.

o The ftp client must use passive mode for all transfers.


Tunneling the Control Connection
--------------------------------

Tunneling the control connection through SSLv3 means to create a tunnel
"outside" the ftp protocol framework, through which a regular clear text
connection is made. In particular, this is _not_ ftps (which negotiates the
encryption as part of the ftp control session setup) and it is _not_ sftp
which basically tunnels an "ftp like" session through ssh and as such has
nothing to do at all with ftp.

Many (if not most) ftp clients don't support tunneling the control connection
as described above. In these cases it is necessary to explicitely create a
tunnel before starting the ftp client. There exist quite a few tools to create
an SSLv3 encrypted tunnel. One that works particularly well with FTPD is
"socat", which is installed (or is available as a ready to install package) on
most current Linux distributions. Windows and OS X versions can also be found
on the internet. Instead of trying to find an ftp client that does the tunneling
correctly it is recommended to install socat and use any regular clear text ftp
client over it.

Before connecting the first ftp client session issue the following socat
command on the client system:

socat TCP-LISTEN:<clientport>,bind=127.0.0.1,reuseaddr,fork,nodelay \
      OPENSSL:<address>:<extport>,nodelay,verify=0

where <clientport> is an arbitrary port on the client system to which the
ftp client will connect, <extport> and <address> are as configured above
on the Hercules host. Of course, DNS resolution is possible for <address>. 

Then the ftp session can be conducted as shown in the following example:

$ ftp -n 127.0.0.1 <clientport>
Connected to 127.0.0.1.
220 *** MVS38j FTP Daemon on TK4- ***
ftp> user juergen
331 Okay, waiting for password.
Password:
230 You are now logged in.
Remote system type is MVS.
ftp> cd /juergen.jcc.tcpip.src
250 CWD command successful
ftp> passive
Passive mode on.
ftp> ls
227 Entering Passive Mode (129,132,252,105,194,193)
150 Now opening data connection
total 00002
-r-xr-xr-x   1 user     group        1024 Mar 15  2015 FTPD-RAC
-r-xr-xr-x   1 user     group        1024 Mar 15  2015 FTPD-STD
226 Transfer complete!
ftp> quit
221 Bye!



Rebuilding from Source
++++++++++++++++++++++


FTPD
----

Much of the FTPD functionality is hardcoded in the source. So most probably it
will at times be necessary to modify the source as found in the ASM, SRC and
INCLUDE datasets of the XMIT distribution. To rebuild FTPD from source modify
job MAKEFTPD in the CNTL dataset to point to the location where the datasets
have been received to (replace JUERGEN.FTPD.RAC whith the HLQs used for receive)
and submit the job. A return code of zero is expected for all steps.


FTPDXCTL
--------

FTPDXCTL is a wrapper called from the FTPD procedure. Its only purpose is to
give up STC/STCGROUP in favour of FTPD/USER privileges before transfering
control to the ftp daemon. The only thing that might need change here is the
user (FTPD) and group (USER) the daemon is to run under in case FTPD/USER would
not match local requirements. The FTPDXCTL module can be rebuilt by adapting job
MAKEXCTL to match the locations used for receive and submitting the job.



----------
Juergen Winkelmann, 5/2/2016
winkelmann@id.ethz.ch
