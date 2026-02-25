---
name: flutter-development
description: Flutter mobile and web development covering Dart fundamentals, widgets, state management (Riverpod/Bloc), navigation (GoRouter), animations, platform channels, Firebase integration, testing, and production deployment to iOS and Android.
---

# Flutter Development

This skill should be used when building cross-platform mobile or web applications with Flutter. It covers Dart language, widget system, state management, navigation, animations, platform integration, and deployment patterns.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile apps (iOS + Android)
- Implement complex UI with Flutter widgets
- Manage state with Riverpod, Bloc, or Provider
- Handle navigation with GoRouter
- Integrate native platform features
- Connect to Firebase or REST APIs
- Test Flutter apps (unit, widget, integration)
- Deploy to App Store and Google Play

## Project Setup

```bash
# Create new project
flutter create --org com.example --platforms ios,android,web my_app
cd my_app

# Project structure
lib/
├── main.dart
├── app.dart                    # MaterialApp/router setup
├── core/
│   ├── constants/
│   ├── theme/
│   │   └── app_theme.dart
│   ├── utils/
│   └── extensions/
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── repositories/
│   │   │   └── models/
│   │   ├── domain/
│   │   └── presentation/
│   │       ├── screens/
│   │       ├── widgets/
│   │       └── providers/
│   └── home/
├── shared/
│   ├── widgets/
│   └── providers/
└── routing/
    └── app_router.dart
```

### pubspec.yaml

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.5.0
  go_router: ^14.0.0
  dio: ^5.4.0
  freezed_annotation: ^2.4.0
  json_annotation: ^4.9.0
  shared_preferences: ^2.2.0
  cached_network_image: ^3.3.0
  flutter_animate: ^4.5.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.0
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  mocktail: ^1.0.0
  flutter_lints: ^4.0.0
```

## Dart Fundamentals

```dart
// Null safety
String? nullableName;
String name = nullableName ?? "default";
int length = nullableName?.length ?? 0;
String forced = nullableName!; // Throws if null

// Records (Dart 3.0+)
(String, int) userInfo = ("Alice", 30);
({String name, int age}) namedRecord = (name: "Alice", age: 30);

// Pattern matching (Dart 3.0+)
String describe(Object obj) => switch (obj) {
  int n when n > 0 => "positive: $n",
  int n => "non-positive: $n",
  String s => "string: $s",
  (int x, int y) => "point: ($x, $y)",
  _ => "unknown",
};

// Sealed classes (exhaustive pattern matching)
sealed class AuthState {}
class Authenticated extends AuthState {
  final String userId;
  Authenticated(this.userId);
}
class Unauthenticated extends AuthState {}
class Loading extends AuthState {}

Widget buildUI(AuthState state) => switch (state) {
  Authenticated(:final userId) => Text("Welcome $userId"),
  Unauthenticated() => const LoginScreen(),
  Loading() => const CircularProgressIndicator(),
};

// Extension methods
extension StringX on String {
  String get capitalize => "${this[0].toUpperCase()}${substring(1)}";
  bool get isEmail => RegExp(r'^[\w-.]+@[\w-]+\.\w+$').hasMatch(this);
}
```

## Widgets and UI

### Stateless and Stateful Widgets

```dart
// Stateless widget
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
    final theme = Theme.of(context);
    return Card(
      child: ListTile(
        leading: CircleAvatar(child: Text(name[0])),
        title: Text(name, style: theme.textTheme.titleMedium),
        subtitle: Text(email),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}

// Stateful widget with lifecycle
class CounterWidget extends StatefulWidget {
  const CounterWidget({super.key});

  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _count = 0;

  @override
  void initState() {
    super.initState();
    // Initialize resources
  }

  @override
  void dispose() {
    // Clean up controllers, streams, etc.
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text("Count: $_count", style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: () => setState(() => _count++),
          child: const Text("Increment"),
        ),
      ],
    );
  }
}
```

### Common Layouts

```dart
// Responsive layout
class ResponsiveLayout extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > 900) {
          return Row(
            children: [
              SizedBox(width: 280, child: SideMenu()),
              Expanded(child: MainContent()),
            ],
          );
        }
        return MainContent(); // Mobile: full width
      },
    );
  }
}

// Scrollable list with pull-to-refresh
class UserListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Users")),
      body: RefreshIndicator(
        onRefresh: () async { /* refresh data */ },
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: users.length,
          itemBuilder: (context, index) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: UserCard(
              name: users[index].name,
              email: users[index].email,
            ),
          ),
        ),
      ),
    );
  }
}

// Form with validation
class LoginForm extends StatefulWidget {
  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(labelText: "Email"),
            validator: (v) => v != null && v.isEmail ? null : "Invalid email",
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            obscureText: true,
            decoration: const InputDecoration(labelText: "Password"),
            validator: (v) => v != null && v.length >= 8 ? null : "Min 8 characters",
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                // Submit
              }
            },
            child: const Text("Login"),
          ),
        ],
      ),
    );
  }
}
```

## State Management with Riverpod

```dart
// providers.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Simple state provider
final counterProvider = StateProvider<int>((ref) => 0);

// Async data provider
final usersProvider = FutureProvider<List<User>>((ref) async {
  final api = ref.watch(apiClientProvider);
  return api.getUsers();
});

// Notifier (complex state)
final authProvider = NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() => Unauthenticated();

  Future<void> login(String email, String password) async {
    state = Loading();
    try {
      final token = await ref.read(authRepoProvider).login(email, password);
      state = Authenticated(token.userId);
    } catch (e) {
      state = Unauthenticated();
      throw Exception("Login failed: $e");
    }
  }

  Future<void> logout() async {
    await ref.read(authRepoProvider).logout();
    state = Unauthenticated();
  }
}

// Usage in widget
class HomeScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final usersAsync = ref.watch(usersProvider);

    return switch (authState) {
      Authenticated(:final userId) => usersAsync.when(
        data: (users) => UserListView(users: users),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text("Error: $err")),
      ),
      Unauthenticated() => const LoginScreen(),
      Loading() => const Center(child: CircularProgressIndicator()),
    };
  }
}
```

## Navigation with GoRouter

```dart
// routing/app_router.dart
import 'package:go_router/go_router.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: "/",
    redirect: (context, state) {
      final isLoggedIn = authState is Authenticated;
      final isOnLogin = state.matchedLocation == "/login";

      if (!isLoggedIn && !isOnLogin) return "/login";
      if (isLoggedIn && isOnLogin) return "/";
      return null;
    },
    routes: [
      ShellRoute(
        builder: (context, state, child) => ScaffoldWithNavBar(child: child),
        routes: [
          GoRoute(
            path: "/",
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: "/users/:id",
            builder: (context, state) {
              final id = state.pathParameters["id"]!;
              return UserDetailScreen(userId: id);
            },
          ),
          GoRoute(
            path: "/settings",
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),
      GoRoute(
        path: "/login",
        builder: (context, state) => const LoginScreen(),
      ),
    ],
  );
});

// Navigate
context.go("/users/123");         // Replace current route
context.push("/users/123");       // Push onto stack
context.pop();                     // Go back
```

## Data Layer

### Freezed Models

```dart
// models/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    @Default("user") String role,
    DateTime? createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// Run: dart run build_runner build
```

### API Client with Dio

```dart
// data/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  final Dio _dio;

  ApiClient(String baseUrl, {String? token})
      : _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 10),
          headers: {
            if (token != null) "Authorization": "Bearer $token",
            "Content-Type": "application/json",
          },
        ));

  Future<List<User>> getUsers() async {
    final response = await _dio.get("/users");
    return (response.data as List).map((j) => User.fromJson(j)).toList();
  }

  Future<User> createUser(Map<String, dynamic> data) async {
    final response = await _dio.post("/users", data: data);
    return User.fromJson(response.data);
  }
}
```

## Theming

```dart
// core/theme/app_theme.dart
class AppTheme {
  static ThemeData light() => ThemeData(
    useMaterial3: true,
    colorSchemeSeed: const Color(0xFF3B82F6),
    brightness: Brightness.light,
    textTheme: GoogleFonts.interTextTheme(),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      filled: true,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size(double.infinity, 48),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
  );

  static ThemeData dark() => ThemeData(
    useMaterial3: true,
    colorSchemeSeed: const Color(0xFF3B82F6),
    brightness: Brightness.dark,
    textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
  );
}
```

## Testing

```dart
// test/auth_notifier_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthRepo extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepo mockRepo;
  late ProviderContainer container;

  setUp(() {
    mockRepo = MockAuthRepo();
    container = ProviderContainer(overrides: [
      authRepoProvider.overrideWithValue(mockRepo),
    ]);
  });

  tearDown(() => container.dispose());

  test("login success updates state to Authenticated", () async {
    when(() => mockRepo.login(any(), any()))
        .thenAnswer((_) async => Token(userId: "123"));

    final notifier = container.read(authProvider.notifier);
    await notifier.login("test@test.com", "password");

    final state = container.read(authProvider);
    expect(state, isA<Authenticated>());
    expect((state as Authenticated).userId, "123");
  });

  // Widget test
  testWidgets("UserCard displays name and email", (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: UserCard(name: "Alice", email: "alice@test.com"),
        ),
      ),
    );

    expect(find.text("Alice"), findsOneWidget);
    expect(find.text("alice@test.com"), findsOneWidget);
  });
}
```

## Additional Resources

- Flutter docs: https://docs.flutter.dev/
- Dart language: https://dart.dev/guides
- Riverpod: https://riverpod.dev/
- GoRouter: https://pub.dev/packages/go_router
- Freezed: https://pub.dev/packages/freezed
- Flutter cookbook: https://docs.flutter.dev/cookbook
