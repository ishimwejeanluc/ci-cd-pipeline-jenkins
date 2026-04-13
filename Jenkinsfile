pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
    }

    stages {
        stage('Load .env') {
            steps {
                withCredentials([file(credentialsId: 'app_env_file', variable: 'APP_ENV_FILE')]) {
                    sh 'cp "$APP_ENV_FILE" .env && chmod 600 .env'
                    script {
                        def props = readProperties file: '.env'
                        def requiredKeys = [
                            'DOCKER_HUB_USER',
                            'DOCKER_HUB_PASSWORD',
                            'DOCKER_HUB_REPO',
                            'EC2_PUBLIC_IP',
                            'DB_HOST',
                            'DB_PORT',
                            'DB_NAME',
                            'DB_USER',
                            'DB_PASSWORD'
                        ]

                        def missingKeys = requiredKeys.findAll { key -> !props[key]?.trim() }
                        if (missingKeys) {
                            error("Missing required .env values: ${missingKeys.join(', ')}")
                        }

                        props.each { key, value ->
                            env."${key}" = value?.toString()?.trim()
                        }

                        env.DOCKER_USERNAME = env.DOCKER_HUB_USER
                        env.DOCKER_PASSWORD = env.DOCKER_HUB_PASSWORD
                        env.DOCKER_IMAGE = "${env.DOCKER_USERNAME}/${env.DOCKER_HUB_REPO}"
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    bash -lc '
                      python3 -m venv venv
                      source venv/bin/activate
                      pip install -r web/requirements.txt
                    '
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building the docker image...'
                sh 'docker build -t $DOCKER_IMAGE:latest -f web/Dockerfile web'
            }
        }

        stage('Push Image') {
            steps {
                echo 'Pushing the docker image...'
                sh 'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin'
                sh 'docker push $DOCKER_IMAGE:latest'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying with Ansible...'
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'ec2_ssh', keyFileVariable: 'ANSIBLE_SSH_KEY', usernameVariable: 'ANSIBLE_SSH_USER')
                ]) {
                    sh '''
                         ansible-playbook -i "$EC2_PUBLIC_IP," -u "$ANSIBLE_SSH_USER" --private-key "$ANSIBLE_SSH_KEY" ansible/main.yml \
                          -e "docker_username=$DOCKER_USERNAME" \
                          -e "docker_password=$DOCKER_PASSWORD" \
                          -e "web_image=$DOCKER_IMAGE:latest" \
                          -e "db_host=$DB_HOST" \
                          -e "db_port=$DB_PORT" \
                          -e "db_name=$DB_NAME" \
                          -e "db_user=$DB_USER" \
                          -e "db_password=$DB_PASSWORD"
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up old images...'
                sh 'docker image prune -f || true'
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed. Check logs for details."
        }
    }
}
