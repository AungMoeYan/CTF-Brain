\# Linux Enumeration



Linux enumeration is the process of gathering information about a Linux target after obtaining access.



\## System Information



Check the kernel:



uname -a



Check the operating system:



cat /etc/os-release



Check the current user:



id



Check the hostname:



hostname



\## Users



List users:



cat /etc/passwd



Check users with login shells:



cat /etc/passwd | grep -E "/bin/bash|/bin/sh"



\## SUID Enumeration



Find SUID binaries:



find / -perm -4000 -type f 2>/dev/null



Alternative:



find / -perm -u=s -type f 2>/dev/null



After finding SUID binaries, compare them against known privilege escalation techniques.



GTFOBins can be used to determine whether a binary can execute commands or access files in a privileged context.



\## Scheduled Tasks



Check cron configuration:



cat /etc/crontab



Check cron directories:



ls -la /etc/cron.\*



\## Network Information



Show interfaces:



ip addr



Show routes:



ip route



Show listening services:



ss -tulpn



\## Processes



List processes:



ps aux



Look for interesting processes:



ps aux | grep -i root

