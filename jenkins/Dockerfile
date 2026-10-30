# Local Jenkins with every tool the Jenkinsfile calls: python, node, docker
# CLI, trivy, terraform.
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-pip curl unzip ca-certificates gnupg docker-cli \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && curl -fsSL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && curl -fsSL -o /tmp/tf.zip https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip \
    && unzip /tmp/tf.zip -d /usr/local/bin && rm /tmp/tf.zip \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git github credentials-binding junit pipeline-stage-view
