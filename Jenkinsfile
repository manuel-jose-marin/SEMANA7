pipeline { 
    agent any
    environment {
        HOME = "${WORKSPACE}"
        GIT_REPO = 'MISW4101-202514-Grupo000'
        GITHUB_TOKEN_ID = '43771338-0057-4a96-ae03-93ee5419d871'
    }
    stages {
        stage('Checkout') { 
            steps {
                git branch: 'develop',  
                    credentialsId: env.GITHUB_TOKEN_ID,
                    url: 'https://github.com/MISW-4101-Practicas/' + env.GIT_REPO
            }
        }
        stage('Gitinspector') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.GITHUB_TOKEN_ID, passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
	                sh 'mkdir -p code-analyzer-report'
	                sh """ curl --request POST --url https://code-analyzer.virtual.uniandes.edu.co/analyze --header "Content-Type: application/json" --data '{"repo_url":"git@github.com:MISW-4101-Practicas/${GIT_REPO}.git", "access_token": "${GIT_PASSWORD}" }' > code-analyzer-report/index.html """   
                }  
	            publishHTML (target: [
	                allowMissing: false,
	                alwaysLinkToLastBuild: false,
	                keepAll: true,
	                reportDir: 'code-analyzer-report',
	                reportFiles: 'index.html',
	                reportName: "GitInspector"
                ])
            }
        }
        stage('Install libraries') {
            steps {
                script {
                    docker.image('python:3.9.12').inside {
                        sh '''
                            pip install --user -r requirements.txt
                        '''
                    }
                }
            }
        }
        stage('Testing') {
            steps {
                script {
                    docker.image('python:3.9.12').inside {
                        sh '''
				python -m unittest discover -s tests -v
                        '''
                    }
                }
            }
        }
        stage('Coverage') {
            steps {
                script {
                    docker.image('python:3.9.12').inside {
                        sh '''
                            python -m coverage run -m unittest discover -s tests -v
                            python -m coverage html
                        ''' 
                    }
                }
            }
        }
        stage('Report') {
            steps {
                publishHTML (target : [allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov/',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report',
                    reportTitles: 'Coverage Report']
                )
            }
        }
    }
    post { 
      always { 
          cleanWs()
          deleteDir() 
          dir("${env.GIT_REPO}@tmp") {
              deleteDir()
	      }
      }
   }
}
