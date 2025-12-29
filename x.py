            } else if (pipelineStatus == "failed" || pipelineStatus == "canceled" || pipelineStatus == "skipped") {

def verifyGitLabStatus(projectId, sha, token) {
    // Pętla będzie trwać, dopóki status to 'running' lub 'pending'
    timeout(time: 10, unit: 'MINUTES') { // Zabezpieczenie przed nieskończonym czekaniem
        waitUntil {
            def cmd = "curl -s --header 'PRIVATE-TOKEN: ${token}' 'https://gitlab.com/api/v4/projects/${projectId}/repository/commits/${sha}/statuses'"
            def response = sh(script: cmd, returnStdout: true).trim()

            if (response.contains('"status":"success"')) {
                echo "GitLab Job zakończony sukcesem!"
                return true 
            } else if (response.contains('"status":"failed"') || response.contains('"status":"canceled"')) {
                error "BŁĄD: Job w GitLab zakończył się statusem: FAILED/CANCELED"
            } else {
                echo "Job wciąż w toku... czekam 15s."
                sleep 15
                return false
            }
        }
    }
}


def getLatestSha(projectId, branch, token) {
    // Zapytanie do API o konkretną gałąź
    def cmd = "curl -s --header 'PRIVATE-TOKEN: ${token}' 'https://gitlab.com/api/v4/projects/${projectId}/repository/branches/${branch}'"
    def response = sh(script: cmd, returnStdout: true).trim()
    
    // Wyciągnięcie SHA (pole "id" wewnątrz obiektu "commit")
    return response.split('"id":"')[1].split('"')[0]
}
