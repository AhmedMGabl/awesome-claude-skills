---
name: android-kotlin
description: Android development with Kotlin covering Jetpack Compose UI, ViewModel with StateFlow, Room database, Retrofit networking, Hilt dependency injection, Navigation Compose, Material 3 theming, coroutines, and modern Android architecture patterns following Google's recommended practices.
---

# Android Kotlin Development

This skill should be used when building Android applications with Kotlin and Jetpack Compose. It covers modern Android architecture, UI composition, data persistence, networking, and dependency injection.

## When to Use This Skill

Use this skill when you need to:

- Build Android UIs with Jetpack Compose
- Implement MVVM architecture with ViewModel
- Handle networking with Retrofit and coroutines
- Persist data with Room database
- Set up dependency injection with Hilt
- Navigate between screens with Navigation Compose

## Jetpack Compose UI

```kotlin
@Composable
fun UserListScreen(
    viewModel: UserListViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Users") }) },
        floatingActionButton = {
            FloatingActionButton(onClick = { viewModel.refresh() }) {
                Icon(Icons.Default.Refresh, contentDescription = "Refresh")
            }
        },
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            is UiState.Success -> {
                LazyColumn(contentPadding = padding) {
                    items(state.users, key = { it.id }) { user ->
                        UserCard(user = user, onClick = { viewModel.onUserClick(user.id) })
                    }
                }
            }
            is UiState.Error -> {
                ErrorMessage(message = state.message, onRetry = { viewModel.refresh() })
            }
        }
    }
}

@Composable
fun UserCard(user: User, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier.size(48.dp).clip(CircleShape),
            )
            Spacer(Modifier.width(12.dp))
            Column {
                Text(user.name, style = MaterialTheme.typography.titleMedium)
                Text(user.email, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
```

## ViewModel with StateFlow

```kotlin
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val userRepository: UserRepository,
) : ViewModel() {

    sealed interface UiState {
        data object Loading : UiState
        data class Success(val users: List<User>) : UiState
        data class Error(val message: String) : UiState
    }

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init { refresh() }

    fun refresh() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            userRepository.getUsers()
                .onSuccess { users -> _uiState.value = UiState.Success(users) }
                .onFailure { e -> _uiState.value = UiState.Error(e.message ?: "Unknown error") }
        }
    }

    fun onUserClick(userId: String) {
        // Navigate to detail
    }
}
```

## Retrofit Networking

```kotlin
// API interface
interface UserApi {
    @GET("users")
    suspend fun getUsers(): List<UserDto>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): UserDto
}

// Repository with Result wrapper
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val userDao: UserDao,
) {
    suspend fun getUsers(): Result<List<User>> = runCatching {
        val remote = api.getUsers()
        val users = remote.map { it.toDomain() }
        userDao.insertAll(users.map { it.toEntity() })  // Cache locally
        users
    }.recoverCatching {
        // Fallback to cached data on network error
        userDao.getAll().map { it.toDomain() }
    }
}

// Hilt module for networking
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .addConverterFactory(MoshiConverterFactory.create())
        .client(OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build())
        .build()

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi = retrofit.create(UserApi::class.java)
}
```

## Room Database

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis(),
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY name ASC")
    fun observeAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users ORDER BY name ASC")
    suspend fun getAll(): List<UserEntity>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): UserEntity?

    @Upsert
    suspend fun insertAll(users: List<UserEntity>)

    @Delete
    suspend fun delete(user: UserEntity)
}

@Database(entities = [UserEntity::class], version = 1, exportSchema = true)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// Hilt module
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

## Navigation Compose

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "users") {
        composable("users") {
            UserListScreen(onUserClick = { userId ->
                navController.navigate("users/$userId")
            })
        }
        composable(
            route = "users/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType }),
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            UserDetailScreen(userId = userId, onBack = { navController.popBackStack() })
        }
    }
}
```

## Additional Resources

- Jetpack Compose: https://developer.android.com/develop/ui/compose
- Android Architecture: https://developer.android.com/topic/architecture
- Hilt: https://dagger.dev/hilt/
- Room: https://developer.android.com/training/data-storage/room
