# Tech Articles Repository 
This repository contains a collection of articles on various technical topics. Each article is organized in a separate directory, with its own README file and any necessary supporting files or resources. 
## Articles
### Functional, Action, Sequence: 3 Diagram Types for Multi-Dimensional Software Modelling
This article discusses using functional diagrams for high-level system architecture, action diagrams for illustrating process flows and logic, and sequence diagrams for detailing object interactions. Together, these three diagram types enable comprehensive modeling of software systems from multiple perspectives - architectural structure, process workflows, and granular execution logic - supporting documentation, communication, and traceability.

Published on [Medium](https://medium.com/@eugene-zimin/functional-action-sequence-3-diagram-types-for-multi-dimensional-software-modeling-d5e5b1a1d870) and [DEV.to](https://dev.to/eugene-zimin/functional-action-sequence-3-diagram-types-for-multi-dimensional-software-modeling-3a50) on March 2, 2024.
### Google Cloud: Provisioning a Virtual Machine and Accessing it via SSH
This article guides users through provisioning a virtual machine on Google Cloud Compute Engine and accessing it via SSH. It covers prerequisites, creating a Compute Engine instance, configuring settings like machine type and networking, establishing an SSH connection using various methods, and verifying the connection and instance details. By following the steps, readers gain practical experience deploying on Google's Cloud infrastructure.

Published on [Medium](https://medium.com/p/dde4307a8e9b) on March 4, 2024.
### Configuring SSH to Access Remote Server
The article guides configuring SSH to securely access remote servers like Google Cloud VMs. It covers generating SSH key pairs, adding the public key to the server, disabling password authentication, and customizing the SSH client configuration file for simplified connections and proxying through bastion hosts. Following these steps enables secure encrypted remote access.

Published on [DEV.to](https://dev.to/eugene-zimin/configuring-ssh-to-access-remote-server-2ljk) [Medium](https://medium.com/p/f12f94a8bec7) and [Substack](https://eugenezimin.substack.com/publish/posts/detail/143371896/share-center) on April 7, 2024.

### Database per Service as a Design Pattern
The article explores the Database per Service pattern, where microservices own individual databases, contrasting it with monolithic shared data stores. It highlights benefits like development autonomy, technology flexibility, and easier maintenance, enabled by API-based data encapsulation. While acknowledging challenges, it presents the pattern as crucial for system adaptability, promising future discussion on drawbacks.

Published on [Medium](https://medium.com/p/1d48cccd0b19) and [DEV.to](https://dev.to/eugene-zimin/database-per-service-as-a-design-pattern-44gi) on June 13, 2024.

### Using Domain-Driven Design to to Create Microservice App
This article explores the development of a Twitter-like platform using Domain-Driven Design and microservices. It details the design of `UserManagementService` and `MessagingService`, highlighting key DDD concepts and architectural decisions. The discussion covers inter-service communication, data management, and scalability strategies, offering insights into building complex, distributed systems that can evolve with changing requirements.

Published on [DEV.to](https://dev.to/eugene-zimin/leveraging-domain-driven-design-for-application-design-58e2) and [Medium](https://medium.com/@eugene-zimin/using-domain-driven-design-to-to-create-microservice-app-e234154a3fd1) on June 23, 2024.

### JWT at a Glance
This article provides an overview of JSON Web Tokens (JWT) and their role in authentication and authorization. It compares JWT-based authentication to traditional session-based methods, highlighting JWT's stateless nature and scalability advantages. The piece explains JWT structure, including header, payload, and signature components, and discusses the importance of token refreshing for security. It also touches on the integration of JWT with OAuth 2.0 and OpenID Connect (OIDC) for enhanced application security. The article aims to clarify common misconceptions about JWT and its relationship to other authentication protocols.

Published on [DEV.to](https://dev.to/eugene-zimin/jwt-at-a-glance-4f1d) and [Medium](https://medium.com/@eugene-zimin/jwt-at-a-glance-0357387417d4) on August 18, 2024.
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
