# audit.py - engagement logging

Simple tool designed to help keeping tracks of security audits / engagements. Logs activity to a dedicated folder for each audit.

It currently supports:
- shell output logging
- periodic screenshots
- automated git versioning of the audit folder

## Setup

Quick install:

```
./install.sh
```

Dependencies:

* python2
* git
* mss (pip)
* termcolor (pip)

## Usage

Edit **config.py** to suit your needs.

Create audit project:
```
$ audit.py init audit1

[+] Created audit project in /root/audits/audit1
```

Start/Resume logging:
```
$ audit.py start audit1 

[!] Already opened shells will not be logged
Logging to /root/audits/audit1
Stop with : audit.py stop audit1
```

Stop/Pause logging:
```
$ audit.py stop audit1
[+] Audit stopped.
```

All audit logs are saved in the main audit folder defined in **config.py**, in a subdirectory "audit1".

