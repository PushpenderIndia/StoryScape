pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', credentialsId: 'be931eed-297a-4c57-9706-565d76161ee0', url: 'https://github.com/pushpenderindia/StoryScape'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'sudo apt install python3-pip -y && pip3 install virtualenv'
                    sh '''
                    chmod +x envsetup.sh
                    ./envsetup.sh
                    '''
                    sh 'sudo apt remove chromium-browser -y'
                }
            }
        }

        stage('Install Redis') {
            steps {
                script {
                    sh 'sudo apt install redis-server -y'
                    sh 'sudo systemctl start redis-server'
                    sh 'sudo systemctl enable redis-server'
                    sh 'sudo service redis-server status'

                    sh 'sudo chmod -R 777 /var/lib/jenkins/workspace/StoryScape'
                    sh 'sudo chmod -R 777 /var/lib/jenkins/workspace/StoryScape/*'
                    sh 'sudo chown -R jenkins:www-data /var/lib/jenkins/workspace/StoryScape'
                    sh 'sudo chown -R jenkins:www-data /var/lib/jenkins/workspace/StoryScape/*'
                }
            }
        }

        stage('Install Celery') {
            steps {
                script {
                    sh 'sudo cp -rf DevOps/celery_storyscape.service /etc/systemd/system/'
                    sh 'sudo systemctl daemon-reload'

                    sh 'sudo systemctl stop celery_storyscape.service'
                    sh 'sudo systemctl start celery_storyscape.service'
                    sh 'echo "celery_storyscape.service has started."'

                    sh 'sudo systemctl enable celery_storyscape.service'
                    sh 'echo "celery_storyscape.service has been enabled."'

                    sh 'sudo systemctl status celery_storyscape.service'
                }
            }
        }

        stage('Configure Ngnix') {
            steps {
                script {
                    sh 'sudo cp -rf DevOps/storyscape.conf /etc/nginx/sites-available/storyscape'
                    try {
                        sh 'sudo rm /etc/nginx/sites-enabled/storyscape'
                    } catch (Exception e) {
                        echo "Nginx Config does'nt exist: ${e.message}"
                    }
                    sh 'sudo ln -s /etc/nginx/sites-available/storyscape /etc/nginx/sites-enabled'
                    sh 'sudo nginx -t'
                    sh 'sudo systemctl reload nginx'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'sudo cp -rf DevOps/gunicorn_storyscape.service /etc/systemd/system/'
                    sh 'sudo systemctl daemon-reload'

                    sh 'sudo systemctl start gunicorn_storyscape.service'
                    sh 'echo "Gunicorn has started."'

                    sh 'sudo systemctl enable gunicorn_storyscape.service'
                    sh 'echo "Gunicorn has been enabled."'

                    sh 'sudo systemctl status gunicorn_storyscape.service'
                    sh 'sudo systemctl restart gunicorn_storyscape.service'
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
    }
}