# From Source Code to a Running Pod

*How to write a small Spring Boot service, package it as a container image, and deploy it to the Kubernetes cluster in our virtual machine, the third part of a three-part series for CST8277 Enterprise Application Programming.*

This is Part 3 of 3. [Part 1](Part%201%20-%20A%20Computer%20Inside%20Your%20Computer.md) built the Ubuntu 26.04 LTS virtual machine, and [Part 2](Part%202%20-%20A%20Kubernetes%20Cluster%20of%20Your%20Own.md) installed MicroK8s, the local image registry at `localhost:32000`, and Headlamp. This article assumes all three are in place.

## 1. The road from a source file to a Service

At the end of Part 2, the cluster in our VM could run any image that somebody had already built and published, as it did with the `nginx` web server. The step that remains is the one every enterprise developer takes many times a day, which is turning code they have just written into something the cluster can run, and that step is less a single leap than a chain of small transformations. Source code becomes a JAR file, the JAR becomes a container image, the image is pushed to a registry, the cluster pulls it to start pods, and a Service routes requests to those pods. Figure 1 draws the chain.

![From source code to a Kubernetes Service](M08-Fig4-Code-To-Pod.png)

*Figure 1. The path from source code to a running Service, in which Maven turns the code into a JAR, Docker turns the JAR into an image and pushes it to the registry, and Kubernetes starts two pods from the image behind a NodePort Service, with a check available after each link.*

Each link in that chain can be checked on its own, as the line beneath the figure reminds us. A JAR can be started with `java -jar`, an image can be started with `docker run`, and a Service can be called with `curl`. That property is what makes the chain practical, because when the final request fails, a developer who understands the links can test them one at a time and find the broken one in minutes, whereas a developer who knows only the first and last steps can do nothing but start again from the beginning. This article therefore walks the chain from left to right, stopping at each link to make sure it holds before moving on.

## 2. The toolchain

### 2.1 Java and Maven

Our service is written in Java, so the VM needs a Java Development Kit, the compiler and runtime together, and Maven, the build tool that downloads libraries and packages the compiled code into a JAR. The commands below install OpenJDK 25, the current long-term-support release of Java, together with Maven and `curl`, a small command-line HTTP client that the default Ubuntu 26.04 desktop does not include, and then print the versions of all three Java tools.

```bash
sudo apt-get install -y openjdk-25-jdk maven curl
java -version && javac -version && mvn -v
```

The `-y` option answers yes to the installer's confirmation question in advance. If every command prints a version, as in Figure 2, the Java toolchain is ready. The screenshot pipes the Maven output through `head -1` to keep it to a single line, and your own output of `mvn -v` will be a few lines longer.

![OpenJDK 25 and Maven installed](27_java_version.png)

*Figure 2. The version check after installation, in which java and javac report OpenJDK 25.0.4.1 and mvn reports Apache Maven 3.9.12.*

### 2.2 Docker

Building container images requires Docker, which we used in the containerization module. Ubuntu packages the Docker Engine in its own repositories under the name `docker.io`, and the separate `docker-buildx` package adds BuildKit, the modern build component that Docker uses to execute a Dockerfile. After installing both, add your user to the `docker` group, so that Docker commands work without `sudo`.

```bash
sudo apt-get install -y docker.io docker-buildx
sudo usermod -aG docker $USER     # then log out and log in again
docker run --rm hello-world
```

As with the `microk8s` group in Part 2, group membership takes effect only in a new login session, so log out and back in before running the last command. If you forget, the command fails with a message containing "permission denied" and `docker.sock`, which means only that the current session does not yet belong to the group. In the new session, the `hello-world` image downloads, runs, prints its greeting, and is removed again because of the `--rm` option, as Figures 3 and 4 show.

![Installing Docker Engine](28_docker_install.png)

*Figure 3. Installing the Docker Engine and BuildKit from the Ubuntu repositories.*

![Docker works](29_docker_hello.png)

*Figure 4. The hello-world container confirming that Docker can download and run images.*

Students who meet the "permission denied" message sometimes find advice online to make the Docker socket writable by everyone, with a command such as `chmod 666 /var/run/docker.sock`. Never follow it. The socket is the door through which programs give orders to the Docker daemon, and the daemon runs as root, so anyone who can write to the socket can start a container that mounts the host's entire file system and do anything they like with it. Membership in the `docker` group grants the same power, which is why that group is treated as equivalent to administrator rights, but it grants it only to the users you deliberately add.

## 3. The IDE and the project

### 3.1 Installing IntelliJ IDEA

Any IDE you are comfortable with will do for this course, whether IntelliJ IDEA, Visual Studio Code with the Java extensions, Eclipse, or NetBeans, and this article uses IntelliJ IDEA. Since 2025 IntelliJ IDEA has been a single product, free for non-commercial use, with its Ultimate features available through a trial or through a free educational license, for which you can apply at [jetbrains.com/community/education](https://www.jetbrains.com/community/education/) with your college e-mail address. Like MicroK8s, it is distributed as a snap, so one command installs it, as Figure 5 shows.

```bash
sudo snap install intellij-idea --classic
```

![Installing IntelliJ IDEA from the snap store](31_idea_install.png)

*Figure 5. Installing IntelliJ IDEA from the snap store.*

### 3.2 Generating the project with Spring Initializr

A Spring Boot project needs a build file that lists the right libraries in compatible versions, a main class, a configuration file, and a Maven wrapper, and writing all of that by hand is both tedious and error-prone. Spring Initializr, a web service at [start.spring.io](https://start.spring.io/), generates it for us. Open it in Firefox inside the VM and make the choices shown in Figure 6, which means Maven as the build tool, Java as the language, Spring Boot 4.1.x, the group `com.cst8277` and the artifact `demo`, Jar packaging, Java 25, and two dependencies, Spring Web for writing REST controllers and Spring Boot Actuator for the health endpoints that Kubernetes will use later.

![Generating the project with Spring Initializr](30_spring_initializr.png)

*Figure 6. Spring Initializr configured for a Maven project with Spring Boot 4.1, Java 25, the group com.cst8277, the artifact demo, and the Spring Web and Spring Boot Actuator dependencies.*

Click *Generate*. The browser downloads a file named `demo.zip`, which the commands below unpack into a `projects` folder in your home directory, after which the last command opens the new project in IntelliJ IDEA, the trailing `&` letting the IDE run in the background so that the terminal stays free.

```bash
mkdir -p ~/projects && cd ~/projects
unzip ~/Downloads/demo.zip
intellij-idea ~/projects/demo &
```

### 3.3 Opening the project and choosing the JDK

On its first start, IntelliJ IDEA asks you to accept its user agreement and to confirm that you trust the project, which matters because opening a Maven project runs code from its build file. It then loads the project and downloads the libraries listed in `pom.xml`, which takes a minute or two the first time.

The IDE does not always notice the JDK installed in section 2.1 by itself, in which case the editor shows the warning *Project JDK is not defined*, as in Figure 7. Click *Setup SDK* and select the detected Java 25 installation, as in Figure 8, and the warning disappears.

![IntelliJ IDEA asks for the project JDK](32_idea_jdk_missing.png)

*Figure 7. The editor warning that no project JDK is defined, with the Setup SDK link that resolves it.*

![Selecting the detected OpenJDK 25](33_idea_setup_sdk.png)

*Figure 8. Selecting the OpenJDK 25 installation that IntelliJ IDEA detected on the VM.*

Earlier versions of this course added Lombok at this point, a library that generates getters, constructors, and similar boilerplate during compilation. It is no longer needed, because Java records, which we met in Module 2, give the same benefit with plain Java and without an extra plugin in the IDE.

## 4. Hello World as a REST service

### 4.1 A record for the response

Our service will answer an HTTP request with a small JSON document containing a greeting and a counter. The shape of that document is described by a data transfer object, or DTO, a class whose only job is to carry data across a boundary, and a record is the natural way to write one. Create a package named `dto` inside `com.cst8277.demo` and, in it, the following file.

```java
package com.cst8277.demo.dto;

public record Greeting(long id, String content) { }
```

That single line declares an immutable class with two fields, a constructor that sets both, accessor methods named `id()` and `content()`, and sensible `equals`, `hashCode`, and `toString` methods. When Spring later converts a `Greeting` to JSON, it uses the accessors, so the response will contain exactly the keys `id` and `content`.

### 4.2 The controller

The controller is the class that receives HTTP requests and decides what to return. Create a second package, `controllers`, and in it the class below, which answers GET requests to the root URL with a greeting and counts the requests it has served.

```java
package com.cst8277.demo.controllers;

import com.cst8277.demo.dto.Greeting;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {

    private static final String TEMPLATE = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();

    @GetMapping("/")
    public Greeting greet(
            @RequestParam(defaultValue = "World") String name) {
        return new Greeting(counter.incrementAndGet(),
                            TEMPLATE.formatted(name));
    }
}
```

The annotation `@RestController` tells Spring that this class handles web requests and that whatever its methods return should be written into the response body, converted to JSON, rather than interpreted as the name of an HTML page. The annotation `@GetMapping("/")` maps GET requests for the root URL to the `greet` method, and `@RequestParam` reads the query parameter `name` from the URL, substituting `World` when the parameter is absent. The counter is an `AtomicLong` rather than a plain `long` because Spring serves requests on many threads at once, and an atomic counter guarantees that two simultaneous requests never receive the same number. Remember that counter, because in section 6 it will tell us something important about how Kubernetes distributes requests.

### 4.3 Health probes

The last piece of code is a line of configuration. Spring Boot Actuator can report two kinds of health that Kubernetes understands, liveness, which says whether the application is still working at all, and readiness, which says whether it is ready to receive traffic. Spring Boot switches these probes on automatically when it detects that it is running inside Kubernetes, and the line below switches them on everywhere, so that we can also see them when the application runs in the IDE. Open `src/main/resources/application.properties`, which Spring Initializr has already created with the application's name, and make it read as follows.

```properties
spring.application.name=demo
management.endpoint.health.probes.enabled=true
```

### 4.4 Running it

Figure 9 shows the finished project in IntelliJ IDEA, with the two new packages beside the generated `DemoApplication` class. The figure also shows a `Dockerfile` and a file named `demo-app.yaml` in the project root, which we write in sections 5 and 6.

![The project structure in IntelliJ IDEA](34_idea_project.png)

*Figure 9. The project in IntelliJ IDEA, with the controllers and dto packages under com.cst8277.demo and GreetingController open in the editor.*

Run the application by clicking the green Run button next to `DemoApplication`. The Run panel at the bottom of the window shows Spring Boot's log, in which the application reports that its embedded web server is listening on port 8080, and, for Spring Boot projects, tabs that list the application's beans, its health, its request mappings, and its environment, as Figure 10 shows.

![Running the application in the IDE](35_idea_run.png)

*Figure 10. The application running in the IDE, with the Spring Boot log in the Console tab and the Beans, Health, Mappings, and Environment tabs beside it in the Run panel.*

Now open `http://localhost:8080/?name=CST8277` in Firefox. The browser displays the JSON in Figure 11, whose `content` is "Hello, CST8277!" and whose `id` is 1. Reload the page, and the `id` grows by one each time, because the same controller object, and therefore the same counter, serves every request. Remove the parameter from the URL, and the greeting becomes "Hello, World!", the default that `@RequestParam` supplied.

![The JSON response of the service](36_browser_hello.png)

*Figure 11. The service's JSON response in Firefox, containing the request counter and the greeting built from the name parameter.*

Before continuing, stop the application in the IDE with the red Stop button. Section 5 starts the same application in a container that also listens on port 8080, and only one program can listen on a port at a time, so an application left running in the IDE would make the container fail to start.

### Learning Activity 1. Extend the service

Add a second endpoint, `GET /time`, that returns the current server time and the host name as JSON, using a record for the response as we did for `Greeting`. Run it in the IDE and call it both from Firefox and with `curl`. Then open `http://localhost:8080/actuator/health` and explain what the Actuator returns and how it relates to the liveness and readiness probes described in section 4.3.

## 5. From JAR to image

### 5.1 A multi-stage Dockerfile

The second link in the chain turns the application into a container image, and the recipe for an image is a Dockerfile, a text file of instructions that Docker executes one after another. Create a file named `Dockerfile` in the project root, next to `pom.xml`, with the content below, which Figure 12 also shows in the editor.

```dockerfile
# ---- build stage: compile and package with the full JDK ----
FROM eclipse-temurin:25-jdk AS build
WORKDIR /src
COPY .mvn .mvn
COPY mvnw pom.xml ./
RUN ./mvnw -q dependency:go-offline
COPY src src
RUN ./mvnw -q package -DskipTests

# ---- runtime stage: only the JRE and the application ----
FROM eclipse-temurin:25-jre
RUN useradd --system --uid 10001 app
WORKDIR /app
COPY --from=build /src/target/*.jar app.jar
USER 10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

![The multi-stage Dockerfile](37_dockerfile.png)

*Figure 12. The multi-stage Dockerfile in the project root.*

The file describes two images, as we saw in the containerization module, and only the second becomes the result. The first stage, named `build`, starts from `eclipse-temurin:25-jdk`, a full Java 25 development kit, and compiles the application with the Maven wrapper `mvnw`, a script that Spring Initializr placed in the project so that the build uses a known Maven version regardless of what is installed. The order of its instructions is deliberate. The build file is copied and the dependencies are downloaded before the source code is copied, because Docker caches each step and reuses it as long as its inputs have not changed, so that editing a Java file later reruns only the compilation and not the much slower download of every library.

The second stage starts afresh from `eclipse-temurin:25-jre`, which contains only the Java runtime, and copies in nothing from the first stage except the finished JAR. The compiler, Maven, the downloaded libraries, and the source code all stay behind in the discarded build stage, which makes the final image smaller and leaves an attacker who might break into the container with far fewer tools. The same reasoning explains the `useradd` and `USER 10001` lines, which make the application run as an ordinary, unprivileged user instead of as root, so that a flaw in the application cannot easily become control of the container. The last two instructions document the port the application listens on and the command that starts it.

### 5.2 Building, trying, and pushing the image

The commands below build the image, start a container from it to check that it works, remove that container, and finally push the image to the registry that Part 2 created.

```bash
cd ~/projects/demo
docker build -t localhost:32000/cst8277/demo-app:1.0 .
# try the container locally
docker run -d --name demo -p 8080:8080 \
    localhost:32000/cst8277/demo-app:1.0
curl 'http://localhost:8080/?name=Docker'
docker rm -f demo
# publish it to the cluster's registry
docker push localhost:32000/cst8277/demo-app:1.0
```

The name given with `-t` deserves a close look, because it does two jobs at once. The part before the first slash, `localhost:32000`, tells Docker which registry the image belongs to, so that `docker push` later knows where to send it without being told again. The part after it, `cst8277/demo-app`, names the image, and the tag after the colon, `1.0`, names this particular version. The final dot tells Docker to use the current folder, with its Dockerfile and source code, as the build context. Figure 13 shows the build, in which the build stage runs Maven and the runtime stage copies in the JAR.

![Building the image](38_docker_build.png)

*Figure 13. Building the image, in which the build stage runs Maven inside the JDK image and the runtime stage copies the resulting JAR into the JRE image.*

The `docker run` command starts the image in the background, because of `-d`, under the name `demo`, and connects port 8080 of the VM to port 8080 of the container, because of `-p 8080:8080`. Spring Boot needs a few seconds to start, so if `curl` reports that the connection was reset or that the server returned an empty reply, wait a moment and try again. Figure 14 shows the image and the running container, together with the answer "Hello, Docker!".

![The image size and the running container](39_docker_run.png)

*Figure 14. The image listed with a content size of 135 MB and a disk usage of 534 MB, the container running with port 8080 published, and the service answering with "Hello, Docker!".*

The two sizes in the image listing measure different things. The content size of 135 MB is roughly what has to travel over the network when the image is pushed or pulled, since image layers are stored and transferred in compressed form, while the disk usage of 534 MB is the space the unpacked layers occupy on the VM. Either figure is far below what a single-stage image containing the full JDK and Maven would need, and that difference is what the second stage of the Dockerfile buys.

Once the test succeeds, `docker rm -f demo` stops and removes the container, freeing port 8080 again, and `docker push` uploads the image to the registry, as Figure 15 shows. From this moment the image exists in a place where Kubernetes can find it.

![Pushing the image to the MicroK8s registry](40_docker_push.png)

*Figure 15. Pushing the image to the MicroK8s registry at localhost:32000.*

We are now halfway along the chain in Figure 1, with source code, JAR, image, and registry behind us, and only the pods and the Service still to come.

## 6. From image to Service

### 6.1 Describing the desired state

In Part 2 we started `nginx` with imperative commands. This time we write the desired state into a file, so that it can be read, reviewed, kept in version control, and applied again on any cluster. Create `demo-app.yaml` in the project root with the content below. It holds two objects separated by the line `---`, a Deployment that runs two replicas of our image and a Service that makes them reachable on port 30080 of the node.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  labels:
    app: demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
        - name: demo-app
          image: localhost:32000/cst8277/demo-app:1.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits: { memory: 512Mi }
---
apiVersion: v1
kind: Service
metadata:
  name: demo
  labels:
    app: demo
spec:
  type: NodePort
  selector:
    app: demo
  ports:
    - port: 8080
      targetPort: 8080
      nodePort: 30080
```

The file is long, but every part of it answers a question that Kubernetes needs answered. The Deployment asks for `replicas: 2`, two identical pods, and its `template` describes what each pod looks like, including the label `app: demo` that every pod receives. The `selector` tells the Deployment which pods it is responsible for, namely those carrying that same label, and the Service at the bottom uses the same label to decide which pods should receive its traffic. Labels and selectors are therefore the glue of the whole file, and a mismatch between them is a classic reason why a Service answers nothing.

The container section names the image we pushed, down to its registry and tag, and declares the two probes that section 4.3 prepared. Kubernetes calls the readiness endpoint and sends traffic to a pod only after it answers successfully, so that a pod still starting up never receives requests it cannot serve. It calls the liveness endpoint throughout the pod's life and restarts the container if that endpoint stops answering, which is how a hung application gets a fresh start without anyone noticing. The `resources` block tells the scheduler that each pod needs at least a tenth of a processor core, written `100m`, and 256 MiB of memory, and it caps the memory at 512 MiB, beyond which the container is stopped rather than allowed to starve its neighbors. Finally, the Service is of type NodePort, as in Part 2, but this time it fixes the node port at 30080 instead of letting Kubernetes choose one.

### 6.2 Applying it and calling the service

Apply the file, wait for the rollout to complete, and list what was created. Then call the service four times, and finally delete both pods and look at what remains.

```bash
kubectl apply -f demo-app.yaml
kubectl rollout status deployment/demo
kubectl get pods,svc -l app=demo -o wide
# call the service several times
for i in 1 2 3 4; do
  curl -s 'http://localhost:30080/?name=Kubernetes'; echo
done
# self-healing: delete the pods and watch them come back
kubectl delete pod -l app=demo --wait=false
kubectl get pods -l app=demo
```

Figure 16 shows the first three commands. The rollout reports that first zero, then one, then both of the two replicas became available, the pod listing shows two pods with their own cluster addresses on the node `cst8277-vm`, and the Service listing shows the mapping `8080:30080/TCP` together with the selector `app=demo`.

![The deployment rolled out](41_k8s_deploy.png)

*Figure 16. The deployment rolled out, with two running pods, each with its own address on the node cst8277-vm, and a NodePort Service mapping port 30080 to port 8080 of the pods selected by app=demo.*

### 6.3 What the counter reveals

Figure 17 shows the rest, and it rewards a careful look.

![Load balancing and self-healing](42_k8s_curl_heal.png)

*Figure 17. Four requests answered with the ids 1, 1, 2, and 3, which shows that two pods with separate counters shared the requests, followed by the deletion of the pods and their replacement by new pods, one of them not yet ready.*

When the application ran in the IDE, the `id` rose by exactly one with every request. Here the four answers carry the ids 1, 1, 2, and 3, which can only mean that the requests were served by two different pods, each holding its own counter in its own memory, with the Service distributing them between the two. We are watching horizontal scaling at work, and we are also watching its most important consequence, the one that Module 3 described in theory. A counter kept in memory belongs to one replica and is invisible to the others, so any state that must be shared, whether a counter, a shopping cart, or a login session, has to live outside the pods, in a database or a cache, and the pods themselves should be stateless.

The second half of the figure repeats the experiment from Part 2 with our own code. After the pods are deleted, the Deployment immediately creates new ones, and the listing catches one of them still starting, shown as `0/1` in the READY column, because its readiness probe has not yet succeeded. Until it does, the Service sends that pod no traffic at all, so a client calling the service during the restart is answered by the pod that is already ready.

## 7. Watching it in Headlamp

The same events can be followed in Headlamp, which Part 2 installed. If the port forward from Part 2 is no longer running, for example because the VM has been restarted since, start it again, create a fresh token if the old one has expired, and open `http://localhost:8888` in Firefox.

```bash
kubectl -n kube-system create token headlamp-admin
kubectl -n kube-system port-forward svc/headlamp 8888:80
```

The cluster overview in Figure 18 summarizes the resources of the cluster, which in the screenshot are four processor units, about 7 GB of memory, eight pods, and one ready node, and lists recent warning events. Among them you will probably find readiness probes that failed with "connection refused" while the demo pods were starting, which is the same moment the `0/1` in Figure 17 captured, recorded this time as an event rather than as a line of command output.

![Headlamp cluster overview](46_headlamp_overview.png)

*Figure 18. The Headlamp cluster overview, with one ready node and eight pods, and four warning events reporting readiness probes that were refused while the demo pods were starting.*

The Workloads page in Figure 19 counts the controllers in the cluster by kind. It shows eight healthy pods, six Deployments with their six ReplicaSets, which are the system components, the registry, Headlamp, and our own `demo`, and the single DaemonSet that runs Calico on the node, and a ring beside each count shows what share of them is running. Below the summary it lists the individual workloads. The Pods page in Figure 20 lists every pod in every namespace, including our two demo pods beside the system pods, the registry, and Headlamp itself.

![Workloads overview](47_headlamp_workloads.png)

*Figure 19. The Workloads page, with eight healthy pods, six Deployments, six ReplicaSets, and one DaemonSet, all of them running.*

![All pods, including the two demo pods](48_headlamp_pods.png)

*Figure 20. The Pods page, listing every pod in the cluster, among them the two demo pods.*

Finally, the Map in Figure 21 draws the cluster as a picture, grouped by namespace. The system components, from CoreDNS and Calico to Headlamp and the storage provisioner, sit together in `kube-system`, the registry has a namespace of its own, and our `demo` Deployment sits in `default` beside the `kubernetes` Service that leads to the API server. Each card can be expanded to show the objects that belong to it, which makes the Map a good place to return to whenever a listing on the command line becomes hard to read.

![The Map view of the cluster](49_headlamp_map.png)

*Figure 21. The Map view grouped by namespace, with the system components in kube-system, the registry in container-registry, and the demo Deployment in default.*

## 8. When it breaks

Sooner or later a deployment fails, and the first command to run is always `kubectl get pods`, because the status of the pods says which link of the chain has broken. Figure 22 turns that observation into a decision guide.

![Troubleshooting a deployment](M08-Fig5-Troubleshooting.png)

*Figure 22. A decision guide for troubleshooting, which starts from the pod status reported by kubectl get pods and leads to the likely cause and the next command for each status.*

A pod in the state `ImagePullBackOff` could not obtain its image, which nearly always means that the image name or tag in the YAML file does not match what was pushed, or that the push itself failed, so the remedy is to compare the two names character by character and to repeat the `docker push`. A pod in `CrashLoopBackOff` has an image that starts but exits almost at once, and Kubernetes keeps restarting it, waiting longer each time, exactly as Part 2 warned. The reason is in the application's own output, which `kubectl logs` followed by the pod's name displays. A pod that is Running but shows `0/1` in the READY column has a failing readiness probe, and `kubectl describe pod` shows the probe's recent results, which usually point to a wrong path or port. A pod stuck in Pending is waiting for memory or processor time that the node cannot provide, which calls for lower resource requests or, as Part 1 explained, a VM with more resources. Finally, a pod that is Running and `1/1` ready while `curl` on port 30080 is refused points away from the pod and toward the Service, whose selector and ports deserve a second look.

Two problems from earlier in this article belong on the same list, even though they occur before any pod exists. A "permission denied" message that mentions `docker.sock` means that the current login session is not yet in the `docker` group, which a log-out and log-in cures, as section 2.2 explained. A container or application that cannot start because port 8080 is already in use means that something else, usually the application still running in the IDE or a forgotten test container, holds the port, and stopping it solves the problem.

### Learning Activity 2. Release version 2.0

Change the greeting template in `GreetingController` to `"Hi, %s!"`, build the image again with the tag `demo-app:2.0`, push it, and tell the Deployment to use it with the command below.

```bash
kubectl set image deployment/demo demo-app=localhost:32000/cst8277/demo-app:2.0
```

Watch the rolling update with `kubectl rollout status` and in Headlamp, and call the service repeatedly while the update is in progress. Then roll back to the previous version with `kubectl rollout undo deployment/demo`. Describe what you observed, including which greetings the service returned while the update was under way and why.

### Learning Activity 3. Break it and fix it

Introduce one fault at a time into `demo-app.yaml`, apply the file, and record what `kubectl get pods`, `kubectl describe pod`, `kubectl logs`, and Headlamp each show. The first fault is a wrong image tag, the second a wrong path for the readiness probe, and the third a memory limit of `64Mi`. Then fix each fault and confirm that the service answers again, using the decision guide in Figure 22 to explain each symptom.

## 9. What you have built

The VM that began Part 1 as an empty disk now holds a complete, modern development environment, with Ubuntu 26.04 LTS running OpenJDK 25 and Maven, Docker, IntelliJ IDEA, and a MicroK8s 1.36 cluster with its own image registry and Headlamp. More important than the list of tools is the path we walked with them. We generated a project, wrote a REST controller with a record as its response, ran it in the IDE, packaged it with a multi-stage Dockerfile that leaves the compiler behind and runs as an unprivileged user, published the image to a registry, and deployed it declaratively to Kubernetes, where we watched requests spread across two replicas, pods replaced without anyone asking, and readiness probes holding traffic back from a pod that was not yet ready. Each of those behaviors had been described in earlier modules, and each has now been seen on a screen we control.

The same service and the same environment carry the rest of the course. Later modules add security to the service, attach a debugger to it inside the cluster, replace the manual build and push with an automated delivery pipeline, and give it the metrics and traces that make a running system observable. Each of those modules starts from the chain in Figure 1, which is why it was worth walking slowly, one link at a time.

## References

- Docker Inc. (n.d.). *Multi-stage builds*. Retrieved from https://docs.docker.com/build/building/multi-stage/
- JetBrains. (n.d.). *Free educational licenses*. Retrieved from https://www.jetbrains.com/community/education/
- Kubernetes SIGs. (n.d.). *Headlamp documentation*. Retrieved from https://headlamp.dev/docs/latest/
- Spring. (n.d.). *Building a RESTful web service*. Retrieved from https://spring.io/guides/gs/rest-service/
- Spring. (n.d.). *Spring Boot Kubernetes*. Retrieved from https://spring.io/guides/gs/spring-boot-kubernetes/
- Spring. (n.d.). *Spring Initializr*. Retrieved from https://start.spring.io/
