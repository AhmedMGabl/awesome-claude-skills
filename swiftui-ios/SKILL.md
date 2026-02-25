---
name: swiftui-ios
description: SwiftUI iOS patterns covering views, modifiers, state management, navigation, data persistence, async/await networking, and App Store deployment.
---

# SwiftUI iOS

This skill should be used when building iOS applications with SwiftUI. It covers views, modifiers, state management, navigation, data persistence, networking, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build iOS apps with SwiftUI declarative UI
- Manage state with @State, @Observable, and @Environment
- Implement navigation with NavigationStack
- Persist data with SwiftData or Core Data
- Make async network requests

## Views and Modifiers

```swift
struct UserProfileView: View {
    let user: User

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            AsyncImage(url: URL(string: user.avatarURL)) { image in
                image.resizable().scaledToFill()
            } placeholder: {
                ProgressView()
            }
            .frame(width: 80, height: 80)
            .clipShape(Circle())

            Text(user.name)
                .font(.title2)
                .fontWeight(.bold)

            Text(user.email)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Label("\(user.postCount) posts", systemImage: "doc.text")
                .font(.caption)
        }
        .padding()
    }
}
```

## State Management

```swift
@Observable
class UserViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    func loadUsers() async {
        isLoading = true
        errorMessage = nil
        do {
            users = try await APIClient.shared.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func deleteUser(_ user: User) async {
        do {
            try await APIClient.shared.deleteUser(user.id)
            users.removeAll { $0.id == user.id }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct UserListView: View {
    @State private var viewModel = UserViewModel()
    @State private var searchText = ""

    var filteredUsers: [User] {
        searchText.isEmpty ? viewModel.users :
            viewModel.users.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        NavigationStack {
            List(filteredUsers) { user in
                NavigationLink(value: user) {
                    UserRowView(user: user)
                }
                .swipeActions {
                    Button("Delete", role: .destructive) {
                        Task { await viewModel.deleteUser(user) }
                    }
                }
            }
            .searchable(text: $searchText)
            .navigationTitle("Users")
            .navigationDestination(for: User.self) { user in
                UserProfileView(user: user)
            }
            .overlay {
                if viewModel.isLoading { ProgressView() }
            }
            .task { await viewModel.loadUsers() }
        }
    }
}
```

## Networking

```swift
struct APIClient {
    static let shared = APIClient()
    private let baseURL = URL(string: "https://api.example.com")!

    func fetchUsers() async throws -> [User] {
        let url = baseURL.appendingPathComponent("users")
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        return try JSONDecoder().decode([User].self, from: data)
    }

    func createUser(_ request: CreateUserRequest) async throws -> User {
        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("users"))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        let (data, _) = try await URLSession.shared.data(for: urlRequest)
        return try JSONDecoder().decode(User.self, from: data)
    }
}
```

## SwiftData Persistence

```swift
@Model
class Task {
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var subtasks: [Subtask]

    init(title: String) {
        self.title = title
        self.isCompleted = false
        self.createdAt = .now
        self.subtasks = []
    }
}

struct TaskListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Task.createdAt, order: .reverse) private var tasks: [Task]

    var body: some View {
        List(tasks) { task in
            HStack {
                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    .onTapGesture { task.isCompleted.toggle() }
                Text(task.title)
            }
        }
        .toolbar {
            Button("Add") {
                context.insert(Task(title: "New Task"))
            }
        }
    }
}
```

## Forms

```swift
struct CreateUserForm: View {
    @State private var name = ""
    @State private var email = ""
    @Environment(\.dismiss) private var dismiss

    var isValid: Bool { !name.isEmpty && email.contains("@") }

    var body: some View {
        Form {
            Section("Details") {
                TextField("Name", text: $name)
                TextField("Email", text: $email)
                    .textInputAutocapitalization(.never)
                    .keyboardType(.emailAddress)
            }
            Section {
                Button("Save") {
                    Task { /* save */ dismiss() }
                }
                .disabled(!isValid)
            }
        }
    }
}
```

## Additional Resources

- SwiftUI: https://developer.apple.com/documentation/swiftui/
- SwiftData: https://developer.apple.com/documentation/swiftdata
- Swift: https://docs.swift.org/swift-book/
