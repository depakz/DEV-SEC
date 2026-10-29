// Declarative pipeline: checkout -> lint/test both apps -> security scan ->
// build & push Docker images -> terraform apply (deploys new image tags to
// Azure Container Apps) -> smoke test the live health endpoint.
//
// Jenkins credentials expected (Manage Jenkins > Credentials):
//   azure-sp            (Username/Password, or 4 Secret texts) - the Service
//                        Principal Terraform/az use: ARM_CLIENT_ID,
//                        ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID
//
// Trigger: either a GitHub webhook to <jenkins-url>/github-webhook/, or the
// pollSCM fallback below if Jenkins isn't reachable from GitHub.

pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        TF_IN_AUTOMATION = "true"
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend: install & lint') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --quiet -r requirements.txt
                        pip install --quiet bandit pip-audit
                    '''
                }
            }
        }

        stage('Backend: test') {
            steps {
                dir('backend') {
                    sh '''
                        . .venv/bin/activate
                        pytest -q --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always {
                    junit 'backend/test-results.xml'
                }
            }
        }

        stage('Backend: security scan') {
            steps {
                dir('backend') {
                    sh '''
                        . .venv/bin/activate
                        # Fails the build on medium+ severity findings in our own code.
                        bandit -r app -ll -f txt -o bandit-report.txt
                        # Fails the build on known-vulnerable dependency versions.
                        pip-audit -r requirements.txt
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backend/bandit-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Frontend: install & test') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run lint
                        npm test
                        npm audit --omit=dev
                        npm run build
                    '''
                }
            }
        }

        stage('Build Docker images') {
            steps {
                // The frontend no longer needs the backend URL at build time —
                // it's injected at container start by docker-entrypoint.sh from
                // the BACKEND_URL env var Terraform sets on the Container App.
                sh '''
                    docker build -t backend:${IMAGE_TAG} ./backend
                    docker build -t frontend:${IMAGE_TAG} ./frontend
                '''
            }
        }

        stage('Container image scan (Trivy)') {
            steps {
                sh '''
                    # Fails the build on HIGH/CRITICAL vulnerabilities in either image.
                    trivy image --exit-code 1 --severity HIGH,CRITICAL backend:${IMAGE_TAG}
                    trivy image --exit-code 1 --severity HIGH,CRITICAL frontend:${IMAGE_TAG}
                '''
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'acr-credentials', usernameVariable: 'ACR_USER', passwordVariable: 'ACR_PASS'),
                    string(credentialsId: 'acr-login-server', variable: 'ACR_SERVER')
                ]) {
                    sh '''
                        echo "$ACR_PASS" | docker login "$ACR_SERVER" -u "$ACR_USER" --password-stdin
                        docker tag backend:${IMAGE_TAG} "$ACR_SERVER/backend:${IMAGE_TAG}"
                        docker tag frontend:${IMAGE_TAG} "$ACR_SERVER/frontend:${IMAGE_TAG}"
                        docker push "$ACR_SERVER/backend:${IMAGE_TAG}"
                        docker push "$ACR_SERVER/frontend:${IMAGE_TAG}"
                    '''
                }
            }
        }

        stage('Deploy via Terraform') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'azure-sp', usernameVariable: 'ARM_CLIENT_ID', passwordVariable: 'ARM_CLIENT_SECRET'),
                    string(credentialsId: 'azure-subscription-id', variable: 'ARM_SUBSCRIPTION_ID'),
                    string(credentialsId: 'azure-tenant-id', variable: 'ARM_TENANT_ID')
                ]) {
                    dir('terraform') {
                        sh '''
                            terraform init -input=false
                            terraform apply -input=false -auto-approve \
                                -var="backend_image_tag=${IMAGE_TAG}" \
                                -var="frontend_image_tag=${IMAGE_TAG}"
                            terraform output -raw frontend_url > ../frontend_url.txt
                            terraform output -raw backend_url > ../backend_url.txt
                        '''
                    }
                }
            }
        }

        stage('Verify (smoke test)') {
            steps {
                sh '''
                    BACKEND_URL=$(cat backend_url.txt)
                    sleep 10
                    curl -sf "$BACKEND_URL/api/health" || (echo "Health check failed after deploy" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} deployed. Frontend: ${readFile('frontend_url.txt').trim()}"
        }
        failure {
            echo "Pipeline failed - check the stage logs above."
        }
    }
}
