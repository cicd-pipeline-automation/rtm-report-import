pipeline {
    agent any

    parameters {
        string(name: 'RTM_PROJECT', defaultValue: 'RTM-DEMO', description: 'RTM Project Key')
        string(name: 'TEST_EXECUTION', defaultValue: 'RD-4', description: 'RTM Test Execution Key')
    }

    environment {
        RTM_API_TOKEN = credentials('rtm-api-token')
        RTM_URL       = 'https://rtm-cloud.herokuapp.com'
        EMAIL_TO      = 'devopsuser8413@gmail.com,ru85206315@gmail.com,ruser3015@gmail.com'
        COMPANY_LOGO  = 'https://your-company.com/logo.png'
        RTM_PROJECT = "${params.RTM_PROJECT}"
        TEST_EXECUTION = "${params.TEST_EXECUTION}"
    }
    
    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Prepare Test Results') {
            steps {
                echo "Copying JUnit XML from tests folder..."
                bat 'powershell -Command "New-Item -ItemType Directory -Force -Path target"'
                bat 'copy tests\\sample_junit_1.xml target\\'
            }
        }

        stage('Generate HTML Report') {
            steps {
                bat """
                    python scripts\\generate_rtm_report.py ^
                        --input target ^
                        --output reports\\rtm-report.html ^
                        --title "RTM Build #${env.BUILD_NUMBER}" ^
                        --test-execution-key "${params.RTM_TEST_EXEC_KEY}"
                """
                archiveArtifacts artifacts: 'reports/rtm-report.html'
            }
        }

        // stage('Import to RTM') {
        //     steps {
        //         script {
        //             bat """
        //                 powershell -Command "Compress-Archive -Path 'target\\*.xml' -DestinationPath 'rtm.zip' -Force"
        //             """

        //             def resp = bat(
        //                 script: """
        //                     curl -s -X POST "${env.RTM_URL}/api/v2/automation/import-test-results" ^
        //                         -H "Authorization: Bearer ${env.RTM_API_TOKEN}" ^
        //                         -F projectKey="${params.RTM_PROJECT_KEY}" ^
        //                         -F testExecutionKey="${params.RTM_TEST_EXEC_KEY}" ^
        //                         -F reportType="JUNIT" ^
        //                         -F file=@rtm.zip
        //                 """,
        //                 returnStdout: true
        //             ).trim()

        //             echo "RTM Response: ${resp}"
        //         }
        //     }
        // }

        stage('Upload RTM Test Results') {
            steps {
                echo "Uploading JUnit test results to RTM..."
                bat(script: '''
                curl -s -X POST "https://rtm-cloud.herokuapp.com/api/v2/automation/import-test-results" ^
                -H "Authorization: Bearer %RTM_API_TOKEN%" ^
                -F projectKey="%RTM_PROJECT%" ^
                -F testExecutionKey="%TEST_EXECUTION%" ^
                -F reportType="JUNIT" ^
                -F jobUrl="%BUILD_URL%" ^
                -F file=@rtm.zip
                ''')
            }
        }

        stage('Email Report') {
            steps {
                emailext(
                    subject: "RTM Test Report - Build #${env.BUILD_NUMBER}",
                    to: "${env.EMAIL_TO}",
                    mimeType: 'text/html',
                    body: """
                        <div style='font-family:Arial;font-size:14px;'>
                            <img src='${env.COMPANY_LOGO}' style='height:45px;'><br><br>

                            <h2>RTM Test Execution Report</h2>

                            <p>RTM Project: <b>${params.RTM_PROJECT_KEY}</b><br>
                            Execution Key: <b>${params.RTM_TEST_EXEC_KEY}</b></p>

                            <p><a href="${env.RTM_URL}/projects/${params.RTM_PROJECT_KEY}/test-executions/${params.RTM_TEST_EXEC_KEY}" target="_blank">
                                Open RTM Execution</a></p>

                            <p><a href="${env.BUILD_URL}artifact/reports/rtm-report.html" target="_blank">
                                View HTML Traffic-Light Report</a></p>

                            <p>Build URL: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>

                            <br>Regards,<br>Automation Team
                        </div>
                    """
                )
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully." }
        failure { echo "Pipeline failed." }
    }
}