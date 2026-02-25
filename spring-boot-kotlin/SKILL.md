---
name: spring-boot-kotlin
description: Spring Boot with Kotlin patterns covering coroutines, WebFlux reactive endpoints, data classes, Spring Data JPA, Spring Security, testing with MockK, and idiomatic Kotlin configuration.
---

# Spring Boot with Kotlin

This skill should be used when building Spring Boot applications in Kotlin. It covers coroutines, reactive endpoints, JPA, security, testing, and idiomatic Kotlin patterns.

## When to Use This Skill

Use this skill when you need to:

- Build REST APIs with Spring Boot and Kotlin
- Use coroutines for async server-side code
- Configure Spring Security with Kotlin DSL
- Write data classes for JPA entities
- Test with MockK and Spring Boot Test

## Basic REST Controller

```kotlin
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/users")
class UserController(private val userService: UserService) {

    @GetMapping
    fun getAll(): List<UserDto> = userService.findAll()

    @GetMapping("/{id}")
    fun getById(@PathVariable id: Long): UserDto =
        userService.findById(id) ?: throw NotFoundException("User not found")

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(@Valid @RequestBody request: CreateUserRequest): UserDto =
        userService.create(request)

    @PutMapping("/{id}")
    fun update(@PathVariable id: Long, @Valid @RequestBody request: UpdateUserRequest): UserDto =
        userService.update(id, request)

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    fun delete(@PathVariable id: Long) = userService.delete(id)
}

data class CreateUserRequest(
    @field:NotBlank val name: String,
    @field:Email val email: String,
    @field:Size(min = 8) val password: String,
)

data class UserDto(
    val id: Long,
    val name: String,
    val email: String,
    val createdAt: Instant,
)
```

## Coroutines Support

```kotlin
import kotlinx.coroutines.flow.Flow
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/api/products")
class ProductController(private val productService: ProductService) {

    @GetMapping
    fun getAll(): Flow<ProductDto> = productService.findAll()

    @GetMapping("/{id}")
    suspend fun getById(@PathVariable id: Long): ProductDto =
        productService.findById(id) ?: throw NotFoundException("Product not found")

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    suspend fun create(@Valid @RequestBody request: CreateProductRequest): ProductDto =
        productService.create(request)
}

@Service
class ProductService(private val repository: ProductRepository) {

    fun findAll(): Flow<ProductDto> =
        repository.findAll().map { it.toDto() }

    suspend fun findById(id: Long): ProductDto? =
        repository.findById(id)?.toDto()

    suspend fun create(request: CreateProductRequest): ProductDto =
        repository.save(request.toEntity()).toDto()
}
```

## JPA Entities

```kotlin
import jakarta.persistence.*

@Entity
@Table(name = "users")
class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    var name: String,

    @Column(nullable = false, unique = true)
    var email: String,

    @Column(nullable = false)
    var passwordHash: String,

    @Enumerated(EnumType.STRING)
    var role: Role = Role.USER,

    @OneToMany(mappedBy = "author", cascade = [CascadeType.ALL])
    val posts: MutableList<Post> = mutableListOf(),

    @Column(nullable = false, updatable = false)
    val createdAt: Instant = Instant.now(),
)

enum class Role { USER, ADMIN, MODERATOR }

interface UserRepository : JpaRepository<User, Long> {
    fun findByEmail(email: String): User?
    fun existsByEmail(email: String): Boolean

    @Query("SELECT u FROM User u WHERE u.role = :role")
    fun findByRole(@Param("role") role: Role): List<User>
}
```

## Spring Security Kotlin DSL

```kotlin
import org.springframework.security.config.annotation.web.invoke

@Configuration
@EnableWebSecurity
class SecurityConfig(private val jwtFilter: JwtAuthFilter) {

    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain {
        http {
            csrf { disable() }
            cors { }
            authorizeHttpRequests {
                authorize("/api/auth/**", permitAll)
                authorize("/api/public/**", permitAll)
                authorize("/api/admin/**", hasRole("ADMIN"))
                authorize(anyRequest, authenticated)
            }
            sessionManagement {
                sessionCreationPolicy = SessionCreationPolicy.STATELESS
            }
            addFilterBefore<UsernamePasswordAuthenticationFilter>(jwtFilter)
        }
        return http.build()
    }

    @Bean
    fun passwordEncoder(): PasswordEncoder = BCryptPasswordEncoder()
}
```

## Testing with MockK

```kotlin
import io.mockk.*
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest

@WebMvcTest(UserController::class)
class UserControllerTest(@Autowired val mockMvc: MockMvc) {

    @MockkBean
    lateinit var userService: UserService

    @Test
    fun `should return user by id`() {
        val user = UserDto(1, "Alice", "alice@test.com", Instant.now())
        every { userService.findById(1) } returns user

        mockMvc.get("/api/users/1")
            .andExpect {
                status { isOk() }
                jsonPath("$.name") { value("Alice") }
                jsonPath("$.email") { value("alice@test.com") }
            }

        verify(exactly = 1) { userService.findById(1) }
    }

    @Test
    fun `should create user`() {
        val request = CreateUserRequest("Bob", "bob@test.com", "password123")
        val created = UserDto(2, "Bob", "bob@test.com", Instant.now())
        every { userService.create(any()) } returns created

        mockMvc.post("/api/users") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(request)
        }.andExpect {
            status { isCreated() }
            jsonPath("$.name") { value("Bob") }
        }
    }
}
```

## Configuration

```kotlin
// application.yml style config as Kotlin
@ConfigurationProperties(prefix = "app")
data class AppProperties(
    val jwt: JwtProperties = JwtProperties(),
    val cors: CorsProperties = CorsProperties(),
)

data class JwtProperties(
    val secret: String = "",
    val expirationMs: Long = 3600000,
)

data class CorsProperties(
    val allowedOrigins: List<String> = listOf("http://localhost:3000"),
)
```

## Additional Resources

- Spring Boot Kotlin: https://spring.io/guides/tutorials/spring-boot-kotlin
- Coroutines support: https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html
- MockK: https://mockk.io/
