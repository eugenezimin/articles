# SSH Config File — Forgotten Gem

An article dedicated to the `~/.ssh/config` file — a tool that ships with every OpenSSH installation but is overlooked by a surprising number of developers who continue to type lengthy SSH commands by hand. The article opens with a concrete example of the pain this causes: a command like `ssh -i ~/.ssh/special_key.pem ubuntu@ec2-123-45-67-89.compute-1.amazonaws.com` is verbose, error-prone, and different for every server. The SSH config file solves this by letting you define named host profiles — each with its own username, identity file, port, hostname, and connection options — so the same connection becomes `ssh staging`. The article frames the config file as a bookmark system that embeds connection intelligence, not just shortcuts.

The foundational section walks through the structure of a config file block-by-block, showing how `Host`, `HostName`, `User`, `IdentityFile`, and `Port` directives combine into a reusable profile. Multiple profiles are demonstrated side by side (a GitHub profile, a staging EC2 instance, a production server), making it easy to see how the file scales with the number of hosts you manage. The article then moves into advanced features: wildcard patterns using `*` and `?` to apply shared settings to groups of hosts (e.g., `dev-*` or `staging-*`), which eliminates redundant configuration and enforces consistency across similar environments.

The final section covers the more powerful capabilities that most developers never discover: `ProxyJump` for chaining connections through bastion hosts without manual tunnelling, `ServerAliveInterval` and `ServerAliveCountMax` for keeping idle connections from dropping, `ForwardAgent` for securely propagating SSH credentials through jump hosts, and `StrictHostKeyChecking` for controlling how unknown host keys are handled in automated pipelines. The article's closing point is that none of these features require any additional software — they are all built into OpenSSH and available wherever SSH is installed.


Published on [DEV.to](https://dev.to/eugene-zimin/ssh-config-file-forgotten-gem-1339).

