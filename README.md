# Solace-Distributed-Tracing_Easy-Deployment
A repository based on the Solace distributed tracing and context propagation tutorial seen here (https://codelabs.solace.dev/codelabs/dt-otel/). This repo aims to streamline configuration by automating it with a dockerized python script.

## Setup and Pre-requisites

1. If not already installed:

- Install the latest version of OpenJDK 17 on your device (The following page has a complete catalogue of OpenJDK downloads: <https://www.openlogic.com/openjdk-downloads>)
- Install Docker on your device (you can use the following link for a guide: <https://docs.docker.com/get-docker/>)
- Install the latest version of Maven on your device (The following page has a  catalogue of Maven downloads: <https://maven.apache.org/download.cgi>)

2. Clone this repository or download the .zip file from GitHub (extract the downloaded zip file )

## Dockerized Deployment

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Run the following command: 

    ```
    docker-compose up --build -d
    ```

    Using the `-d` flag will allow us to keep using the same CLI window for later commands.

3. the following 4 containers should now be running:
    - `solace`: The Solace PubSub+ message broker
    - `solace-init`: where a python script runs to set up our solace container to work with Distributed Tracing. This includes configuring the message VPN, a telemetry profile, queues and more.
    * `jaeger-all-in-one`: A Jaeger container to monitor the Solace broker with distributed tracing
    * `otel-collector`: An OpenTelemetry Collector to receive telemetry data from the Solace broker to the Jaeger container

4. After a minute or so, the Solace broker will be ready for use

## Verifying our Solace Container

 The deployed Solace broker can be accessed at <http://localhost:8081>. You will be greeted with  a login page: use the credentials specified in the `solace` service's environment variables, specifically the `username_admin_globalaccesslevel` and the `username_admin_password` fields. Once you are signed in, select the `default` message vpn, then go to Queues and select the `#telemetry-trace` queue: verify the following parameters:

 - Current Consumers: 1
 - Access Type: Non-Exclusive
 - Durable: Yes

## Running Publishing/Subscribing Applications with Context Propagation

At each step of running any application, be sure to check on the Jaeger web interface: it is accessible at <http://localhost:16686/>. You might notice you won't be able to immediately select the solace broker to monitor. Don't panic, the Solace broker will be visible after it is sent a message. Once you have sent a message to your Solace broker, you will be able to select it as a drop-down menu option in the `Service` field of the search form. From there, you will be able to view and filter through all messages received by and consumed by the Solace broker.

This readme will highlight what the result in Jaeger should look like after each publishing or subscribing application is successfully run.

### With Auto-Instrumentation

#### Publisher

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Change directory to `auto-instrumentation/src` with the following command:
    ```
    cd auto-instrumentation/src
    ```

3. Run the following command, making sure to replace `<absolute_path_to_the_repo>` with the absolute path to the cloned repository on your local machine (it appears twice in the command):
    ```
    java -javaagent:"<absolute_path_to_the_repo>/auto-instrumentation/src/opentelemetry-javaagent.jar" \
    -Dotel.javaagent.extensions="<absolute_path_to_the_repo>/solace-opentelemetry-jms-integration-1.1.0.jar" \
    -Dotel.propagators=solace_jms_tracecontext \
    -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
    -Dotel.traces.exporter=otlp \
    -Dotel.metrics.exporter=none \
    -Dotel.instrumentation.jms.enabled=true \
    -Dotel.resource.attributes="service.name=SolaceJMSPublisher" \
    -Dsolace.host=localhost:55554 \
    -Dsolace.vpn=default \
    -Dsolace.user=default \
    -Dsolace.password=default \
    -Dsolace.topic=solace/tracing \
    -jar solace-publisher.jar
    ```
4. Let the application run. Once it has completed, go to the Jaeger web interface: you should see 3 sources, 2 of which are `solace` and `SolaceJMSPublisher`. Select the latter and then click `Find Traces`. You should see a trace that spans both sources called `SolaceJMSPublisher: solace/tracing publish`.

#### Subscriber

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Change directory to `auto-instrumentation/src` with the following command:
    ```
    cd auto-instrumentation/src
    ```

3. Run the following command, making sure to replace `<absolute_path_to_the_repo>` with the absolute path to the cloned repository on your local machine (it appears twice in the command):
    ```
    java -javaagent:"<absolute_path_to_the_repo>/auto-instrumentation/src/opentelemetry-javaagent.jar" \
    -Dotel.javaagent.extensions="<absolute_path_to_the_repo>/solace-opentelemetry-jms-integration-1.1.0.jar" \
    -Dotel.propagators=solace_jms_tracecontext \
    -Dotel.traces.exporter=otlp \
    -Dotel.metrics.exporter=none \
    -Dotel.instrumentation.jms.enabled=true \
    -Dotel.resource.attributes="service.name=SolaceJMSQueueSubscriber" \
    -Dsolace.host=localhost:55554 \
    -Dsolace.vpn=default \
    -Dsolace.user=default \
    -Dsolace.password=default \
    -Dsolace.queue=q \
    -Dsolace.topic=solace/tracing \
    -jar solace-queue-receiver.jar
    ```
4. Let the application run. Once it has completed, go to the Jaeger web interface: you should see 4 sources, 3 of which are `solace`, `SolaceJMSPublisher` and `SolaceJMSQueueSubscriber`. Select the latter and then click `Find Traces`. You should see a trace that spans all 3 sources called `SolaceJMSPublisher: solace/tracing publish`.

### With Manual Instrumentation

The original guide provided by Solace calls specific attention to the original java projects' codebase to highlight the implementation of manually instrumented context propagation. Since this readme will concern itself only with running these applications, you may find these implementation highlights here:

- Publisher: https://codelabs.solace.dev/codelabs/dt-otel/#16
- Subscriber: https://codelabs.solace.dev/codelabs/dt-otel/#17

#### Publisher

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Change directory to `manual-instrumentation/jcsmp-publisher` with the following command:
    ```
    cd manual-instrumentation/jcsmp-publisher
    ```

3. Run the following commands in order: 
    ```
    mvn clean install

    mvn compile

    java -jar target/solace-samples-jcsmp-publisher-manual-instrumentation-1.0-SNAPSHOT.jar tcp://localhost:55554 default default default
    ```

4. When running, the publishing application will send 4 to 5 messages a second. End it once you're satisfied with the output.

5. Once it has completed, go to the Jaeger web interface: you should see a source named `SolaceJCSMPManualOpenTelemetry`. Select it and then click `Find Traces`. You should see a multitude of traces from this source and `solace` called `SolaceJCSMPManualOpenTelemetry: SolaceJCSMPPublisherManualInstrumentation SEND`.

#### Subscriber

1. Using a Command Line Interface of your choosing, change directory to the downloaded/cloned repository

2. Change directory to `manual-instrumentation/jcsmp-publisher` with the following command:
    ```
    cd manual-instrumentation/jcsmp-publisher
    ```

3. Run the following commands in order: 
    ```
    mvn clean install

    mvn compile

    java -jar target/solace-samples-jcsmp-subscriber-manual-instrumentation-1.0-SNAPSHOT.jar tcp://localhost:55554 default default default
    ```

4. When running, the publishing application will send 4 to 5 messages a second. End it once you're satisfied with the output.

5. Once it has completed, go to the Jaeger web interface: you should see a source named `SolaceJCSMPManualOpenTelemetry`. Select it and then click `Find Traces`. You should see a multitude of traces from this source and `solace` called `SolaceJCSMPManualOpenTelemetry: SolaceJCSMPPublisherManualInstrumentation RECEIVE` and `SolaceJCSMPManualOpenTelemetry: SolaceJCSMPPublisherManualInstrumentation PROCESS`.

## Stopping the container

To stop the docker containers, run the following commands: 
```
docker-compose down
```