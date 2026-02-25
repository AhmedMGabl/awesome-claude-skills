---
name: android-jetpack-compose
description: Jetpack Compose patterns covering composables, state management, navigation, Material 3, Hilt DI, Room database, Retrofit networking, and testing.
---

# Android Jetpack Compose

This skill should be used when building Android applications with Jetpack Compose. It covers composables, state, navigation, Material 3, Hilt, Room, Retrofit, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build Android UIs with Jetpack Compose
- Manage state with ViewModel and StateFlow
- Implement navigation with Compose Navigation
- Use Hilt for dependency injection
- Persist data with Room and network with Retrofit

## Composable Basics

```kotlin
@Composable
fun UserCard(
    user: User,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = null,
                modifier = Modifier.size(48.dp).clip(CircleShape)
            )
            Spacer(Modifier.width(16.dp))
            Column {
                Text(user.name, style = MaterialTheme.typography.titleMedium)
                Text(user.email, style = MaterialTheme.typography.bodySmall,
                     color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}
```

## ViewModel with StateFlow

```kotlin
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserListUiState>(UserListUiState.Loading)
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UserListUiState.Loading
            try {
                val users = userRepository.getUsers()
                _uiState.value = UserListUiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UserListUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UserListUiState {
    data object Loading : UserListUiState
    data class Success(val users: List<User>) : UserListUiState
    data class Error(val message: String) : UserListUiState
}

@Composable
fun UserListScreen(
    viewModel: UserListViewModel = hiltViewModel(),
    onUserClick: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserListUiState.Loading -> Box(
            Modifier.fillMaxSize(), contentAlignment = Alignment.Center
        ) { CircularProgressIndicator() }

        is UserListUiState.Success -> LazyColumn {
            items(state.users, key = { it.id }) { user ->
                UserCard(user = user, onClick = { onUserClick(user.id) })
            }
        }

        is UserListUiState.Error -> Text("Error: ${state.message}")
    }
}
```

## Navigation

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "users") {
        composable("users") {
            UserListScreen(onUserClick = { id ->
                navController.navigate("users/$id")
            })
        }
        composable(
            route = "users/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: return@composable
            UserDetailScreen(userId = userId, onBack = { navController.popBackStack() })
        }
    }
}
```

## Room Database

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): UserEntity?

    @Upsert
    suspend fun upsert(user: UserEntity)

    @Delete
    suspend fun delete(user: UserEntity)
}

@Database(entities = [UserEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

## Retrofit Networking

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<UserDto>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): UserDto
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

## Testing

```kotlin
class UserListViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `loadUsers emits Success state`() = runTest {
        val fakeRepo = FakeUserRepository(listOf(User("1", "Alice", "a@b.com")))
        val viewModel = UserListViewModel(fakeRepo)

        val state = viewModel.uiState.first { it is UserListUiState.Success }
        assertThat((state as UserListUiState.Success).users).hasSize(1)
    }
}

@Test
fun userCard_displaysNameAndEmail() {
    composeTestRule.setContent {
        UserCard(user = User("1", "Alice", "alice@test.com"), onClick = {})
    }
    composeTestRule.onNodeWithText("Alice").assertIsDisplayed()
    composeTestRule.onNodeWithText("alice@test.com").assertIsDisplayed()
}
```

## Additional Resources

- Jetpack Compose: https://developer.android.com/develop/ui/compose
- Architecture: https://developer.android.com/topic/architecture
- Room: https://developer.android.com/training/data-storage/room
