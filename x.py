import groovy.json.JsonSlurper

def deleteStrapiEntry(String apiUrl, String token, String fieldName, String valueToCheck) {
    // 1. Szukamy ID wpisu o podanej nazwie
    // URL wygląda tak: .../api/articles?filters[slug][$eq]=moj-artykul
    def findUrl = "${apiUrl}?filters[${fieldName}][\$eq]=${valueToCheck}"
    
    def findResp = httpRequest url: findUrl,
            customHeaders: [[name: 'Authorization', value: "Bearer ${token}"]]
            
    def json = new JsonSlurper().parseText(findResp.content)

    // Jeśli lista pusta, to znaczy że wpis nie istnieje -> Sukces (nic nie trzeba robić)
    if (json.data.isEmpty()) {
        echo "✅ Obiekt '${valueToCheck}' już nie istnieje. Koniec."
        return
    }

    // 2. Pobieramy ID i usuwamy
    def id = json.data[0].id
    
    httpRequest httpMode: 'DELETE',
            url: "${apiUrl}/${id}",
            customHeaders: [[name: 'Authorization', value: "Bearer ${token}"]],
            validResponseCodes: '200:404' // Ignorujemy błędy jeśli usunięto w międzyczasie

    echo "🗑️ Usunięto obiekt '${valueToCheck}' (ID: ${id})."
}

// --- PRZYKŁAD ---
node {
    stage('Delete') {
        // Usuwamy wpis, którego pole 'slug' to 'moj-stary-post'
        deleteStrapiEntry(
            "http://twoje-strapi/api/articles",
            "TOKEN",
            "slug",             // nazwa pola w Strapi po którym szukasz
            "moj-stary-post"    // wartość pola (nazwa wpisu)
        )
    }
}
