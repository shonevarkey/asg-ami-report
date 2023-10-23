pipeline {
    agent any

    environment {
        AWS_CREDENTIALS = credentials('awscredentials') // Use the credentials ID 
        PATH = "/usr/bin/python3:$PATH"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run Script') {
            steps {
                script {
                    sh 'pip install boto3'  
                    sh 'python3 aws_report_script.py'
                    echo "Output files are stored in: ${WORKSPACE}"
                }
            }
        }
    }
}
