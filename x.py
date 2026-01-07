Oto gotowa, czytelna funkcja do Jenkins Pipeline (Groovy).

Ponieważ domyślne REST API Strapi (v4) nie posiada dedykowanej metody findOrCreate (która sama sprawdza duplikaty i nie zwraca błędu), najlepszym podejściem w Jenkinsie jest:

Wysłanie żądania POST.

Skonfigurowanie Jenkinsa, aby nie przerywał pipeline'u przy kodzie 400.

Ręczne sprawdzenie, czy błąd wynika z duplikatu (np. pole unikalne już istnieje) i "wyciszenie" go.

Wymaga wtyczki HTTP Request Plugin.

code
Groovy
download
content_copy
expand_less
import groovy.json.JsonOutput
import groovy.json.JsonSlurper

def createStrapiEntry(String apiUrl, String token, Map entryData) {
    echo "➡️ Próba utworzenia obiektu w Strapi..."

    // Strapi wymaga, aby dane były owinięte w obiekt "data"
    def payload = JsonOutput.toJson([data: entryData])

    def response = httpRequest httpMode: 'POST',
            url: apiUrl,
            contentType: 'APPLICATION_JSON',
            customHeaders: [[name: 'Authorization', value: "Bearer ${token}"]],
            requestBody: payload,
            // KLUCZOWE: Pozwalamy na kody błędów (400-499), żeby pipeline nie wybuchł od razu
            validResponseCodes: '200:499' 

    if (response.status == 200 || response.status == 201) {
        echo "✅ Sukces: Obiekt został utworzony."
        return
    }

    if (response.status == 400) {
        // Parsujemy błąd, aby upewnić się, że to problem z unikalnością (duplikat)
        def jsonResp = new JsonSlurper().parseText(response.content)
        def errorName = jsonResp?.error?.name
        def errorMessage = jsonResp?.error?.message

        // Strapi przy duplikatach zwraca 'ValidationError' lub komunikat 'must be unique'
        if (errorName == 'ValidationError' || errorMessage?.contains('unique')) {
            echo "ℹ️ Info: Obiekt już istnieje (wykryto duplikat). Nie podejmuję akcji."
            return // Wychodzimy z funkcji bez błędu
        }
    }

    // Jeśli to inny błąd (np. 403 Forbidden, 404, albo 400 z innego powodu), rzucamy błąd
    error "❌ Błąd Strapi API [${response.status}]: ${response.content}"
}

// --- PRZYKŁAD UŻYCIA W PIPELINE ---
node {
    stage('Update CMS') {
        // Dane Twojego obiektu
        def myObject = [
            title: "Mój Artykuł",
            slug: "moj-artykul", // Zakładamy, że to pole jest unikalne w Strapi
            content: "Treść artykułu..."
        ]

        createStrapiEntry(
            "https://twoje-strapi.com/api/articles",
            "TWOJ_TOKEN_BEARER",
            myObject
        )
    }
}
Dlaczego tak to rozwiązałem?

validResponseCodes: '200:499': Domyślnie plugin httpRequest uznaje kod 400 za awarię i zatrzymuje cały build (Failure). Ten parametr mówi Jenkinsowi: "Przyjmij odpowiedź, nawet jak jest błędem, ja sam zdecyduję co z nią zrobić w kodzie".

Obsługa ValidationError: Jeśli obiekt już istnieje (np. pole slug jest zajęte), Strapi zwraca 400 z komunikatem Attribute must be unique. Funkcja to wykrywa i wypisuje Info, zamiast psuć build.

Automatyczne owijanie w data: Funkcja sama robi [data: entryData], więc przekazujesz jej czystą mapę z polami, co jest wygodniejsze w użyciu.
