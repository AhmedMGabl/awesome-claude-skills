---
name: swiftui-development
description: SwiftUI development for iOS and macOS covering views, modifiers, state management with @Observable, NavigationStack, lists and grids, async/await networking, Combine basics, SwiftData persistence, MVVM architecture, previews, and accessibility. This skill should be used when building native Apple platform applications with SwiftUI.
---

# SwiftUI Development

This skill should be used when the user needs to build, structure, or enhance iOS or macOS applications with SwiftUI. It covers view composition, state management, navigation, networking with async/await, data persistence with SwiftData, MVVM architecture, previews, and accessibility.

## When to Use This Skill

Use this skill when you need to:

- Build SwiftUI views with modifiers and composition
- Manage state with @State, @Binding, @Observable, and @Environment
- Implement navigation with NavigationStack and NavigationSplitView
- Display data in List, LazyVGrid, or LazyHGrid
- Perform network requests with async/await and Task
- Persist data with SwiftData or Core Data
- Structure apps using MVVM architecture
- Write SwiftUI previews for rapid iteration
- Add accessibility modifiers for VoiceOver and Dynamic Type

## Project Structure

```
MyApp/
├── MyApp.swift                  # @main App entry point
├── Models/
│   ├── Item.swift               # SwiftData / domain models
│   └── User.swift
├── ViewModels/
│   ├── ItemListViewModel.swift
│   └── UserViewModel.swift
├── Views/
│   ├── ContentView.swift
│   ├── ItemListView.swift
│   ├── ItemDetailView.swift
│   └── Components/
│       ├── ItemRow.swift
│       └── LoadingOverlay.swift
├── Services/
│   ├── NetworkService.swift
│   └── PersistenceService.swift
├── Utilities/
│   └── Extensions.swift
└── Preview Content/
    └── SampleData.swift
```

## View Composition and Modifiers

### Building Views

```swift
// Views/ItemRow.swift
struct ItemRow: View {
    let title: String
    let subtitle: String
    let iconName: String
    var isFavorite: Bool = false

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: iconName)
                .font(.title2)
                .foregroundStyle(isFavorite ? .yellow : .secondary)
                .frame(width: 32)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            if isFavorite {
                Image(systemName: "star.fill")
                    .foregroundStyle(.yellow)
            }
        }
        .padding(.vertical, 8)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title), \(subtitle)")
        .accessibilityAddTraits(isFavorite ? .isSelected : [])
    }
}
```

### Custom View Modifiers

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .shadow(color: .black.opacity(0.1), radius: 4, y: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// Usage
Text("Hello")
    .cardStyle()
```

## State Management

### @State and @Binding

```swift
struct SettingsView: View {
    @State private var notificationsEnabled = true
    @State private var fontSize: Double = 16

    var body: some View {
        Form {
            Toggle("Enable Notifications", isOn: $notificationsEnabled)
            Slider(value: $fontSize, in: 12...24, step: 1) {
                Text("Font Size: \(Int(fontSize))")
            }
            // Pass binding to child view
            FontPreview(size: $fontSize)
        }
    }
}

struct FontPreview: View {
    @Binding var size: Double

    var body: some View {
        Text("Preview Text")
            .font(.system(size: size))
    }
}
```

### @Observable (Swift 5.9+)

```swift
// ViewModels/ItemListViewModel.swift
import Observation

@Observable
class ItemListViewModel {
    var items: [Item] = []
    var isLoading = false
    var errorMessage: String?
    var searchText = ""

    var filteredItems: [Item] {
        if searchText.isEmpty { return items }
        return items.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }

    private let networkService: NetworkService

    init(networkService: NetworkService = NetworkService()) {
        self.networkService = networkService
    }

    func loadItems() async {
        isLoading = true
        errorMessage = nil

        do {
            items = try await networkService.fetchItems()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func deleteItem(at offsets: IndexSet) {
        items.remove(atOffsets: offsets)
    }

    func toggleFavorite(for item: Item) {
        guard let index = items.firstIndex(where: { $0.id == item.id }) else { return }
        items[index].isFavorite.toggle()
    }
}

// Usage in a view
struct ItemListView: View {
    @State private var viewModel = ItemListViewModel()

    var body: some View {
        List {
            ForEach(viewModel.filteredItems) { item in
                ItemRow(
                    title: item.title,
                    subtitle: item.subtitle,
                    iconName: item.iconName,
                    isFavorite: item.isFavorite
                )
            }
            .onDelete(perform: viewModel.deleteItem)
        }
        .searchable(text: $viewModel.searchText)
        .overlay {
            if viewModel.isLoading {
                ProgressView("Loading...")
            }
        }
        .task {
            await viewModel.loadItems()
        }
    }
}
```

### @Environment

```swift
// Define a custom environment key
struct ThemeKey: EnvironmentKey {
    static let defaultValue = AppTheme.standard
}

extension EnvironmentValues {
    var appTheme: AppTheme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// Inject at the top level
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.appTheme, .standard)
        }
    }
}

// Read anywhere in the hierarchy
struct ThemedButton: View {
    @Environment(\.appTheme) private var theme
    let title: String
    let action: () -> Void

    var body: some View {
        Button(title, action: action)
            .font(theme.buttonFont)
            .foregroundStyle(theme.primaryColor)
    }
}
```

## NavigationStack

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List {
                NavigationLink("Users", value: Route.userList)
                NavigationLink("Settings", value: Route.settings)
            }
            .navigationTitle("Home")
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .userList:
                    UserListView(path: $path)
                case .userDetail(let id):
                    UserDetailView(userId: id)
                case .settings:
                    SettingsView()
                }
            }
        }
    }
}

enum Route: Hashable {
    case userList
    case userDetail(id: String)
    case settings
}

// Programmatic navigation
struct UserListView: View {
    @Binding var path: NavigationPath
    let users: [User] = []

    var body: some View {
        List(users) { user in
            Button {
                path.append(Route.userDetail(id: user.id))
            } label: {
                Text(user.name)
            }
        }
        .navigationTitle("Users")
    }
}
```

## Lists and Grids

### LazyVGrid

```swift
struct PhotoGridView: View {
    let photos: [Photo]
    let columns = [GridItem(.adaptive(minimum: 120), spacing: 8)]

    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 8) {
                ForEach(photos) { photo in
                    AsyncImage(url: photo.thumbnailURL) { image in
                        image
                            .resizable()
                            .scaledToFill()
                    } placeholder: {
                        Rectangle()
                            .fill(.quaternary)
                            .overlay { ProgressView() }
                    }
                    .frame(height: 120)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .accessibilityLabel(photo.description)
                }
            }
            .padding()
        }
    }
}
```

## Async/Await Networking

```swift
// Services/NetworkService.swift
actor NetworkService {
    private let session: URLSession
    private let decoder: JSONDecoder

    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
    }

    func fetchItems() async throws -> [Item] {
        let url = URL(string: "https://api.example.com/items")!
        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.invalidResponse
        }

        return try decoder.decode([Item].self, from: data)
    }

    func createItem(_ item: Item) async throws -> Item {
        var request = URLRequest(url: URL(string: "https://api.example.com/items")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(item)

        let (data, _) = try await session.data(for: request)
        return try decoder.decode(Item.self, from: data)
    }
}

enum NetworkError: LocalizedError {
    case invalidResponse
    case decodingFailed

    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "Server returned an invalid response."
        case .decodingFailed: return "Failed to process server data."
        }
    }
}

// Using Task in views
struct UserDetailView: View {
    let userId: String
    @State private var user: User?
    @State private var errorMessage: String?

    var body: some View {
        Group {
            if let user {
                VStack(alignment: .leading, spacing: 12) {
                    Text(user.name).font(.largeTitle)
                    Text(user.email).foregroundStyle(.secondary)
                }
            } else if let errorMessage {
                ContentUnavailableView("Error", systemImage: "exclamationmark.triangle",
                    description: Text(errorMessage))
            } else {
                ProgressView()
            }
        }
        .task {
            do {
                user = try await NetworkService().fetchUser(id: userId)
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}
```

## SwiftData

```swift
// Models/Item.swift
import SwiftData

@Model
class Item {
    var title: String
    var subtitle: String
    var iconName: String
    var isFavorite: Bool
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var tags: [Tag]

    init(title: String, subtitle: String, iconName: String = "doc",
         isFavorite: Bool = false) {
        self.title = title
        self.subtitle = subtitle
        self.iconName = iconName
        self.isFavorite = isFavorite
        self.createdAt = Date()
        self.tags = []
    }
}

@Model
class Tag {
    var name: String
    var items: [Item]

    init(name: String) {
        self.name = name
        self.items = []
    }
}

// App configuration
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Item.self, Tag.self])
    }
}

// Query and mutate in views
struct ItemListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Item.createdAt, order: .reverse) private var items: [Item]

    var body: some View {
        List {
            ForEach(items) { item in
                ItemRow(title: item.title, subtitle: item.subtitle,
                        iconName: item.iconName, isFavorite: item.isFavorite)
            }
            .onDelete(perform: deleteItems)
        }
        .toolbar {
            Button("Add", systemImage: "plus") {
                let item = Item(title: "New Item", subtitle: "Description")
                modelContext.insert(item)
            }
        }
    }

    private func deleteItems(at offsets: IndexSet) {
        for index in offsets {
            modelContext.delete(items[index])
        }
    }
}
```

## Combine Basics

```swift
import Combine

class SearchViewModel: ObservableObject {
    @Published var query = ""
    @Published var results: [String] = []

    private var cancellables = Set<AnyCancellable>()

    init() {
        $query
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .sink { [weak self] query in
                self?.performSearch(query)
            }
            .store(in: &cancellables)
    }

    private func performSearch(_ query: String) {
        // Execute search logic
    }
}
```

## Previews

```swift
#Preview("Item Row") {
    ItemRow(title: "Meeting Notes", subtitle: "Updated today",
            iconName: "doc.text", isFavorite: true)
    .padding()
}

#Preview("Item List") {
    NavigationStack {
        ItemListView()
    }
    .modelContainer(for: Item.self, inMemory: true)
}

#Preview("Dark Mode") {
    ItemRow(title: "Report", subtitle: "Draft", iconName: "doc")
        .padding()
        .preferredColorScheme(.dark)
}

#Preview("Large Text") {
    ItemRow(title: "Accessible", subtitle: "Dynamic Type", iconName: "textformat.size")
        .padding()
        .environment(\.dynamicTypeSize, .xxxLarge)
}
```

## Accessibility

```swift
struct AccessibleCardView: View {
    let title: String
    let description: String
    let isImportant: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(title).font(.headline)
                    if isImportant {
                        Image(systemName: "exclamationmark.circle.fill")
                            .foregroundStyle(.red)
                    }
                }
                Text(description)
                    .font(.body)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .cardStyle()
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title). \(description)")
        .accessibilityHint("Double tap to open details")
        .accessibilityAddTraits(isImportant ? .isHeader : [])
    }
}
```

## Additional Resources

- SwiftUI docs: https://developer.apple.com/documentation/swiftui
- SwiftData: https://developer.apple.com/documentation/swiftdata
- Swift concurrency: https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency
- Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
