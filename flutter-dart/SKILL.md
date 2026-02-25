---
name: flutter-dart
description: Flutter and Dart patterns covering widgets, state management, navigation, platform channels, animations, testing, and cross-platform mobile/web/desktop development.
---

# Flutter & Dart

This skill should be used when building cross-platform applications with Flutter and Dart. It covers widgets, state management, navigation, platform channels, animations, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile, web, or desktop apps
- Create custom widgets and layouts
- Manage state with Riverpod, Bloc, or Provider
- Implement navigation and routing
- Write widget and integration tests

## Widget Basics

```dart
class UserCard extends StatelessWidget {
  final String name;
  final String email;
  final VoidCallback? onTap;

  const UserCard({
    super.key,
    required this.name,
    required this.email,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(child: Text(name[0])),
        title: Text(name),
        subtitle: Text(email),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
```

## Stateful Widget

```dart
class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Counter')),
      body: Center(
        child: Text('$_count', style: Theme.of(context).textTheme.headlineLarge),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => setState(() => _count++),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

## Riverpod State Management

```dart
// providers.dart
final usersProvider = FutureProvider<List<User>>((ref) async {
  final api = ref.watch(apiClientProvider);
  return api.getUsers();
});

final selectedUserProvider = StateProvider<User?>((ref) => null);

final filteredUsersProvider = Provider<AsyncValue<List<User>>>((ref) {
  final query = ref.watch(searchQueryProvider);
  final users = ref.watch(usersProvider);
  return users.whenData((list) =>
    list.where((u) => u.name.toLowerCase().contains(query.toLowerCase())).toList()
  );
});

// Usage in widget
class UserListPage extends ConsumerWidget {
  const UserListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final users = ref.watch(filteredUsersProvider);
    return users.when(
      data: (list) => ListView.builder(
        itemCount: list.length,
        itemBuilder: (_, i) => UserCard(
          name: list[i].name,
          email: list[i].email,
          onTap: () => ref.read(selectedUserProvider.notifier).state = list[i],
        ),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(child: Text('Error: $err')),
    );
  }
}
```

## Navigation (GoRouter)

```dart
final router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomePage()),
    GoRoute(
      path: '/users/:id',
      builder: (_, state) => UserDetailPage(id: state.pathParameters['id']!),
    ),
    ShellRoute(
      builder: (_, __, child) => AppShell(child: child),
      routes: [
        GoRoute(path: '/dashboard', builder: (_, __) => const DashboardPage()),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsPage()),
      ],
    ),
  ],
  redirect: (context, state) {
    final isLoggedIn = /* check auth */;
    if (!isLoggedIn) return '/login';
    return null;
  },
);
```

## HTTP Requests (Dio)

```dart
class ApiClient {
  final Dio _dio;

  ApiClient() : _dio = Dio(BaseOptions(
    baseUrl: 'https://api.example.com',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 10),
  ))..interceptors.add(LogInterceptor());

  Future<List<User>> getUsers() async {
    final response = await _dio.get('/users');
    return (response.data as List).map((e) => User.fromJson(e)).toList();
  }

  Future<User> createUser(CreateUserRequest request) async {
    final response = await _dio.post('/users', data: request.toJson());
    return User.fromJson(response.data);
  }
}
```

## Data Models (Freezed)

```dart
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    @Default(false) bool isActive,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

## Testing

```dart
void main() {
  testWidgets('Counter increments', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: CounterPage()));
    expect(find.text('0'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();
    expect(find.text('1'), findsOneWidget);
  });

  test('User model from JSON', () {
    final user = User.fromJson({'id': '1', 'name': 'Alice', 'email': 'a@b.com'});
    expect(user.name, 'Alice');
    expect(user.isActive, false);
  });
}
```

## Additional Resources

- Flutter: https://docs.flutter.dev/
- Dart: https://dart.dev/guides
- Riverpod: https://riverpod.dev/docs/introduction/getting-started
