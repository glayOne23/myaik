import java.math.RoundingMode;

@NonCPS
// format versioning: v{number} | V{number} and latest
def sorted_list(def list,def size_f_sector = [5,5]) {
    def ones = list.find { it == 'latest' }
    def front = list.findAll { it =~ /(?i)^v\d+$|^v\d+(\.0)?(0)?$/ }
    def mid = list.findAll { it =~ /(?i)^v\d+\.[1-9](0)?$/ }
    def last = list.findAll { it =~ /(?i)^v\d+\.\d{2}$/ }
    front.sort { a,b -> b <=> a }
    mid.sort { a,b -> b <=> a }
    last.sort { a,b -> b <=> a }
    def frontest = []
    def midest = []
    if (size_f_sector.size() > 1) {
        frontest = front.take(size_f_sector[0])
        midest = mid.take(size_f_sector[1])
    }
    def new_current_raw = ([ones] + frontest + midest + last + front.findAll { !frontest.contains(it) } + mid.findAll { !midest.contains(it) })
    def new_current = new_current_raw
    if (list.size() != new_current.size()) {
        new_current = list.findAll { !new_current_raw.contains(it) } + new_current_raw
    }
    Collections.reverse(new_current)
    return new_current
}


pipeline {
    agent any
    environment {
        GITLAB_URL = 'gitlab.ums.ac.id'
        PORT_REG = '5050'
        REQUEST_TYPE = "$env.GITLAB_OBJECT_KIND"
        BRANCH = "$env.BRANCH_NAME"
        URL_REPO = "$env.GITLAB_REPO_GIT_SSH_URL"
        IMAGE_NAME = "$env.GITLAB_REPO_NAME"
        // PROJECT_ID = '187'
        PROJECT_ID = "$env.GITLAB_PROJECT_ID"
        USER_NAME = "$env.GITLAB_USER_USERNAME"
        PROJECT_NAME = "$env.GITLAB_PROJECT_PATH_NAMESPACE"
        PASS_REG = '74862f64-4b55-4bf4-b799-551784b488e1'

        TOKEN_PRIV = credentials('7ee60d27-dce4-4bd3-88e5-0e70e0a0a853')

        // API test
        API_TEST_VOL = credentials('07751012-967e-4951-812e-d80eb0f4e3d2')
        FILE_TEST = 'api-test.json'
        FILE_TEST_ENV = 'api-test-env.json'

        MIN_IMAGE = 20

        // LIST_PROPERTY = ['name','']
    }
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('define environment') {
            when {
                allOf {
                    environment(name:'REQUEST_TYPE', value:'push')
                    anyOf {
                        environment(name:'BRANCH', value:'dev')
                        environment(name:'BRANCH', value:'main')
                    }
                }
            }
            steps {
                script {
                    dir("$USER_NAME") {
                        updateGitlabCommitStatus name:'build', state: 'running'
                        checkout scm
                        def commit = sh(returnStdout: true, script: 'git log -1 --oneline').trim()
                        String commitMsg = commit.substring(commit.indexOf(' ')).trim()
                        def tags = []
                        if (fileExists('Dockerfile')) {
                            def response = httpRequest "https://$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories?private_token=$TOKEN_PRIV_PSW&tags=true"
                            int id_data = 0
                            def BigDecimal version = 1.0
                            if (response != null) {
                                def dataResponse = readJSON text: response.getContent()
                                if (dataResponse != null && !dataResponse.isEmpty()) {
                                    id_data = dataResponse[0]['id'] as int
                                    if (dataResponse != null) {
                                        if (dataResponse[0]['tags'] != null && dataResponse[0]['tags'].size() > 0) {
                                            dataResponse[0]['tags'].each {
                                                def ver = it['name'] =~ /(\d+(?:\.\d+)?)/
                                                if (ver.find()) {
                                                    if (BigDecimal.valueOf(Double.valueOf(ver.group(1))).setScale(2, RoundingMode.FLOOR) > version) {
                                                        version = BigDecimal.valueOf(Double.valueOf(ver.group(1))).setScale(2, RoundingMode.FLOOR)
                                                    }
                                                }
                                                tags << it['name']
                                            }
                                            if (commitMsg =~ /--mc/) {
                                                version = version.setScale(0, RoundingMode.FLOOR) + 1.0
                                            } else if (commitMsg =~ /--fc/) {
                                                version = version.setScale(1, RoundingMode.FLOOR) + 0.1
                                            } else {
                                                version = version.add(0.01)
                                            }
                                        }
                                    }

                                    // def tags_test = ["v1.0","v7","latest","v3.01","v8","v2.02","v2.0","v4.0","v5.0","v3.0",
                                    //     "v2.06","v4.01","v3.21","v6","v2.04","v5.01","v5.1","v2.04","v1.05","v1.3","v2.11",
                                    //     "V5.27","v4.5","v4.8","v6.1","v2.3","v4.3","env","version1","version2"]
                                    
                                    // def sorted_dt = sorted_list(tags_test)
                                    // echo "$sorted_dt"

                                    if (tags.size() >= Integer.valueOf(env.MIN_IMAGE)) {
                                        def del_datas = new ArrayList<>(sorted_list(tags).subList(0, tags.size() - Integer.valueOf(env.MIN_IMAGE)))
                                        for (dt_del in del_datas) {
                                            def delete = httpRequest httpMode: 'DELETE',
                                                url: "https://$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories/$id_data/tags/$dt_del?private_token=$TOKEN_PRIV_PSW"
                                            echo "delete success ${delete.getContent()}"
                                        }
                                    }
                                }
                                def image_name = "$GITLAB_URL:$PORT_REG/${env.PROJECT_NAME.replaceAll(' ', '-').toLowerCase()}:v$version"
                                def image_name_latest = "$GITLAB_URL:$PORT_REG/${env.PROJECT_NAME.replaceAll(' ', '-').toLowerCase()}:latest"
                                if (tags.contains('latest')) {
                                    def delete = httpRequest httpMode: 'DELETE',
                                        url: "https://$GITLAB_URL/api/v4/projects/$PROJECT_ID/registry/repositories/$id_data/tags/latest?private_token=$TOKEN_PRIV_PSW"
                                    echo "delete success ${delete.getContent()}"
                                }
                                docker.withRegistry("https://$GITLAB_URL:$PORT_REG", env.PASS_REG) {
                                    def app = docker.build("$image_name")
                                    def app_latest = docker.build("$image_name_latest")
                                    app.push()
                                    app_latest.push()
                                    sh "docker image rm -f $image_name"
                                    sh "docker image rm -f $image_name_latest"
                                }
                            }
                        } else {
                            emailext body: 'Your Dockerfile is missing on your project', to:"$USER_NAME@ums.ac.id", subject:'Dockerfile is Missing'
                            currentBuild.result = 'FAILURE'
                        }
                        // if (commitMsg =~ /--name(?:\s)?([a-zA-Z0-9-]+)/) {

                        // }
                        // if (commitMsg =~ /--name(?:\s)?([a-zA-Z0-9-]+)/) {
                            
                        // }
                        // if (env.BRANCH == 'dev') {
                        //     // deploy
                        //     def server_utama = ''
                        //     // unit test
                        //     if (fileExists(env.FILE_TEST)) {
                        //         def url_origin = commitMsg =~ /--origin-server(?:\s)?([a-zA-Z0-9.@:\/]+)/
                        //         if (url_origin.find()) {
                        //             def server_origin = url_origin.group(1)
                        //             sh "sed 's/${server_origin.replaceAll('/','\\/')}/${server_utama.replaceAll('/','\\/')}/g' $FILE_TEST > $FILE_TEST"
                        //         }
                        //         if (fileExists(env.FILE_TEST_ENV)) {
                        //             sh """
                        //                 docker run -t postman/newman:latest -v $API_TEST_VOL:/collection run /collection/workspace/${IMAGE_NAME.replaceAll(' ', '-').toLowerCase()}_$BRANCH/$USER_NAME/$FILE_TEST \
                        //                 --environment="$FILE_TEST_ENV" -r json --reporter-json-export="/collection/api-results.json"
                        //             """
                        //             def response = readJSON file: 'api-results.json'
                        //             echo "$response"
                        //             // emailext body: output,to:"$EMAIL",subject:'Test Result'
                        //             // docker.image('postman/newman').withRun("-v $API_TEST_VOL:/collection") { c ->
                        //             //     sh "newman /collection/workspace/${IMAGE_NAME.replaceAll(' ','-').toLowerCase()}_$BRANCH/$USER_NAME/$FILE_TEST --environment=\"$FILE_TEST_ENV\" --reporters=\"json,cli\" --reporter-json-export=\"api-results.json\""
                        //         // }
                        //         } else {
                        //             sh """
                        //                 docker run -t postman/newman:latest -v $API_TEST_VOL:/collection run /collection/workspace/${IMAGE_NAME.replaceAll(' ', '-').toLowerCase()}_$BRANCH/$USER_NAME/$FILE_TEST \
                        //                 -r json --reporter-json-export=/collection/api-results.json
                        //             """
                        //             def response = readJSON file: 'api-results.json'
                        //             echo "$response"
                        //         //  emailext body: output,to:"$EMAIL",subject:'Test Result'
                        //         // docker.image('postman/newman').withRun("-v $API_TEST_VOL:/collection") { c ->
                        //         //     sh "newman /collection/workspace/${IMAGE_NAME.replaceAll(' ','-').toLowerCase()}_$BRANCH/$USER_NAME/$FILE_TEST --reporters=\"json,cli\" --reporter-json-export=\"api-results.json\""
                        //         //     def response = readJSON file: "api-results.json"
                        //         //     echo "$response"
                        //         // }
                        //         }
                        //     }
                        // }
                        // else {
                        //     if (commitMsg =~ /deploy/) {
                        //         if (fileExists('docker-compose.yml')) {
                        //             if (commitMsg =~ /priority (1-10)/) {
                        //             }
                        //             else if (commitMsg =~ /scale (1-5)/) {
                        //             }
                        //             else {
                        //             }
                        //         } else {
                        //             emailext body: 'Using "docker-compose.yml" to with use "deploy" is a must only', to:"$EMAIL", subject:'docker-compose.yml is Missing'
                        //         }
                        //     }
                        // }
                    }
                }
            }
        }
        stage('if branch wrong') {
            when {
                not {
                    anyOf {
                        environment(name:'BRANCH', value:'dev')
                        environment(name:'BRANCH', value:'main')
                    }
                }
            }
            steps {
                emailext body: 'Using Branch "dev" or "main" only', to:"$USER_NAME@ums.ac.id", subject:'Wrong Build Environment'

            }
        }
    }

    post {
        always  {
            echo "Build completed. currentBuild.result = ${currentBuild.result}"
        }

        changed {
            echo 'Build result changed'
            script {
                if(currentBuild.result == 'SUCCESS') {
                    echo 'Build has changed to SUCCESS status'
                }
            }
        }

        failure {
            updateGitlabCommitStatus name: 'build', state: 'failed'
            emailext body: "Check out in this URL: ${env.BUILD_URL}", to:"$USER_NAME@ums.ac.id", subject:"Jenkins Build Failed"
        }

        success {
            updateGitlabCommitStatus name:'build', state: 'success'
            echo 'Build was a success'
        }

        unstable {
            updateGitlabCommitStatus name:'build', state: 'skipped'
            emailext body: "Check out in this URL: ${env.BUILD_URL}", to:"$USER_NAME@ums.ac.id", subject:"Image Unstable"
        }
    }
}
