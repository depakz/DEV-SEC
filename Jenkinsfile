// Declarative pipeline: checkout -> lint/test both apps -> security scan ->
// build & scan the Docker image -> validate Terraform -> trigger a Render
// deploy through its API -> wait until live -> smoke test the health endpoint.
//
// Render has Auto-Deploy turned OFF (set in terraform/main.tf), so a deploy
// only happens when this pipeline reaches the "Deploy to Render" stage.
//
// Jenkins credentials expected (Manage Jenkins > Credentials, kind "Secret text"):
//   render-api-key      - Render dashboard > Account Settings > API Keys
//   render-service-id   - `terraform output service_id` (srv-xxxxxxxx)
//   render-service-url  - `terraform output service_url`, e.g. https://devsec.onrender.com
//
// Trigger: GitHub webhook to <jenkins-url>/github-webhook/, or the pollSCM
// fallback below if Jenkins isn't reachable from GitHub.

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

        stage('Build Docker image') {
            steps {
                // One image: React build served by FastAPI (root Dockerfile).
                sh 'docker build -t devsec:${IMAGE_TAG} .'
            }
        }

        stage('Container image scan (Trivy)') {
            steps {
                // Fails the build on HIGH/CRITICAL vulnerabilities that have a fix available.
                sh 'trivy image --exit-code 1 --ignore-unfixed --severity HIGH,CRITICAL devsec:${IMAGE_TAG}'
            }
        }

        stage('Terraform validate') {
            steps {
                dir('terraform') {
                    sh '''
                        terraform init -backend=false -input=false
                        terraform fmt -check -recursive
                        terraform validate
                    '''
                }
            }
        }

        stage('Deploy to Render') {
            steps {
                withCredentials([
                    string(credentialsId: 'render-api-key', variable: 'RENDER_API_KEY'),
                    string(credentialsId: 'render-service-id', variable: 'RENDER_SERVICE_ID')
                ]) {
                    sh '''
                        API="https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"
                        DEPLOY_ID=$(curl -sf -X POST "$API" \
                            -H "Authorization: Bearer $RENDER_API_KEY" \
                            -H "Content-Type: application/json" \
                            -d '{"clearCache":"do_not_clear"}' \
                            | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
                        echo "Triggered Render deploy $DEPLOY_ID"

                        # Poll until Render reports the deploy live (max ~20 min).
                        for i in $(seq 1 80); do
                            STATUS=$(curl -sf "$API/$DEPLOY_ID" \
                                -H "Authorization: Bearer $RENDER_API_KEY" \
                                | python3 -c 'import sys,json; print(json.load(sys.stdin)["status"])')
                            echo "Deploy status: $STATUS"
                            case "$STATUS" in
                                live) exit 0 ;;
                                build_failed|update_failed|canceled|deactivated)
                                    echo "Render deploy failed ($STATUS)"; exit 1 ;;
                            esac
                            sleep 15
                        done
                        echo "Timed out waiting for Render deploy"; exit 1
                    '''
                }
            }
        }

        stage('Verify (smoke test)') {
            steps {
                withCredentials([string(credentialsId: 'render-service-url', variable: 'APP_URL')]) {
                    sh '''
                        # Free instances can take a while to wake up.
                        for i in $(seq 1 12); do
                            curl -sf "$APP_URL/api/health" && exit 0
                            sleep 10
                        done
                        echo "Health check failed after deploy"; exit 1
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Build #${env.BUILD_NUMBER} deployed to Render."
        }
        failure {
            echo "Pipeline failed - check the stage logs above."
        }
    }
}
