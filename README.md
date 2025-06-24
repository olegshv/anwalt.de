**Answers to the technical assignment for the position of cloud infrastructure engineer.**


### 1.   **Operating system, basic networking and scripting**

#### a) While managing Linux-based servers, you come across an 8-core box taking very long to establish a connection (via secure shell). Once in, you notice the following:
**load average: (99.53, 97.19, 91.12)**


>#### Explain what the above means

The load average values represent the number of processes that are either running or waiting for CPU/IO resources during the last 1, 5, and 15 minutes. On an 8-core system, a load average close to 8 is considered optimal, as it matches the number of available CPU cores. In this case, the system is under severe load, many processes (91-92) are queued for execution, and over time, the picture gets worse.

>#### Speculate what could be causing it (give examples)

This problem can be caused by many reasons, for example:  
- **CPU-bound:** A stuck or buggy process consuming all available CPU resources, or excessive parallel builds/tasks that overwhelm the CPU scheduler.  
- **IO-bound:** Disk subsystem problems (slow disks or storage controller issues) can cause processes to wait for IO, increasing the load.
- **Memory-bound:** There may also be insufficient RAM, and when working with swap, a queue of processes accumulates.

>#### Theorise how you would solve one of the cases you’ve just described, hence returning the box to normal operation

As an example, let’s consider the case of slowdown and a high load average by PostgreSQL process.

**Step 1.** I would use tools like `htop`,  to identify which processes are consuming the most resources (CPU, I/O).

**Step 2.** For example, we see many postgres processes with the name of one of the databases. 
We execute an SQL query to understand what is currently happening on the database server.

```
select age(clock_timestamp(), query_start), * from pg_stat_activity
where state = 'active' and pid <> pg_backend_pid()
order by query_start asc;
```

**Step 3.** Here, everything is very individual depending on the purpose of this server. Let's assume that our server is internal and does not contain anything important. We can kill the problematic process without coordination and involvement of the responsible teams.

```
SELECT pg_terminate_backend(<pid>);
```
**Step 4.** Check again `htop` to see if the load on the server has gone down. If everything is fine, we can pass the logs to the responsible team for investigation.

---

#### b) You have created a lightweight script for pushing metrics into a centralised timeseries database. Testing it locally on your laptop, everything works fine. Running it on a server, however, throws back the following error message:
`getaddrinfo for my-cool-metrics.server.internal failed: Name or service not known`
>#### Explain what the error message is telling you

This error means that the server running the script cannot find the IP address for the domain name. This may be caused by a missing DNS record, incorrect DNS configuration, or the name being assigned to an internal network that is not accessible from this server.

>#### The endpoint is correct, propose a solution to making your script work

If we know that the endpoint is correct, it means that we are locally connected to a DNS server that knows about this host, or it is manually added to the hosts file.

**Let's fix this:** 

**Step 1:** Fist of all we should doublcheck if this DNS resolved on the server. We can use commands `dig` (linux) or `nslookup` (windows).  
```
dig my-cool-metrics.server.internal
nslookup my-cool-metrics.server.internal
```
**Step 2:** Check which DNS servers we are connected to locally and on the server where the script needs to be run. This can be checked with the commands `ipconfig /all`  windows `/etc/resolv.conf`  linux. 

**Step 3:** If we see a difference in DNS servers, we can add the necessary one or use a bypass and add a record in `/etc/hosts` on the server. It is also advisable to clear your cache.

**Step 4:** If the endpoint still does not resolve, we need to make sure that we are in the same VPC. 

**Step 5:** If we are in the same VPC, the next step is to pay attention to the subnets and whether there are routes between them on the server. It may be that the DNS server is located in another subnet to which we simply do not have access.

**Step 6:** Most likely, after these checks, we have already found a potential problem and can try to perform the check again from step 1.

---

#### с) A web server running a standard reverse-proxy setup (nginx + backend running on the same box, communicating over TCP) sporadically returns 502 response codes. CPU load, load average, memory utilisation, disk space and I/O metrics are within standard operational ranges. The multi-threaded, back-end application, running on the server, is self-sufficient (does not require external services to operate) and is capable of reliably handling up to 1000 qps. Assuming the server is on the open internet and is a known authority for randomly providing baby names, speculate why nginx could be returning 502 responses.

A 502 error (Bad Gateway) from nginx indicates it couldn’t get a valid response from its upstream (from back-end).
- This may be caused by too short timeouts `proxy_read_timeout` and `proxy_connect_timeout`
- The connection to the backend may be configured incorrectly and we are receiving the error: `no live upstreams while connecting to upstream`. This may be caused by incorrect port or host name configuration.

---
#### d) You need to create an automated approach to making centrally-managed (remote service) environment variables available to a group of Linux-based servers (at the shell level). The allowed synchronisation drift is 10 seconds. Propose a solution using BASH, Python or any scripting language of your choice. Assuming the centralised storage offers a simple HTTP endpoint (basic authentication, takes only variable names as parameters - comma-separated string, takes 2 seconds to respond), provide a simple script for retrieving the values and pulling them to the servers. Describe your solution’s workflow.

I developed and implemented a test solution for centralised management of environment variables in a group of Linux-based servers using Docker containers:

- **Centralized mock service** (Flask): A lightweight HTTP server securely stores and serves environment variables. Variables can be fetched (GET) and updated on the fly (POST) with basic authentication.
    
- **Sync client** (Python): Each server (container) runs a script that securely pulls the latest environment variables from the central service every 10 seconds and writes them atomically to a shell-available file.
    
- **Automation & scaling:** The entire solution is containerized using Docker Compose for easy deployment and scaling. Multiple clients can synchronize with the central service independently.
    
- **Code is version-controlled**: All scripts and configuration files are committed to the repository.
    

This setup enables near real-time (<10s drift) distribution and live update of environment variables across multiple servers with a single source of truth.

See the screenshots below demonstrating multi-client sync, environment variable updates, and real-time synchronization.


>*In this screenshot, we see a test stand. All containers (mockserver and two sync clients) are running. Logs show that both clients periodically fetch environment variables and write them to file.*
![Знімок екрана 2025-06-24 121106](https://github.com/user-attachments/assets/75187b68-f024-47dc-8e7c-b11cb50b920a)

>*Here we output the test values of the variables on both servers.*
![Знімок екрана 2025-06-24 121133](https://github.com/user-attachments/assets/d0739781-7b86-4e57-8a93-54b42a78d7a1)

>*Sending a POST request to the mockserver to update the SECRET_KEY variable. The server confirms the update with a JSON response.*
![Знімок екрана 2025-06-24 121537](https://github.com/user-attachments/assets/c81f2660-daeb-4831-accc-cc733fad3a2d)

>*Live logs from Docker Desktop show both sync clients fetching updated variables from the mockserver and writing them to file after the update request.*
![Знімок екрана 2025-06-24 121613](https://github.com/user-attachments/assets/1d97ff13-07f0-4f3c-bb27-d641d462b373)

>*Reading the environment variable file inside both client containers confirms that the new SECRET_KEY value has been successfully synchronized.*
![Знімок екрана 2025-06-24 121704](https://github.com/user-attachments/assets/4a8a8047-1d29-4abd-8929-b5fc82068061)

[Synchronisation script link](https://github.com/olegshv/anwalt.de/blob/main/sync-test/remote_env_sync.py)

---

#### e) You’re setting up a small cluster of servers (3-tier deployment, 4 servers - 1:2:1) and you need to decide how you would configure their networking. Provide a simple diagram to illustrate how you would achieve this (assume you’re not working with physical servers), indicating connectivity links and assigned IP addresses.

![Знімок екрана 2025-06-24 002156](https://github.com/user-attachments/assets/9f47ad78-7523-41fb-bd29-952da2f565ad)


---

### 2.   **Amazon Web Services**

#### You’re running a multi-account setup (star topology). Each account serves a different area of the Software Development Lifecycle (development, testing, staging, production, monitoring, etc.). Only one of them takes any inbound traffic from the open internet.

---
#### a) Assuming you’ve got the task of organising the AWS accounts from scratch, what kind of networking topology would you use - as suggested above or different? Explain how you would solve the cross-account connectivity challenge and why (give examples to support your arguments). Provide details on the individual account setup (hint: go with one VPC per account), including networking configuration, indication of which account can “speak” to which of the rest and how you would control the traffic flow (hint: don’t go deeper than VPC and its directly related components, e.g. subnets, routing tables, security groups, etc.) 

For a multi-account AWS setup, I would choose a star (hub-and-spoke) topology with one VPC per account, using AWS Transit Gateway for cross-account connectivity. This approach offers strong isolation between environments, centralized control of traffic, and simplifies network management as the environment scales.
##### **Networking Topology**

- **Each AWS account (development, testing, staging, production, monitoring, etc.) has its own VPC.**
- **Only the “hub” account (typically production or a dedicated network/account) has direct inbound access from the internet.**
- **All other accounts are “spokes”, connected to the hub via AWS Transit Gateway (TGW).**

##### **Cross-Account Connectivity Solution**

- **AWS Transit Gateway** is deployed in the “hub” account and attached to each VPC from the spoke accounts. TGW acts as a central router, allowing or denying communication between accounts using route tables and attachment policies.
    
- **Traffic flow is managed using TGW route tables, VPC route tables, security groups, and NACLs:**
    
    - Only the hub account is connected to the Internet Gateway (IGW).
    - Spoke accounts (development, test, etc.) access other environments only as allowed via TGW and route table rules.
    - For example, monitoring can access all other accounts for metrics, but development cannot access production, unless specifically allowed.
#### **Why Star Topology with Transit Gateway?**

- **Scalability:** Transit Gateway simplifies the addition of new accounts/VPCs without a mesh of VPC peering connections.
    
- **Security and Isolation:** Each environment is fully isolated at the account and VPC level, reducing blast radius.
    
- **Centralized Control:** All inter-account routing decisions are managed in one place.
    
- **Reduced Complexity:** Avoids the operational overhead and route table bloat of full mesh peering.

![Знімок екрана 2025-06-24 130738](https://github.com/user-attachments/assets/256eebc6-7530-4faf-b5db-b9300363200c)


---
####  b) There are multiple groups of employees, requiring different levels of access permissions to each of the accounts. How would you architect an IAM-based solution to grant and manage these? Explain the benefits of the suggested solution and list any potential drawbacks or considerations. 

I would use AWS Identity Center to centrally manage user access across all AWS accounts. I would create groups (like Developers, Admins, QA) and assign them to roles with the needed permissions in each account. This way, each group only gets access to what they need.

**Benefits:**

- Easy to manage users and permissions from one place.
- Quick onboarding/offboarding and group changes.
- Enforces least privilege and improves security.
- Auditing is simpler—you know who has access to what.

**Drawbacks:**

- Initial setup can be a bit complex because each group requires very careful configuration of permissions.
- Changes may not take effect immediately everywhere.
- Requires some learning for teams new to SSO/role-based access.

---

#### c) All in-house-built services deployed to the environments need to use local (to their host AWS account) AWS resources, while some of them also need to be able to access AWS resources from other AWS accounts. Explain how you would manage the permissions, available to each of the services (regardless of the platform they’re running on - could be EC2, ECS, EKS, Fargate, etc.) and how you would authorise access to the in-house-built services/applications.

1. **Local resources:** each service (on EC2, ECS, EKS, Fargate, etc.), we create an IAM role with only the permissions needed to access resources in its own AWS account. Attach this role to the service (for example, as an instance role, task role, or service account).

2.  **Cross-account access:** If a service needs to access resources in another AWS account, set up IAM role in the target account (the account that owns the resource).
- In the target account, create an IAM role with the needed permissions and configure a **trust policy** to allow the source service's role to "assume" it (using `sts:AssumeRole`).
- In the source account, update the service’s IAM policy to allow it to assume the cross-account role.


---

### 3.   **Containerisation**

#### You’ve got the task of putting together a Docker-based container image, which would be used as the foundation of a broad variety of micro services. It has to be streamlined, reliable and multi-architecture compatible (for the sake of simplicity, needs to run on x86_64 and ARM64).

#### a) Propose a plan how you would approach the task, gather initial requirements and nominate stakeholders

The first thing we need to do is get all the requirements from the competent people who gave us the task.

**What we need to know:**
- Application stack (PHP8, PostgreSQL, Redis)
- Target platforms (x86_64, ARM64)
- Security, performance, and compliance needs
- And usage scenarios (prod, dev, etc.)

**Define Stakeholders:**
-  **Product Owner** — sets business goals and priorities
- **Developers** — provide app requirements, use images for local/dev
- **DevOps/Cloud Engineers** — design and implement the build/release workflow
- **QA Team** — validate container behaviour across environments
- **Security Team** — review image security and compliance

**Draft Solution Design:**
- Propose a multi-stage Dockerfile with PHP8, PostgreSQL/Redis support, and multi-arch builds
- Define CI/CD pipeline for automated build
- Plan for versioning, tagging, and documentation

**Review & Feedback:**
- Present the plan and Dockerfile design to all stakeholders
- Gather feedback and address concerns (e.g., image size, security, usability)

**Implementation:**
- Build and test the Docker image for both architectures
- Integrate with CI/CD for automated publishing and scanning
- Document usage for developers and operations


---

#### b) Provide an example build file (Dockerfile), which would create a container image for a standard PHP8-based application, which would in turn be communicating with a PostgreSQL relational database and a Redis key-value store.

Files in the repository


---

#### c) Given the container image would be used in a variety of environments (locally by developers, for automated testing, beta deployments, etc.), explain how you would build, store, manage and maintain it (hint: remember it would be pulled from different locations). Provide a diagram to visualise the proposed workflow.

**Build**
- Use a CI/CD pipeline (e.g., GitHub Actions, GitLab CI, Jenkins) to automatically build the Docker image on every push to the main branch.
- Build the image for multiple architectures (x86_64 and ARM64) using Docker Buildx.

**2. Store**
- Push the built image to a centralized container registry (e.g., Docker Hub, AWS ECR, GitHub Container Registry).
- Use versioned tags (e.g., `latest`, `1.0.0`, `dev`) for easy reference.

**3. Manage**
- Set up automated security scans in the registry to detect vulnerabilities.
- Implement role-based access to control who can push/pull images.
- Regularly clean up unused/old images to save space and reduce risk.

**4. Maintain**
- Update dependencies and base images regularly via scheduled pipeline jobs.
- Patch vulnerabilities quickly and rebuild the image.
- Monitor image usage and pull statistics.
- Maintain documentation for how to use and update the image.

**5. Usage**
- Developers pull images locally for testing and development.
- QA and CI/CD pipelines use the image for automated tests.
- Operations use the same image for staging and production deployments.
