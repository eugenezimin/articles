# [Configuring SSH to Access Remote Server](https://dev.to/eugene-zimin/configuring-ssh-to-access-remote-server-2ljk)
Earlier in another article, we provided a detailed description of how to create and set up a Virtual Machine (VM) instance in the Google Cloud Platform (GCP) using Google Compute Engine (GCE). It is accessible here - [Google Cloud: Provisioning a Virtual Machine and Accessing it via SSH](https://medium.com/@eugene-zimin/google-cloud-provisioning-a-virtual-machine-and-accessing-it-via-ssh-dde4307a8e9b).

Provisioning a GCP VM allows us to create our own powerful computing environment to serve as a sandbox or workspace for our further testing and experiments. Having successfully deployed a VM in GCP, the next crucial step is to establish a secure remote connection to this virtual machine. It is required by many reasons, starting from efficient administration and management up to the monitoring and observing it. Google Cloud Platform provides a straightforward method to configure SSH access to Compute Engine instances, facilitating an encrypted communication channel. In this article, we will outline the steps required to set up SSH access to a Google Compute Engine (GCE) virtual machine.

## Few Words About SSH
Secure Shell (SSH) is a cryptographic network protocol and the de facto standard for secure remote login and command execution on Unix-like operating systems. SSH provides a secure encrypted channel over an unsecured network, preventing potential eavesdropping, packet sniffing, or man-in-the-middle attacks that could compromise login credentials or sensitive data. By leveraging strong encryption algorithms and authenticated key exchange, SSH ensures data integrity and confidentiality, making it an essential tool for securely administering remote servers, transferring files, and managing networked systems over insecure networks such as the internet.

SSH operates through the use of encrypted key pairs - a public key that gets placed on the remote server, and a private key that is kept secure by the client. The keys are very large numbers derived via a one-way mathematical function, making them virtually impossible to derive if intercepted during transmission.

When initiating an SSH connection, the client and server negotiate a secure symmetrical encryption cipher and session keys to use. This key exchange utilizes the private/public keys for authentication and protection against man-in-the-middle attacks. Once the secure tunnel is established, all subsequent commands, file transfers, and communications are encrypted between the client and server.
![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/cw2az2xkm7x20jvgjj1z.png)Figure 1. Communication schema for SSH exchange

SSH supports several strong modern encryption algorithms such as AES, Blowfish, 3DES, and ciphers like ChaCha20. The specific algorithms used can be configured on both ends based on policy and requirements. SSH also provides data integrity verification through cryptographic message authentication codes like HMAC-SHA1 to detect tampering.

By default, SSH operates on TCP port 22, but can be configured to use any port. It supports various user authentication mechanisms like passwords, public keys, security keys, and more. SSH key-based authentication is considered more secure than basic password authentication.
## Configuring SSH on Local Machine

Before initiating an SSH connection to our Google Cloud VM instance, we'll need to have SSH configured and set up on our local machine. The steps vary slightly depending on the operating system, as Linux and macOS usually have preinstalled SSH client which requires minimal configuration, whereas Window requires a bit more steps to make initial setup ready.
#### Linux and macOS
Most Linux distributions and macOS come pre-installed with OpenSSH, a free open source SSH client and server utility. To check if it's installed, we can open a terminal and run:
```shell
ssh -V

# Response should be something like the line below
# OpenSSH_9.6p1, LibreSSL 3.3.6
```
This should display the installed OpenSSH version. If not installed, we can get it through the operating system's package manager, for Linux it may be usually `apt` or `yum` for macOS `brew` is very popular.
#### Windows
Windows 11 has pre-installed SSH client. To check it we need to open `cmd` application (a.k.a `Command Prompt`) and run the same command:
```shell
ssh -V
```
If we will see a similar output we saw for Linux and macOS (some names may vary), it means we have installed SSH client and we are good to go.

A little bit more complicated situation happens if Windows doesn't have preinstalled client. In that case we may use one of the following 3rd party applications to run it:
- [PuTTY](https://www.putty.org/) for Windows
- [Git Bash](https://git-scm.com/download/win) for Windows

### Generating Key Pairs
To establish secure SSH connections, we need to generate cryptographic key pairs consisting of a public and private key. The `ssh-keygen` utility allows us to create these key pairs locally on our machine. Before we start creating a key pair it may worth to overview file schema for the it.
![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ixv1emprhbt4i04lqlp4.png)Figure 2. Schema of SSH key pairs

We can run `ssh-keygen` in a terminal/command prompt and follow the prompts. Some common options include:

- `-t` to specify the key type (e.g. rsa, ecdsa, ed25519)
- `-b` to set the key length in bits (e.g. 2048, 4096)
- `-C` to add a comment to identify the key

For example:
```shell
ssh-keygen -t ecdsa -b 521
```

will give us the following output:
```
Generating public/private ecdsa key pair.
Enter file in which to save the key (~/.ssh/id_ecdsa): ~/.ssh/id_ecdsa_gce
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in ~/.ssh/id_ecdsa_gce
Your public key has been saved in ~/.ssh/id_ecdsa_gce.pub
The key fingerprint is:
SHA256:Utwi6b8NzdJSFT5RlH6HOvr7y5HvNJiw08YB7wxAaQU user@laptop.local
```

There are various key types we may use. Here are the most popular ones we may want to generate:
- **RSA** - One of the oldest and most widely used key types. Recommended minimum key length is 2048 bits, with 4096 bits being more secure.
- **ECDSA** (Elliptic Curve Digital Signature Algorithm) - This key type is based on elliptic curve cryptography which provides equal security strength with smaller key sizes compared to RSA.
- **Ed25519** - A modern EdDSA (Edwards-curve Digital Signature Algorithm) key type that provides better performance and security than RSA/ECDSA. Ed25519 uses elliptic curve cryptography with a 256-bit key length.

While RSA is the most widely compatible, Ed25519 keys are considered more secure and efficient for modern systems. We can check which key types our SSH server and client support using `ssh -Q key`.

During key generation, we have the option to protect the private key with a passphrase. While providing a passphrase enhances security, we need to enter it every time the key is used.

After generating, both keys - private and public - will be saved in the local SSH configuration folder. Usually (for Linux and macOS systems) this folder is under the following path - `~/.ssh/`. Both keys by default use their name pattern as `id-<algorithm-name>[.pub]` , where extension `.pub` is used only for public key from the pair. As an example, user may get `id-rsa` and `id-rsa.pub` if there was RSA algorithm used, or `id-ed25519` and `id-ed25519.pub` there was Ed25519 algorithm in use during key pair generation.

Next step would be to copy the content of the public key (which has `.pub` extension) to the remote server, in accordance with the Figure 2. We may copy the content of the public key and paste it on the new line of the `~/.ssh/authorized_keys` file for the user which we will be connecting to. We can do that by many ways, but usually we should have access to the remote server via screen sharing or through the web interface, like with Google Compute Engine in GCP, where we can paste our public key.

> **NOTE FOR GCP**
> GCP requires to add at the end of the key `userName` and `expireOn` in form of JSON. We should do that manually to get the ready for pasting. Eventually we should have something like that:
> 
> ```shell
> ecdsa-sha2-nistp521 AAAAE2...== user@laptop.local {"userName":"<user@yourgcp.email>","expireOn":"2024-05-06T08:43:20+0000"}
> ```

At the same time private key (without `.pub` extension) remains securely stored on our local machine. We must keep the private key safe and never share it.

With our key pair ready, we can now proceed to configure server to use key pair only and disallow further access using username and password.
### Configuring Server Side
While using SSH keys provides a much more secure authentication mechanism compared to passwords, many cloud providers, including Google Cloud Platform, enable password-based logins to SSH servers by default. However, relying solely on password authentication for SSH connections introduces potential security risks and is considered a poor practice, so we should consider to disable it and keep it disabled.

Main reasons why we should do that lay in the security considerations. Having password authentication enabled we allow anyone to try to connect to remote server and try out to brute force the password. Sometimes password are not that strong and such an attack might be successful.

That being said the advantages of disabling Password authentication for the remote server are as follows:

1. **Enhanced Security**: SSH keys utilize strong encryption algorithms and prevent brute-force and dictionary attacks that are common threats to password-based authentication. Keys are virtually impossible to guess or decrypt.
2. **Eliminate Weak Passwords**: Enforcing key-based authentication eliminates the risk of users setting weak or easily guessable passwords, which is a common vulnerability.
3. **Audit Trail**: SSH key pairs provide better audit trails and monitoring capabilities, as each key can be associated with a specific user or system.
4. **Compliance**: Many security standards and best practices, such as PCI-DSS, HIPAA, and NIST, recommend or mandate the use of key-based authentication over passwords for remote access to servers.

At the same time nothing comes without price. If any of the parts for the key pair would be lost or corrupted, it means we may also lost the access to the server, thus we should be very careful and keep generated key pair as good as possible.

To disable password authentication for the SSH server we need to modify the SSH daemon (`sshd`) configuration file. To do that we need to connect to the VM instance over SSH. We will use our new generated private key to connect to the server (don't forget to replace username and address of the server).
```shell
ssh -i ~/.ssh/id_ed25519 remote-user-name@remote-server-ip-address
```

On the remote server open the SSH daemon configuration file as a `superuser`:
```shell
sudo nano /etc/ssh/sshd_config # may be changed to vim
```

In the file editor find the line `#PasswordAuthentication yes` and change it to `PasswordAuthentication no` and save the file and exit the editor.

Finally we need to restart the SSH daemon to make our changes take effect:
```shell
sudo systemctl restart sshd # (or the appropriate command for your OS)
```
 
After making this change, the SSH server will only allow key-based authentication, and password logins will be disabled.

It's important to note that we should have at least one authorized SSH key added to the VM instance before disabling password authentication. Otherwise, we may get locked out of the system.

By enforcing key-based authentication and disabling password logins, we significantly enhance the security of our SSH server and remote access to our Google Cloud virtual machines, aligning with industry best practices for secure system administration.
#### Simplifying Connections with SSH Client Configuration File
While we can directly specify options when invoking the `ssh` command, using a configuration file allows us to set persistent options, create aliases, and simplify the process of connecting to remote hosts. This is particularly useful when managing multiple SSH connections to different servers or cloud instances.

On Unix-based systems (Linux and macOS), the SSH client refers to the configuration file located at `~/.ssh/config` location. On Windows systems using the OpenSSH client, the file is located at `%UserProfile%.ssh\config`.

The `~/.ssh/config` file supports a wide range of configuration options and settings that can be applied globally or to specific hosts. Here are some common use cases:
##### Creating Aliases
We can define aliases or shorthand names for hosts, making it easier to connect without having to type out the full hostname or IP address every time.

```configuration
Host remote_server
    HostName remote_host.com
    User ubuntu
```

Instead of `remote_host.com` it is possible to use IP address of the remote server directly. Now we can use:

```shell
ssh remote_server
```

to reach remote server instead of using its name `remote_host.com` or direct IP address. It's clear that aliases might be different and their usage makes it easier to set up connections.
##### Setting Default Options
We can set default options that will be applied to all SSH connections, such as the default user, identity file (private key), and forwarding settings.

```configuration
Host *
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
    ForwardAgent yes
```

In this configuration instead of doing aliasing, we set default configuration which will be applied to **all** connections and hosts. 1. The asterisk (`*`) is a wildcard that matches any hostname.

`User ubuntu` sets the default user account to be used for SSH connections. In this case, it will attempt to log in as the `ubuntu` user on remote hosts.

`IdentityFile ~/.ssh/id_rsa` specifies the path to the default SSH private key file that should be used for authentication. Here, it is set to `~/.ssh/id_rsa`, which is the standard location for an SSH private key on Unix-based systems. That's convenient way to use previously generated key pair.

`ForwardAgent yes` option enables SSH agent forwarding. When enabled, it allows authentication keys loaded into the local SSH agent to be automatically forwarded to the remote host, enabling single sign-on (SSO) functionality. This can be useful when you need to connect to additional hosts from the initial remote host without re-authenticating.
##### Host-Specific Settings
We can define settings specific to a particular host or group of hosts, such as using a different private key, enabling compression, or specifying a non-standard port.

```configuration
Host *.example.com
    IdentityFile ~/.ssh/id_rsa
    Compression yes

Host gcp-instance
    HostName 34.123.45.67
    User user2
    Port 2222
```

In this configurations we used 2 different values for `Host` key. In the first configuration option host entry applies settings to any host whose name matches the pattern `*.example.com`. The `*` acts as a wildcard, so this would include hosts like `server1.example.com`, `web.example.com`, or any other subdomain under the `example.com` domain.

`IdentityFile ~/.ssh/id_rsa` specifies that the private SSH key located at `~/.ssh/id_rsa` should be used for authentication when connecting to hosts matching the `*.example.com` pattern.

Second configuration behaves differently and creates an alias for the only single IP address of `34.123.45.67` in form of the `gcp-instance`.
##### Proxying Through Bastion Hosts
If we need to connect to instances that are not directly accessible (e.g., behind a bastion host or a NAT gateway), we can configure SSH tunneling through a jump host.

```configuration
Host gcp-instance
    HostName 10.0.0.5
    User user2
    ProxyJump bastion.example.com
```

By leveraging the `~/.ssh/config` file, we can streamline our SSH workflow, ensure consistent settings across connections, and simplify the management of multiple remote hosts, including our Google Cloud VM instances.

To get started, we can create or edit the file using a text editor, and refer to the `ssh_config` man pages (`man ssh_config`) for a comprehensive list of available options and their descriptions.