---
name: jetpack-compose
description: Jetpack Compose patterns covering declarative UI, state management, navigation, Material 3, lazy lists, animations, and ViewModel integration for Android.
---

# Jetpack Compose

This skill should be used when building Android UIs with Jetpack Compose. It covers declarative UI, state management, navigation, Material 3, lazy lists, animations, and ViewModel integration.

## When to Use This Skill

Use this skill when you need to:

- Build modern Android UIs with Jetpack Compose
- Manage state with remember, ViewModel, and StateFlow
- Implement Compose Navigation
- Use Material 3 Design components
- Create animations and transitions

## Composable Functions

```kotlin
@Composable
fun ItemListScreen(
    viewModel: ItemListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Items") },
                actions = {
                    IconButton(onClick = viewModel::refresh) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = viewModel::addItem) {
                Icon(Icons.Default.Add, contentDescription = "Add")
            }
        }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> LoadingIndicator(Modifier.padding(padding))
            is UiState.Success -> ItemList(state.items, Modifier.padding(padding))
            is UiState.Error -> ErrorMessage(state.message, viewModel::retry, Modifier.padding(padding))
        }
    }
}

@Composable
private fun ItemList(items: List<Item>, modifier: Modifier = Modifier) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items, key = { it.id }) { item ->
            ItemCard(item = item)
        }
    }
}
```

## State Management

```kotlin
// ViewModel
@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val repository: ItemRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<Item>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Item>>> = _uiState.asStateFlow()

    init { loadItems() }

    fun loadItems() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getItems()
                .catch { e -> _uiState.value = UiState.Error(e.message ?: "Unknown error") }
                .collect { items -> _uiState.value = UiState.Success(items) }
        }
    }

    fun refresh() = loadItems()
    fun retry() = loadItems()

    fun addItem() {
        viewModelScope.launch {
            repository.addItem(Item(title = "New Item"))
        }
    }
}

// State classes
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

## Navigation

```kotlin
// NavGraph
@Composable
fun AppNavGraph(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onItemClick = { id -> navController.navigate("detail/$id") }
            )
        }
        composable(
            route = "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.StringType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId") ?: return@composable
            DetailScreen(
                itemId = itemId,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
```

## Material 3 Theming

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
```

## Animations

```kotlin
@Composable
fun ExpandableCard(title: String, content: String) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .animateContentSize(animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy))
            .clickable { expanded = !expanded }
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                Icon(
                    if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null
                )
            }
            AnimatedVisibility(visible = expanded) {
                Text(content, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = 8.dp))
            }
        }
    }
}
```

## Additional Resources

- Compose Docs: https://developer.android.com/jetpack/compose
- Material 3: https://m3.material.io/develop/android/jetpack-compose
- Compose Samples: https://github.com/android/compose-samples
