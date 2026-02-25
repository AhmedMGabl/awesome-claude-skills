---
name: kotlin-multiplatform
description: Kotlin Multiplatform patterns covering shared modules, expect/actual declarations, Ktor networking, SQLDelight persistence, Koin DI, and Compose Multiplatform UI.
---

# Kotlin Multiplatform

This skill should be used when sharing code across platforms with Kotlin Multiplatform. It covers shared modules, expect/actual, Ktor, SQLDelight, Koin, and Compose Multiplatform.

## When to Use This Skill

Use this skill when you need to:

- Share business logic between Android, iOS, and desktop
- Use expect/actual declarations for platform-specific code
- Implement networking with Ktor client
- Set up local persistence with SQLDelight
- Build shared UI with Compose Multiplatform

## Project Structure

```
shared/
├── src/
│   ├── commonMain/kotlin/
│   │   ├── data/
│   │   │   ├── repository/
│   │   │   └── remote/
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   └── usecase/
│   │   └── di/
│   ├── androidMain/kotlin/
│   ├── iosMain/kotlin/
│   └── commonTest/kotlin/
├── build.gradle.kts
androidApp/
iosApp/
```

## Gradle Configuration

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    kotlin("plugin.serialization")
    id("com.android.library")
    id("app.cash.sqldelight")
}

kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:2.3.7")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
            implementation("app.cash.sqldelight:coroutines-extensions:2.0.1")
            implementation("io.insert-koin:koin-core:3.5.3")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
        }
        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:2.3.7")
            implementation("app.cash.sqldelight:android-driver:2.0.1")
        }
        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:2.3.7")
            implementation("app.cash.sqldelight:native-driver:2.0.1")
        }
    }
}
```

## Expect/Actual Declarations

```kotlin
// commonMain
expect class PlatformContext

expect fun createDatabaseDriver(context: PlatformContext): SqlDriver

// androidMain
actual typealias PlatformContext = android.content.Context

actual fun createDatabaseDriver(context: PlatformContext): SqlDriver {
    return AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")
}

// iosMain
actual class PlatformContext

actual fun createDatabaseDriver(context: PlatformContext): SqlDriver {
    return NativeSqliteDriver(AppDatabase.Schema, "app.db")
}
```

## Ktor Networking

```kotlin
// commonMain/data/remote/ApiClient.kt
class ApiClient(engine: HttpClientEngine) {
    private val client = HttpClient(engine) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
            })
        }
        install(Logging) { level = LogLevel.INFO }
        defaultRequest {
            url("https://api.example.com/")
            contentType(ContentType.Application.Json)
        }
    }

    suspend fun getItems(): List<Item> =
        client.get("items").body()

    suspend fun getItem(id: String): Item =
        client.get("items/$id").body()

    suspend fun createItem(item: CreateItemRequest): Item =
        client.post("items") { setBody(item) }.body()
}
```

## Repository Pattern

```kotlin
// commonMain/data/repository/ItemRepository.kt
class ItemRepository(
    private val api: ApiClient,
    private val db: AppDatabase,
) {
    fun observeItems(): Flow<List<Item>> =
        db.itemQueries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.Default)

    suspend fun refresh() {
        val items = api.getItems()
        db.transaction {
            db.itemQueries.deleteAll()
            items.forEach { db.itemQueries.insert(it.id, it.title, it.description) }
        }
    }
}
```

## Koin Dependency Injection

```kotlin
// commonMain/di/SharedModule.kt
val sharedModule = module {
    single { ApiClient(get()) }
    single { ItemRepository(get(), get()) }
    factory { GetItemsUseCase(get()) }
}

// androidMain/di/PlatformModule.kt
val androidModule = module {
    single<HttpClientEngine> { OkHttp.create() }
    single { createDatabaseDriver(get()) }
}

// iosMain/di/PlatformModule.kt
val iosModule = module {
    single<HttpClientEngine> { Darwin.create() }
    single { createDatabaseDriver(PlatformContext()) }
}
```

## Compose Multiplatform UI

```kotlin
// commonMain/ui/ItemListScreen.kt
@Composable
fun ItemListScreen(viewModel: ItemListViewModel = koinViewModel()) {
    val items by viewModel.items.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Items") }) }
    ) { padding ->
        if (isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(contentPadding = padding) {
                items(items) { item ->
                    ListItem(
                        headlineContent = { Text(item.title) },
                        supportingContent = { Text(item.description) },
                    )
                }
            }
        }
    }
}
```

## Additional Resources

- KMP Docs: https://kotlinlang.org/docs/multiplatform.html
- Compose Multiplatform: https://www.jetbrains.com/lp/compose-multiplatform/
- KMP Samples: https://kotlinlang.org/docs/multiplatform-samples.html
