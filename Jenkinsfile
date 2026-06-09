pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'python_docker_app'
        // Define your Docker Hub or ECR credentials ID if you plan to push the image
        // DOCKER_CREDS = credentials('docker-hub-credentials-id')
    }

    stages {
        stage('Checkout') {
            steps {
                // Jenkins usually handles checkout automatically if configured via SCM
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker Image...'
                    sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo 'Running Tests inside Container...'
                    // Example: running django tests
                    sh "docker run --rm ${DOCKER_IMAGE}:${env.BUILD_ID} python manage.py test"
                }
            }
        }

        /* 
        // Uncomment this stage if you have a Docker registry and credentials configured
        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDS}") {
                        docker.image("${DOCKER_IMAGE}").push("${env.BUILD_ID}")
                        docker.image("${DOCKER_IMAGE}").push("latest")
                    }
                }
            }
        }
        */

        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying application using Docker Compose...'
                    // This assumes Jenkins has access to the target deployment environment
                    // and 'docker-compose' is installed.
                    sh "docker-compose up -d"
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
            // Clean up old images to save space
            sh "docker image prune -f"
        }
        success {
            echo 'Pipeline Succeeded!'
        }
        failure {
            echo 'Pipeline Failed!'
        }
    }
}
