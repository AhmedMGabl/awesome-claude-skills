---
name: swiftui-patterns
description: SwiftUI patterns covering declarative views, state management, navigation, animations, async data loading, and platform-adaptive layouts for iOS, macOS, and watchOS.
---

# SwiftUI Patterns

This skill should be used when building Apple platform apps with SwiftUI. It covers declarative views, state management, navigation, animations, async data, and adaptive layouts.

## When to Use This Skill

Use this skill when you need to:

- Build declarative UIs for iOS, macOS, watchOS, or tvOS
- Manage state with @State, @Binding, @Observable
- Implement NavigationStack and navigation paths
- Create animations and transitions
- Load async data with structured concurrency

## View Composition

```swift
struct ContentView: View {
    @State private var items: [Item] = []
    @State private var searchText = ""
    @State private var isLoading = false

    var filteredItems: [Item] {
        if searchText.isEmpty { return items }
        return items.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView("Loading...")
                } else if filteredItems.isEmpty {
                    ContentUnavailableView.search(text: searchText)
                } else {
                    List(filteredItems) { item in
                        NavigationLink(value: item) {
                            ItemRow(item: item)
                        }
                    }
                }
            }
            .navigationTitle("Items")
            .searchable(text: $searchText)
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
            .task { await loadItems() }
            .refreshable { await loadItems() }
        }
    }

    private func loadItems() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await ApiService.shared.fetchItems()
        } catch {
            // handle error
        }
    }
}
```

## State Management with @Observable

```swift
@Observable
class AppState {
    var user: User?
    var isAuthenticated: Bool { user != nil }
    var notifications: [AppNotification] = []
    var unreadCount: Int { notifications.filter { !$0.isRead }.count }

    func signIn(email: String, password: String) async throws {
        user = try await AuthService.shared.signIn(email: email, password: password)
    }

    func signOut() {
        user = nil
        notifications = []
    }
}

// Usage in view hierarchy
@main
struct MyApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            if appState.isAuthenticated {
                MainTabView()
                    .environment(appState)
            } else {
                LoginView()
                    .environment(appState)
            }
        }
    }
}
```

## Custom Components

```swift
struct CardView<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
            content()
        }
        .padding()
        .background(.regularMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .shadow(radius: 2)
    }
}

// Usage
CardView(title: "Statistics") {
    HStack {
        StatItem(label: "Views", value: "1.2K")
        StatItem(label: "Likes", value: "342")
    }
}
```

## Animations

```swift
struct AnimatedCard: View {
    @State private var isExpanded = false

    var body: some View {
        VStack {
            Text("Card Title")
                .font(.title2)

            if isExpanded {
                Text("Expanded content with additional details")
                    .transition(.asymmetric(
                        insertion: .move(edge: .top).combined(with: .opacity),
                        removal: .scale.combined(with: .opacity)
                    ))
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .onTapGesture {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                isExpanded.toggle()
            }
        }
    }
}
```

## Async Data Loading

```swift
struct UserProfileView: View {
    let userId: String
    @State private var profile: Profile?
    @State private var error: Error?

    var body: some View {
        Group {
            if let profile {
                ProfileContent(profile: profile)
            } else if let error {
                ErrorView(error: error, retryAction: { Task { await load() } })
            } else {
                ProgressView()
            }
        }
        .task(id: userId) { await load() }
    }

    private func load() async {
        do {
            profile = try await ProfileService.shared.fetch(id: userId)
        } catch {
            self.error = error
        }
    }
}
```

## Platform Adaptive Layout

```swift
struct AdaptiveLayout: View {
    @Environment(\.horizontalSizeClass) var sizeClass

    var body: some View {
        if sizeClass == .compact {
            TabView {
                HomeView().tabItem { Label("Home", systemImage: "house") }
                SearchView().tabItem { Label("Search", systemImage: "magnifyingglass") }
                ProfileView().tabItem { Label("Profile", systemImage: "person") }
            }
        } else {
            NavigationSplitView {
                SidebarView()
            } detail: {
                DetailView()
            }
        }
    }
}
```

## Additional Resources

- SwiftUI Docs: https://developer.apple.com/documentation/swiftui
- Tutorials: https://developer.apple.com/tutorials/swiftui
- WWDC Sessions: https://developer.apple.com/videos/swiftui
