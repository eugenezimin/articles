SSH (Secure Shell) is the backbone of remote system administration and secure remote access, serving millions of developers and system administrators daily. However, when SSH connections fail, the cryptographic nature of the protocol can make debugging challenging. The complex interplay between authentication mechanisms, encryption algorithms, and network layers often obscures the root cause of connection issues. This complexity is further compounded by the protocol's security-first design, where error messages are intentionally vague to prevent potential attackers from gathering system information. Whether we're dealing with key authentication failures, network connectivity issues, or configuration mismatches, understanding the underlying SSH architecture becomes critical for effective troubleshooting.
## Understanding SSH Connection Process

Before diving into debugging, it's important to understand how SSH establishes connections. The process follows these steps:

1. TCP connection establishment (Port 22 by default)
2. Protocol version exchange
3. Key exchange and server authentication
4. Client authentication
5. Session establishment

Detailed process is highlighted in another article: [Configuring SSH to Access Remote Server](https://dev.to/eugene-zimin/configuring-ssh-to-access-remote-server-2ljk) dedicated to overview this process in a deeper level.

Each step can fail for different reasons, producing various error messages. Understanding these steps helps pinpoint where issues occur.

## Common SSH Errors and Solutions

When working with SSH connections, we frequently encounter various error messages that might seem cryptic at first glance. While SSH's error reporting is intentionally terse for security reasons, each error message provides valuable clues about the underlying issue. Understanding these common errors and their potential solutions not only helps us resolve issues faster but also deepens our knowledge of SSH's security model and connection process. Many of these errors stem from incorrect configurations, permission issues, or network problems, and they often appear during system upgrades, after server migrations, or when setting up new environments. Let's explore the most frequent SSH connection issues and their systematic solutions.

### Connection Refused: Understanding Server Accessibility 

One of the most common SSH errors we encounter during daily operations looks deceptively simple:

```bash
ssh: connect to host example.com port 22: Connection refused
```

This error message indicates that our SSH server is completely unreachable, though the underlying cause requires careful investigation. Most frequently, we discover that the SSH daemon (`sshd`) has stopped running on the target server. This typically happens after system updates, configuration changes, or occasional service crashes. A quick check of the service status often reveals the problem:

```
$ sudo systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled)
     Active: inactive (dead) since Mon 2024-01-15 09:23:45 UTC
```

Pay attention that the server is shown as `inactive (dead)` and usually it should be started with the following command:

```
$ sudo systemctl start sshd
```

Network connectivity issues present another common culprit. Corporate or cloud provider firewalls might be blocking the default SSH port 22, requiring us to verify firewall rules. In cloud environments like AWS or GCP, this often means checking both the instance's security group and network ACLs:

```
$ sudo iptables -L | grep ssh
# No output indicates potential firewall blocking
```

Sometimes the issue stems from DNS resolution problems or incorrect IP addressing. We can validate basic network connectivity using standard networking tools:

```
$ ping example.com
ping: example.com: Name or service not known

$ telnet example.com 22
telnet: Unable to connect to remote host: Connection refused
```

If all these checks pass but the connection still fails, the server itself might be experiencing issues, possibly due to resource exhaustion or hardware problems. In such cases, server logs become our primary diagnostic tool:

```
$ sudo tail -f /var/log/syslog
Jan 26 10:15:32 server kernel: Out of memory: Kill process 1234 (sshd) score 28 or sacrifice child
```

### Permission Denied

One of the most frustrating SSH errors occurs during the authentication phase, presenting itself as a seemingly simple message:

```bash
Permission denied (publickey,password)
```

This deceptively brief message indicates an authentication failure, though its resolution often requires careful investigation. The error message's format actually provides our first clue - the terms "publickey" and "password" in parentheses tell us which authentication methods the server attempted before denying access.

When troubleshooting this error, we often find that the username doesn't match the remote system's records. For example, while connecting to an Ubuntu server, we might mistakenly use:

```
$ ssh admin@ubuntu-server
Permission denied (publickey,password)
```

When the correct username should be 'ubuntu':

```
$ ssh ubuntu@ubuntu-server
Welcome to Ubuntu 22.04.2 LTS...
```

Private key mismatches represent another common scenario. The SSH server maintains a strict relationship between private and public key pairs, and even a slight mismatch will trigger this error. We can investigate key-related issues by enabling verbose output:

```
$ ssh -v ubuntu@ubuntu-server
...
debug1: Trying private key: /home/user/.ssh/id_rsa
debug1: Trying private key: /home/user/.ssh/id_ed25519
debug1: No more authentication methods to try.
```

This verbose output shows SSH attempting to use each private key file it finds. The sequence shows that SSH couldn't successfully authenticate with any available key file. When you see 'No more authentication methods to try', it means SSH has exhausted all configured authentication methods (in this case, trying both RSA and ED25519 keys) without success.

A particularly tricky variant occurs when all credentials appear correct, but file permissions are preventing SSH from accepting the keys. SSH enforces strict permission requirements for security reasons. We commonly see this when copying key files between systems:

```
$ ls -la ~/.ssh/id_ed25519
-rw-rw-r-- 1 user user 464 Nov 26 10:15 /home/user/.ssh/id_ed25519

$ ssh ubuntu@ubuntu-server
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0664 for '/home/user/.ssh/id_ed25519' are too open.
```

The solution requires setting appropriate permissions:

```
$ chmod 600 ~/.ssh/id_ed25519
$ ssh ubuntu@ubuntu-server
Welcome to Ubuntu 22.04.2 LTS...
```

For those cases where the server has our public key but still denies access, examining the server's auth log often reveals the underlying issue:

```
$ sudo tail -f /var/log/auth.log
Nov 26 10:15:32 ubuntu-server sshd[12345]: Authentication refused: bad ownership or modes for directory /home/ubuntu/.ssh
```


### Host Key Verification Failed

During routine SSH operations, we occasionally encounter an alarming message that stops us in our tracks:

```bash
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @ WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED! @ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY! Someone could be eavesdropping on you right now (man-in-the-middle attack)! It is also possible that a host key has just been changed. The fingerprint for the ED25519 key sent by the remote host is SHA256:abcdef1234567890abcdef1234567890. Please contact your system administrator. Add correct host key in /home/user/.ssh/known_hosts to get rid of this message. Offending ECDSA key in /home/user/.ssh/known_hosts:3
```

This error, while alarming, serves as a critical security feature in SSH's trust model. When we first connect to a server, SSH stores its unique fingerprint in our `known_hosts` file. Any subsequent changes to this fingerprint trigger this warning, protecting us from potential security breaches.

In cloud environments, this error frequently occurs after server rebuilds. For instance, when working with AWS EC2 instances:

```shell
$ ssh ubuntu@ec2-12-34-56-78.compute-1.amazonaws.com
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

The instance might have been terminated and recreated, generating a new host key. We can verify this through AWS console or CLI:

```shell
$ aws ec2 describe-instance-history --instance-id i-1234567890abcdef0
{
    "InstanceHistoryEvents": [
        {
            "EventType": "instanceStop",
            "EventTime": "2024-01-25T10:00:00Z"
        }
    ]
}
```

For known legitimate changes, we can remove the old key:

```shell
$ ssh-keygen -R ec2-12-34-56-78.compute-1.amazonaws.com
# Host ec2-12-34-56-78.compute-1.amazonaws.com found: line 3
/home/user/.ssh/known_hosts updated.
```

However, when this error occurs unexpectedly, particularly with production servers, it warrants immediate investigation. We can examine the server's SSH fingerprint directly:

```shell
$ ssh-keyscan -t ed25519 hostname
# hostname:22 SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1
hostname ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...
```

For added security, we can compare this with the fingerprint provided by our infrastructure provider or system administrator:

```shell
$ ssh-keygen -lf <(ssh-keyscan -t ed25519 hostname 2>/dev/null)
256 SHA256:abcdef1234567890abcdef1234567890 hostname (ED25519)
```

In cases involving DNS changes, we might see this error when a domain name starts pointing to a different server. A quick DNS lookup can confirm such changes:

```shell
$ dig +short hostname
93.184.216.34  # Note if this IP has changed
```

### Slow Connections

While SSH generally provides very responsive connections, we occasionally encounter frustratingly slow sessions that impact us. These performance issues often manifest in various ways: delayed command responses, laggy terminal output, or prolonged initial connection times. 

One of the most common culprits involves DNS resolution delays. When establishing an SSH connection, the server attempts to resolve the client's hostname by default. In environments with misconfigured DNS servers or slow network responses, this resolution process can add significant delays:

```shell
$ time ssh server.example.com date 
Warning: Reverse DNS lookup failed 
Tue Nov 26 10:15:32 UTC 2024 
real 0m3.245s 
user 0m0.035s 
sys 0m0.012s
```

The output shows three timing measurements: 'real' indicates the actual elapsed wall-clock time (3.245 seconds), while 'user' and 'sys' show CPU time spent in user and kernel mode respectively. The large difference between real time (3.245s) and CPU time (0.047s total) indicates the connection is spending most of its time waiting for DNS resolution, not processing.

We can significantly improve connection times by disabling DNS lookups in the server configuration:

```shell
$ sudo nano /etc/ssh/sshd_config
# Add or modify the following line
UseDNS no

# Restart the SSH service to apply changes
$ sudo systemctl restart sshd

# Test the connection speed again
$ time ssh server.example.com date
Tue Nov 26 10:15:32 UTC 2024
real    0m0.532s
user    0m0.034s
sys     0m0.011s
```

For connections over high-latency networks or when transferring large amounts of data, enabling SSH compression can yield substantial performance improvements. SSH compression becomes particularly effective when working with text-heavy sessions or transferring compressible data:

```shell
$ cat ~/.ssh/config
# Global SSH client configuration
Host *
    # Enable compression for all connections
    Compression yes
    # Use compression level 6 for optimal balance
    CompressionLevel 6
```

Perhaps one of the most powerful optimizations involves SSH connection multiplexing. Instead of establishing new TCP connections for each SSH session, multiplexing reuses an existing connection, dramatically reducing connection overhead. This becomes especially valuable when working with remote Git repositories or running multiple SSH sessions to the same server:

```shell
$ cat ~/.ssh/config
Host *
    # Enable automatic multiplexing
    ControlMaster auto
    # Define the control socket location
    ControlPath ~/.ssh/control/%C
    # Keep the master connection alive for an hour
    ControlPersist 1h
    # Optional: Configure keepalive to prevent timeouts
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

We can verify multiplexing is working by examining the control socket:

```shell
$ ls -la ~/.ssh/control/
total 0
drwx------ 2 user user 100 Nov 26 10:15 .
drwx------ 8 user user 160 Nov 26 10:15 ..
srw------- 1 user user   0 Nov 26 10:15 example.com-22-user
```

The `srw` at the start of the last line indicates this is a socket file (`s`) with read-write permissions (`rw`). The size showing as 0 is normal for socket files. The filename `example.com-22-user` follows the format hostname-port-username, indicating an active multiplexed connection for this specific combination.

The presence of the socket file indicates an active multiplexed connection. Subsequent SSH commands to the same host will reuse this connection, resulting in nearly instantaneous session establishment:

```shell
$ time ssh server.example.com date
Tue Nov 26 10:15:32 UTC 2024
real    0m0.087s
user    0m0.012s
sys     0m0.008s
```

For production environments where consistent performance is critical, we might also consider adjusting `TCPkeepalive` settings to prevent connection drops over problematic networks:

```shell
Host production-*
    # More aggressive keepalive for production servers
    TCPKeepAlive yes
    ServerAliveInterval 30
    ServerAliveCountMax 6
```

### Resolving SSH Key-Related Issues

SSH key problems often emerge as some of the most perplexing authentication challenges. Let's explore two critical categories of key-related issues that frequently impact SSH connections.

One of the most common SSH key errors presents itself with an alarming warning message:

```shell
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
Permissions 0644 for '/home/user/.ssh/id_rsa' are too open. It is required that your private key files are NOT accessible by others. 
This private key will be ignored.`
```

This error reflects SSH's strict security requirements for private key files. Common scenarios leading to this issue include copying keys from another system, extracting them from backups, or creating them with incorrect default permissions. Let's examine a typical scenario:

```shell
$ ls -la ~/.ssh/id_rsa
-rw-rw-r-- 1 user user 1876 Nov 26 10:15 /home/user/.ssh/id_rsa
```

The permissions shown above (664) allow group members to read the private key, creating a security vulnerability. We can resolve this by applying proper permissions:

```shell
# Secure the private key file
$ chmod 600 ~/.ssh/id_rsa
$ ls -la ~/.ssh/id_rsa
-rw------- 1 user user 1876 Nov 26 10:15 /home/user/.ssh/id_rsa

# Secure the SSH directory itself
$ chmod 700 ~/.ssh
$ ls -la ~ | grep .ssh
drwx------ 2 user user 4096 Nov 26 10:15 .ssh
```

Another subtle but frustrating issue occurs when SSH refuses to read seemingly valid key files:

```shell
Load key "/home/user/.ssh/id_rsa": invalid format
```

This error often surfaces after migrating keys between different SSH implementations or when working with keys generated by third-party tools. Let's investigate a problematic key:

```shell
$ ssh-keygen -l -f ~/.ssh/id_rsa
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: INVALID KEY FILE FORMAT DETECTED!           @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

The `-l` flag attempts to show the key's fingerprint and bit length. This error indicates the key file exists but isn't in a format SSH can parse. This often happens when the key file has been corrupted during transfer or when it's been modified by a text editor that changed line endings or character encoding.

The error might occur because the key is in a modern OpenSSH format while connecting to an older server, or vice versa. We can examine the key's content (being careful not to expose private key material):

```shell
$ head -n 1 ~/.ssh/id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
```

If we see a different header format or unexpected content, we might need to convert the key to a compatible format. The PEM format offers the widest compatibility:

```shell
# Backup the original key first
$ cp ~/.ssh/id_rsa ~/.ssh/id_rsa.backup

# Convert the key to PEM format
$ ssh-keygen -p -f ~/.ssh/id_rsa -m PEM
Key has comment 'user@hostname'
Enter new passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved with the new passphrase.

# Verify the key format
$ head -n 1 ~/.ssh/id_rsa
-----BEGIN RSA PRIVATE KEY-----
```

For keys that appear completely unreadable, we might need to check their encoding:

```shell
$ file ~/.ssh/id_rsa
/home/user/.ssh/id_rsa: PEM RSA private key
```

Sometimes, keys might become corrupted during transfer, especially when copying between Windows and Unix systems. In such cases, checking for hidden characters or incorrect line endings can help:

```shell
$ dos2unix ~/.ssh/id_rsa
dos2unix: converting file /home/user/.ssh/id_rsa to Unix format...
```

## Advanced Debugging Techniques

When standard troubleshooting steps fall short, we often need to delve deeper into SSH's internal workings to identify and resolve complex connection issues. SSH provides sophisticated debugging capabilities that, while potentially overwhelming at first glance, offer invaluable insights into the connection process. These advanced techniques become particularly necessary when dealing with enterprise environments, complex network configurations, or when standard error messages prove insufficient for diagnosis. 

During production incidents or when supporting mission-critical systems, these debugging approaches help us understand the intricate dance between client and server configurations, network interactions, and authentication mechanisms. Let's explore the advanced tools and techniques that experienced system administrators rely on for resolving challenging SSH connection problems.

### Verbose Logging

The very first step which should be done - enable excessive logging. SSH's logging capabilities represent one of our most powerful diagnostic tools, offering three distinct levels of detail (`-v`, `-vv`, `-vvv`). Each level peels back another layer of the connection process:

```bash
# Basic debugging output
$ ssh -v user@hostname
OpenSSH_8.9p1 Ubuntu-3ubuntu0.1, OpenSSL 3.0.2 15 Mar 2022
debug1: Reading configuration data /etc/ssh/ssh_config
debug1: Connecting to hostname port 22 [192.168.1.100]

# More detailed protocol debugging
$ ssh -vv user@hostname
debug2: resolving "hostname" port 22
debug2: ssh_connect_direct: needpriv 0
debug2: fd 3 setting O_NONBLOCK

# Maximum verbosity for complex issues
$ ssh -vvv user@hostname
debug3: send packet: type 5
debug3: receive packet: type 6
debug3: rekey after 134217728 bytes, 3600 seconds
```

### Server-Side Logging

Understanding what's happening on SSH server gives better vision of root cause of the problems, as well as security and troubleshooting. By enabling detailed logging, we can monitor authentication attempts, track user sessions, and investigate potential security incidents with precision.

To unlock the full potential of SSH logging, at first we need to modify SSH daemon configuration. Open `/etc/ssh/sshd_config` and set the logging level to its most verbose setting:

```shell
LogLevel DEBUG3
```

SSH activity can be monitored in real-time through system logs. The log location varies by Linux distribution:

```shell
# For Debian-based systems (Ubuntu, Debian)
sudo tail -f /var/log/auth.log

# For Red Hat-based systems (RHEL, CentOS, Fedora)
sudo tail -f /var/log/secure
```

The logs contain detailed information about SSH connections. Here's an example of a successful login with its associated IP address:

```shell
Apr 15 14:23:21 server sshd[12345]: Accepted publickey for alice from 192.168.1.100 port 52413
```

Failed authentication attempts are also recorded, providing valuable security insights:

```shell
Apr 15 14:25:33 server sshd[12346]: Failed password for invalid user admin from 203.0.113.1 port 59632 ssh2
```

Log rotation helps manage the increased volume of data from DEBUG3 level logging. This can be configured in `/etc/logrotate.d/sshd` to maintain disk space while preserving historical data.

Note that verbose logging creates additional system overhead. In high-traffic production environments, consider reducing the log level after completing specific monitoring or investigation tasks.

### Testing Connectivity

Before diving into complex SSH issues, establishing basic connectivity helps narrow down potential problems. Let's start by examining network paths and connections.

The `netcat` utility provides a straightforward way to verify if the SSH port accepts connections:

```shell
nc -zv hostname 22
```

The `-z` flag tells netcat to scan for listening daemons without sending data, while `-v` enables verbose output. A successful response looks like 'Connection to hostname port 22 succeeded!', while a failure might show 'Connection refused' or 'Connection timed out'. This test confirms basic TCP connectivity without attempting SSH authentication.

When connection issues arise, tracing the network path often reveals routing problems or blocked ports:

```shell
traceroute hostname
```

DNS resolution problems can manifest as connection failures, so checking name resolution adds another layer of verification:

```shell
dig hostname
```

Moving beyond basic connectivity, validating SSH configuration prevents common setup issues. The SSH client includes built-in configuration testing:

```shell
ssh -G hostname
```

This command displays the exact configuration that will be used when connecting to the specified host, including inherited defaults and matching Host blocks.

For server-side verification, the SSH daemon offers similar diagnostic capabilities:

```shell
sudo sshd -T
```

This command performs a comprehensive check of the server configuration, displaying the active settings after processing all included files and applying default values. The output helps identify misconfigurations before they impact users.
## Best Practices for SSH Troubleshooting

When troubleshooting SSH issues, following a methodical approach leads to faster resolution. Starting with basic connectivity checks establishes a foundation for further investigation. Moving through permission verification and authentication methods helps isolate problems systematically. System logs and verbose SSH output often reveal the root cause of connection issues.

Maintaining clear documentation strengthens our troubleshooting capabilities. Recording configuration changes, preserving working configurations, and keeping configuration backups creates a reliable reference point when issues arise. This documentation becomes particularly valuable when dealing with complex multi-server environments.

During troubleshooting, maintaining security remains paramount. Avoiding temporary security bypasses prevents accidental exposure. Host key changes warrant careful verification, and proper file permissions must be maintained throughout the debugging process.
## Conclusion

SSH debugging requires a methodical approach and understanding of both the protocol and common failure points. By following this guide, you can efficiently diagnose and resolve SSH connection issues while maintaining security. Remember that SSH's complexity is a feature, not a bug – it's designed to be secure first and convenient second.

Future maintenance of SSH connections can be simplified by implementing proper monitoring, maintaining documentation, and following security best practices. When issues do arise, a systematic debugging approach will help resolve them quickly and effectively.
