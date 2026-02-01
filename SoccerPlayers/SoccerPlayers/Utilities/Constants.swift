import Foundation

/// App-wide constants
enum Constants {
    /// Known mononyms - players commonly known by a single name
    /// These are exceptions to the "require first and last name" rule
    static let knownMononyms: Set<String> = [
        // Brazilian legends
        "pele", "ronaldinho", "ronaldo", "kaka", "neymar", "rivaldo", "cafu",
        "robinho", "hulk", "fred", "willian", "firmino", "casemiro", "fabinho",
        "ederson", "alisson", "thiago", "dani", "marcelo", "adriano", "denilson",
        "juninho", "edmundo", "bebeto", "romario", "zico", "socrates", "falcao",
        "garrincha", "jairzinho", "tostao", "rivelino", "dida", "gilberto",
        // Portuguese
        "eusebio", "figo",
        // Other single-name players
        "xavi", "iniesta", "puyol", "isco", "saul", "koke", "morata",
        "coutinho", "vinicius", "rodrygo", "militao", "valverde",
        "chicharito", "ochoa",
        // Goalkeepers often known by single name
        "buffon", "casillas", "neuer", "oblak", "courtois", "lloris"
    ]

    /// Default season for roster viewing
    static var currentSeason: Int {
        let year = Calendar.current.component(.year, from: Date())
        let month = Calendar.current.component(.month, from: Date())
        // If before July, show previous season
        return month < 7 ? year - 1 : year
    }

    /// Target number of players to guess (the "1000" in "1000 Soccer Players")
    static let targetPlayerCount = 1000
}
