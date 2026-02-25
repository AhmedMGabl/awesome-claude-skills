---
name: kotlin-coroutines
description: Kotlin coroutines patterns covering suspend functions, structured concurrency, Flow, channels, dispatchers, error handling, and testing coroutines.
---

# Kotlin Coroutines

This skill should be used when writing asynchronous code with Kotlin coroutines. It covers suspend functions, structured concurrency, Flow, channels, dispatchers, and testing.

## When to Use This Skill

Use this skill when you need to:

- Write asynchronous code with coroutines
- Use structured concurrency patterns
- Implement reactive streams with Flow
- Handle errors in concurrent operations
- Test coroutine-based code

## Basic Coroutines

```kotlin
import kotlinx.coroutines.*

suspend fun fetchUser(id: String): User {
    return withContext(Dispatchers.IO) {
        userRepository.findById(id) ?: throw NotFoundException("User $id not found")
    }
}

suspend fun fetchUserWithPosts(id: String): UserWithPosts {
    return coroutineScope {
        val user = async { fetchUser(id) }
        val posts = async { fetchPosts(id) }
        UserWithPosts(user.await(), posts.await())
    }
}

fun main() = runBlocking {
    val result = fetchUserWithPosts("123")
    println(result)
}
```

## Structured Concurrency

```kotlin
suspend fun processOrders(orders: List<Order>): List<Result<OrderResult>> {
    return coroutineScope {
        orders.map { order ->
            async {
                runCatching { processOrder(order) }
            }
        }.awaitAll()
    }
}

// SupervisorScope: failure in one child doesn't cancel siblings
suspend fun fetchDashboard(userId: String): Dashboard {
    return supervisorScope {
        val profile = async { fetchProfile(userId) }
        val notifications = async {
            try { fetchNotifications(userId) }
            catch (e: Exception) { emptyList() }
        }
        val recommendations = async {
            try { fetchRecommendations(userId) }
            catch (e: Exception) { emptyList() }
        }
        Dashboard(profile.await(), notifications.await(), recommendations.await())
    }
}
```

## Flow

```kotlin
import kotlinx.coroutines.flow.*

fun observePriceUpdates(symbol: String): Flow<Price> = flow {
    while (true) {
        val price = fetchPrice(symbol)
        emit(price)
        delay(1000)
    }
}

// Operators
val expensiveItems: Flow<Item> = itemsFlow
    .filter { it.price > 100 }
    .map { it.copy(highlighted = true) }
    .distinctUntilChanged()
    .debounce(300)

// Combining flows
val combined: Flow<Pair<User, Settings>> = combine(userFlow, settingsFlow) { user, settings ->
    Pair(user, settings)
}

// StateFlow (hot stream)
class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val user = userRepository.getUser(id)
                _state.value = UiState.Success(user)
            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// SharedFlow (events)
class EventBus {
    private val _events = MutableSharedFlow<Event>(extraBufferCapacity = 64)
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}
```

## Channels

```kotlin
// Producer-consumer pattern
fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    var x = 1
    while (true) {
        send(x++)
        delay(100)
    }
}

// Fan-out: multiple consumers
suspend fun processWithWorkers(items: List<WorkItem>, workerCount: Int) {
    val channel = Channel<WorkItem>(Channel.BUFFERED)

    coroutineScope {
        // Producer
        launch {
            items.forEach { channel.send(it) }
            channel.close()
        }

        // Workers
        repeat(workerCount) { workerId ->
            launch {
                for (item in channel) {
                    println("Worker $workerId processing ${item.id}")
                    processItem(item)
                }
            }
        }
    }
}
```

## Error Handling

```kotlin
// CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, exception ->
    logger.error("Unhandled exception", exception)
}

val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default + handler)

// Retry pattern
suspend fun <T> retry(
    times: Int = 3,
    initialDelay: Long = 100,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong()
        }
    }
    return block()
}

// Usage
val result = retry(times = 3) {
    apiClient.fetchData()
}
```

## Testing

```kotlin
class UserServiceTest {

    @Test
    fun `should fetch user with posts concurrently`() = runTest {
        val userRepo = FakeUserRepository()
        val postRepo = FakePostRepository()
        val service = UserService(userRepo, postRepo)

        val result = service.fetchUserWithPosts("123")

        assertEquals("Alice", result.user.name)
        assertEquals(3, result.posts.size)
        // runTest auto-advances virtual time
    }

    @Test
    fun `should emit flow values`() = runTest {
        val flow = observePriceUpdates("BTC")

        val prices = flow.take(3).toList()

        assertEquals(3, prices.size)
    }

    @Test
    fun `should handle timeout`() = runTest {
        assertFailsWith<TimeoutCancellationException> {
            withTimeout(1000) {
                delay(2000) // Virtual time, completes instantly in test
            }
        }
    }
}
```

## Additional Resources

- Coroutines: https://kotlinlang.org/docs/coroutines-guide.html
- Flow: https://kotlinlang.org/docs/flow.html
- Testing: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/
