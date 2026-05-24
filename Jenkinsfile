pipeline {
    
    environment{
        DOCKER_IMAGE_NAME = 'todoapp:latest'
        DOCKER_HUB_IMAGE_NAME = 'abishek1710/todoapplicationpython:latest'
    }
    
    agent {
        label 'pythonnode' 
    }
    
    stages{
        stage('Source Checkout'){
            steps {
                git branch: 'main', credentialsId: 'abishekgittokenaws1', url: 'https://github.com/Abishek-DevOps-Engineer/todo_app'
            }
        }
        
        stage('Install Dependencies & Run Tests'){
            steps {
			
				sh '''
					pip install -r requirements.txt --break-system-packages
					pip install pytest --break-system-packages
					python3 -m pytest
				'''

            }
        }
        stage('Build Docker Image'){
            steps {
                sh 'docker build -t $DOCKER_IMAGE_NAME .'
            }
        }
        stage('Push to Docker Hub'){
            steps { 
                
                withCredentials([usernamePassword(credentialsId: 'abishekdockertokenaws1', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
				
					sh '''
						echo "$DOCKER_PASS" | docker login -u $DOCKER_USER --password-stdin
						docker tag $DOCKER_IMAGE_NAME $DOCKER_HUB_IMAGE_NAME
						docker push $DOCKER_HUB_IMAGE_NAME
					
					'''
                }
                      
            }
        }
		stage('Deploy Application'){
		
			agent {
				label 'productionnode'
			
			}
			
			steps {
			
				git branch: 'main', credentialsId: 'abishekgittokenaws1', url: 'https://github.com/Abishek-DevOps-Engineer/todo_app'
			
				withCredentials([string(credentialsId: 'mysqlpasswordabishek', variable: 'MYSQL_ROOT_PASSWORD')]) {
					
					withCredentials([usernamePassword(credentialsId: 'abishekdockertokenaws1', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
					
					sh '''
					
						export MYSQL_PASSWORD=$MYSQL_ROOT_PASSWORD
						export SECRET_KEY=test123
						echo "$DOCKER_PASS" | docker login -u $DOCKER_USER --password-stdin
						docker compose -f docker_compose.yaml down || true
						docker compose -f docker_compose.yaml up -d
					'''

					}
					
				}
			
			}
		
		
		}
    }
	post{
	
		success{
		
			echo 'Success'
		}
		
		failure {
		
			echo 'Failure'
		}
	}
}