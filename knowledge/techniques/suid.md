\# Linux SUID Privilege Escalation



SUID binaries execute with the privileges of the file owner.



To enumerate SUID binaries on a Linux target:



find / -perm -4000 -type f 2>/dev/null



Another useful command is:



find / -perm -u=s -type f 2>/dev/null



After finding a SUID binary, identify whether it is a known exploitable binary.



GTFOBins is useful for checking whether a binary can be abused for privilege escalation.



For example, if a vulnerable SUID binary allows command execution, an attacker may be able to execute commands with the privileges of the binary owner.

