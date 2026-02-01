// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SoccerPlayers",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "SoccerPlayers",
            targets: ["SoccerPlayers"]),
    ],
    dependencies: [
        .package(url: "https://github.com/groue/GRDB.swift.git", from: "6.24.0")
    ],
    targets: [
        .target(
            name: "SoccerPlayers",
            dependencies: [
                .product(name: "GRDB", package: "GRDB.swift")
            ],
            path: "SoccerPlayers"
        )
    ]
)
