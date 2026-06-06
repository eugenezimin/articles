# Tech Articles Repository 
This repository contains a collection of articles on various technical topics. Each article is organized in a separate directory, with its own README file and any necessary supporting files or resources. 

## Articles

### SSH & Remote Access

#### Google Cloud: Provisioning a Virtual Machine and Accessing it via SSH
This article guides users through provisioning a virtual machine on Google Cloud Compute Engine and accessing it via SSH. It covers prerequisites, creating a Compute Engine instance, configuring settings like machine type and networking, establishing an SSH connection using various methods, and verifying the connection and instance details. By following the steps, readers gain practical experience deploying on Google's Cloud infrastructure.

Published on [Medium](https://medium.com/p/dde4307a8e9b) on March 4, 2024.

#### Access to Google Cloud Virtual Machine through SSH
A practical walkthrough for establishing a secure SSH connection to a Google Compute Engine virtual machine. It covers local SSH setup on Linux, macOS, and Windows, key pair generation with `ssh-keygen`, GCP-specific public key metadata requirements, and server-side hardening by disabling password authentication. A companion piece to the VM provisioning article above.

Published on [Medium](https://medium.com/@eugene-zimin/configuring-ssh-to-access-remote-server-f12f94a8bec7) and [DEV.to](https://dev.to/eugene-zimin/configuring-ssh-to-access-remote-server-2ljk).

#### Configuring SSH to Access Remote Server
The article guides configuring SSH to securely access remote servers like Google Cloud VMs. It covers generating SSH key pairs, adding the public key to the server, disabling password authentication, and customizing the SSH client configuration file for simplified connections and proxying through bastion hosts. Following these steps enables secure encrypted remote access.

Published on [DEV.to](https://dev.to/eugene-zimin/configuring-ssh-to-access-remote-server-2ljk), [Medium](https://medium.com/p/f12f94a8bec7), and [Substack](https://eugenezimin.substack.com/publish/posts/detail/143371896/share-center) on April 7, 2024.

#### Understanding SSH Key Pairs — A Developer's Guide
A developer-focused deep dive into SSH key pairs that goes beyond key generation commands and explains the underlying cryptography. It walks through RSA's prime-number factoring problem, ECDSA's elliptic curve approach, and Ed25519's modern Edwards-curve design, with concrete algorithm comparisons and `ssh-keygen` invocations for each. Covers passphrases, key fingerprints, and the `authorized_keys` format on the server side.

Published on [DEV.to](https://dev.to/eugene-zimin/understanding-ssh-key-pairs-a-developers-guide-2eoo).

#### SSH Config File — Forgotten Gem
An article dedicated to the `~/.ssh/config` file — a built-in OpenSSH tool that turns verbose SSH commands into short, memorable aliases. It demonstrates how to define named host profiles, apply wildcard patterns to groups of servers, and use advanced features such as `ProxyJump` for bastion-host chaining, `ForwardAgent`, and keep-alive settings. All without installing any additional software.

Published on [DEV.to](https://dev.to/eugene-zimin/ssh-config-file-forgotten-gem-1339).

#### Debugging SSH Connections — A Comprehensive Guide
A systematic troubleshooting reference for SSH connection failures, structured around the five stages of an SSH handshake. It covers the most common error classes — connection refused, host key verification failures, and permission denied — with concrete diagnostic commands and annotated output for each. Cloud-specific scenarios (AWS security groups, GCP firewall rules) and server-side log reading are also addressed.

Published on [DEV.to](https://dev.to/eugene-zimin/debugging-ssh-connections-a-comprehensive-guide-1hoc).

---

### API Authentication

#### API Authentication — Part I. Basic Authentication
The opening article in the API authentication series, establishing the conceptual foundation by separating authentication (proving identity) from authorization (granting access). It explains how Basic Auth credentials are base64-encoded and transmitted via the `Authorization` header, demonstrates both client and server implementations in Python, and honestly addresses the mechanism's limitations — credentials on every request, no built-in expiry, base64 is not encryption.

Published on [DEV.to](https://dev.to/eugene-zimin/practical-guide-to-api-authentication-part-i-basic-authentication-4ndn).

#### API Authentication — Part II. API Keys
The second article in the series, introducing API Keys as a more scalable alternative to Basic Auth for machine-to-machine communication. It traces the mechanism's history through the mid-2000s public API boom and walks through a Python implementation that generates structured, cryptographically secure keys with embedded metadata. Covers rate limiting, usage analytics, and per-key permission scoping.

Published on [DEV.to](https://dev.to/eugene-zimin/api-authentication-part-ii-api-keys-2l51).

#### API Authentication — Part III. JWT — The Self-Contained Token
The third article in the series, explaining how JSON Web Tokens eliminate the database roundtrip required by API Keys by embedding all identity metadata directly inside the token and cryptographically signing it. It traces JWT's origins from the server-side session era through RFC 7519 (May 2015), introduces the JOSE family of standards, and is honest about the core trade-off: a JWT cannot be revoked before it expires. Sets up the need for OAuth 2.0 in Part IV.

Published on [DEV.to](https://dev.to/eugene-zimin/api-authentication-part-iii-jwt-tokens-3c6a), [Medium](https://medium.com/@eugene-zimin/api-authentication-part-iii-jwt-tokens-f511d5dfb43a), and [Habr](https://habr.com/en/articles/1036016/).

#### API Authentication — Part IV. OAuth 2.0 and OpenID Connect: Letting Someone Act for You
The fourth and final article in the series answers the question the first three parts didn't: not "who are you?" but "how do you let an app act on your behalf without handing it your password?" It begins with the **password anti-pattern** — the intuitive but flawed approach of sharing credentials with a third party — and identifies its four failure modes: all-or-nothing access, credential storage risk, inability to revoke without disrupting everything else, and incompatibility with two-factor authentication. The fix is OAuth 2.0, built around a scoped, time-limited **access token** issued after explicit user consent. The article defines the four OAuth roles (Resource Owner, Client, Authorization Server, Resource Server), explains **scopes** and the **consent screen** as the user-facing face of the protocol, and walks through the **Authorization Code flow** step by step. **OpenID Connect** is introduced as the thin identity layer on top of OAuth 2.0 that powers every "Sign in with…" button on the internet.

#### JWT at a Glance
This article provides a comprehensive overview of JSON Web Tokens (JWT) and their role in modern authentication and authorization systems. It compares JWT-based authentication to traditional session-based methods, explains JWT structure (header, payload, signature), and discusses token expiration, refresh strategies, and integration with OAuth 2.0 and OpenID Connect (OIDC). The author uses relatable analogies and clear diagrams to make complex concepts accessible to readers with varying levels of technical expertise.

Published on [DEV.to](https://dev.to/eugene-zimin/jwt-at-a-glance-4f1d) and [Medium](https://medium.com/@eugene-zimin/jwt-at-a-glance-0357387417d4) on August 18, 2024.

---

### Architecture & System Design

#### Functional, Action, Sequence: 3 Diagram Types for Multi-Dimensional Software Modelling
This article discusses using functional diagrams for high-level system architecture, action diagrams for illustrating process flows and logic, and sequence diagrams for detailing object interactions. Together, these three diagram types enable comprehensive modeling of software systems from multiple perspectives — architectural structure, process workflows, and granular execution logic — supporting documentation, communication, and traceability.

Published on [Medium](https://medium.com/@eugene-zimin/functional-action-sequence-3-diagram-types-for-multi-dimensional-software-modeling-d5e5b1a1d870) and [DEV.to](https://dev.to/eugene-zimin/functional-action-sequence-3-diagram-types-for-multi-dimensional-software-modeling-3a50) on March 2, 2024.

#### From Idea to Blueprint — Turning a Vague App Concept into Something You Can Actually Build (Lessons 1–3)
A three-part series ("Build a Twitter Clone") that begins before any code is written and works up to a complete, traceable blueprint for a scoped messaging app called `Bird`.

**Lesson 1** makes the case that a one-sentence app idea is a wish rather than a plan, and that diagrams are the cheapest place to discover a wrong decision. It introduces the three-lens modelling framework — behaviour (flowchart), structure (functional diagram), and interaction (sequence diagram) — each lens derived from the previous.

Published on [DEV.to](https://dev.to/eugene-zimin/from-idea-to-blueprint-turning-a-vague-app-concept-into-something-you-can-actually-build-1a60) and [Medium](https://medium.com/@eugene-zimin/from-idea-to-blueprint-turning-a-vague-app-concept-into-something-you-can-actually-build-23a45754afba) on May 17, 2026.

**Lesson 2** defers the diagrams by one lesson to build the data model first. It reads the three use cases for data clues, names two entities (`User` and `Message`), and derives a MySQL schema split across two databases — `ums` for identity and access, `twitter` for content and social graph — grounded in the Database per Service pattern and DDD bounded contexts.

Published on [DEV.to](https://dev.to/eugene-zimin/the-blueprint-beneath-the-blueprint-designing-data-model-and-choosing-its-database-3bhl) and [Medium](https://medium.com/@eugene-zimin/the-blueprint-beneath-the-blueprint-designing-data-model-and-choosing-its-database-f6b20d741f66) on May 23, 2026.

**Lesson 3** draws all three diagrams using "Post a message" as the single worked example, constructing each in strict order: flowchart → functional diagram → sequence diagram. It closes by tracing the same permission check across all three diagrams to demonstrate end-to-end traceability.

Published on [DEV.to](https://dev.to/eugene-zimin/drawing-the-blueprint-flowchart-functional-diagram-and-sequence-diagram-537c) and [Medium](https://medium.com/@eugene-zimin/drawing-the-blueprint-flowchart-functional-diagram-and-sequence-diagram-a3758d6846d3) on May 23, 2026.

#### Database per Service as a Design Pattern
This article explores the Database per Service pattern, a design approach where each microservice owns and manages its dedicated database. It begins by contrasting this model with traditional monolithic architectures, highlighting how shared databases can become bottlenecks for change and scalability. The article examines the benefits — enhanced development autonomy, flexible technology choices, and simplified maintenance — while acknowledging challenges such as cross-service data consistency.

Published on [Medium](https://medium.com/p/1d48cccd0b19) and [DEV.to](https://dev.to/eugene-zimin/database-per-service-as-a-design-pattern-44gi) on June 13, 2024.

#### Using Domain-Driven Design to Create Microservice App
This article explores the practical application of Domain-Driven Design (DDD) principles in developing a Twitter-like application using a microservices architecture. It details the design of `UserManagementService` and `MessagingService`, covering aggregates, repositories, domain services, inter-service communication strategies, event-driven consistency, and caching. It offers valuable insights into building complex, real-world distributed systems using modern software development practices.

Published on [DEV.to](https://dev.to/eugene-zimin/leveraging-domain-driven-design-for-application-design-58e2) and [Medium](https://medium.com/@eugene-zimin/using-domain-driven-design-to-to-create-microservice-app-e234154a3fd1) on June 23, 2024.

---

### Tools & Performance

#### A native macOS load tester app — and backpressure made it honest
An article about building Requester, a real-time HTTP load testing app for macOS written in Swift and SwiftUI. The piece explores three key design decisions: using a simple RPS-per-channel concurrency model, implementing honest backpressure (shedding requests instead of buffering them indefinitely), and leveraging Swift structured concurrency (`async`/`await`, actors, `TaskGroup`) to safely coordinate concurrent state. Includes practical insights on pitfalls like URLSession silently dropping custom headers, and demonstrates how a load tester's UI can make the truth about server bottlenecks immediately visible — when the "Received" line dips below "Sent," the endpoint is struggling.

Published on [Medium](https://medium.com/@eugene-zimin/a-native-macos-load-tester-app-and-backpressure-made-it-honest-6b72d946f4d0) and [DEV.to](https://dev.to/eugene-zimin/a-native-macos-load-tester-app-and-backpressure-made-it-honest-3jah).

---

## Contributing 
Contributions to this repository are welcome! If you would like to add a new article or improve an existing one, please follow these steps: 
1. Fork the repository. 
2. Create a new branch for your changes: `git checkout -b my-new-article` 
3. Add your article or make changes to an existing one. 
4. Commit your changes: `git commit -m "Add new article on [topic]"` 
5. Push your changes to your forked repository: `git push origin my-new-article` 
6. Open a pull request in this repository, describing your changes. 

Please ensure that your article is well-written, accurate, and includes relevant examples or code snippets. Follow the existing structure and formatting conventions used in the other articles. 

## License 
This repository is licensed under the [BSD 2-Clause License](LICENSE).
