---
name: spring-boot
description: Spring Boot development covering REST APIs, Spring Data JPA, Spring Security with JWT/OAuth2, Spring WebFlux reactive programming, validation, exception handling, caching, scheduling, actuator monitoring, testing with MockMvc, and production deployment patterns.
---

# Spring Boot Development

This skill should be used when building Java/Kotlin applications with Spring Boot. It covers REST APIs, data access, security, reactive programming, and production patterns.

## When to Use This Skill

Use this skill when you need to:

- Build REST APIs with Spring Boot
- Implement data access with Spring Data JPA
- Configure authentication and authorization
- Use reactive programming with WebFlux
- Write integration and unit tests
- Deploy Spring Boot applications

## Project Structure

```
src/
├── main/
│   ├── java/com/example/app/
│   │   ├── Application.java
│   │   ├── config/          # Configuration classes
│   │   ├── controller/      # REST controllers
│   │   ├── service/         # Business logic
│   │   ├── repository/      # Data access
│   │   ├── model/           # Entity classes
│   │   ├── dto/             # Data transfer objects
│   │   ├── exception/       # Custom exceptions
│   │   └── security/        # Security configuration
│   └── resources/
│       ├── application.yml
│       └── db/migration/    # Flyway migrations
└── test/
    └── java/com/example/app/
```

## REST Controller

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping
    public Page<UserResponse> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt,desc") String[] sort) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(
            Sort.Order.by(sort[0]).with(sort.length > 1 ? Sort.Direction.fromString(sort[1]) : Sort.Direction.ASC)
        ));
        return userService.findAll(pageable).map(UserResponse::from);
    }

    @GetMapping("/{id}")
    public UserResponse get(@PathVariable UUID id) {
        return UserResponse.from(userService.findById(id));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse create(@Valid @RequestBody CreateUserRequest request) {
        return UserResponse.from(userService.create(request));
    }

    @PutMapping("/{id}")
    public UserResponse update(@PathVariable UUID id, @Valid @RequestBody UpdateUserRequest request) {
        return UserResponse.from(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable UUID id) {
        userService.delete(id);
    }
}
```

## DTOs with Validation

```java
public record CreateUserRequest(
    @NotBlank @Size(max = 100) String name,
    @NotBlank @Email String email,
    @NotBlank @Size(min = 8, max = 100) String password,
    @NotNull Role role
) {}

public record UpdateUserRequest(
    @Size(max = 100) String name,
    @Email String email
) {}

public record UserResponse(
    UUID id, String name, String email, Role role, Instant createdAt
) {
    public static UserResponse from(User user) {
        return new UserResponse(user.getId(), user.getName(), user.getEmail(),
            user.getRole(), user.getCreatedAt());
    }
}
```

## Entity and Repository

```java
@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role = Role.USER;

    @CreationTimestamp
    private Instant createdAt;

    @UpdateTimestamp
    private Instant updatedAt;
}

public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.role = :role AND u.createdAt > :since")
    Page<User> findByRoleSince(@Param("role") Role role, @Param("since") Instant since, Pageable pageable);
}
```

## Service Layer

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public Page<User> findAll(Pageable pageable) {
        return userRepository.findAll(pageable);
    }

    public User findById(UUID id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));
    }

    @Transactional
    public User create(CreateUserRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new ConflictException("Email already in use");
        }
        User user = new User();
        user.setName(request.name());
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setRole(request.role());
        return userRepository.save(user);
    }

    @Transactional
    public User update(UUID id, UpdateUserRequest request) {
        User user = findById(id);
        if (request.name() != null) user.setName(request.name());
        if (request.email() != null) user.setEmail(request.email());
        return userRepository.save(user);
    }

    @Transactional
    public void delete(UUID id) {
        if (!userRepository.existsById(id)) {
            throw new ResourceNotFoundException("User", id);
        }
        userRepository.deleteById(id);
    }
}
```

## Global Exception Handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(ConflictException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ProblemDetail handleConflict(ConflictException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail detail = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        detail.setTitle("Validation failed");
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
            .forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
        detail.setProperty("errors", errors);
        return detail;
    }
}
```

## Spring Security with JWT

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {
    private final JwtAuthFilter jwtAuthFilter;
    private final UserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/public/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

## application.yml

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate  # Use Flyway for migrations
    open-in-view: false
    properties:
      hibernate:
        default_batch_fetch_size: 16
        order_inserts: true
        order_updates: true
        jdbc:
          batch_size: 50
  flyway:
    enabled: true
    locations: classpath:db/migration
  cache:
    type: redis
    redis:
      time-to-live: 600000

server:
  port: 8080

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
```

## Testing

```java
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class UserControllerTest {
    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;
    @Autowired UserRepository userRepository;

    @Test
    void createUser_returns201() throws Exception {
        var request = new CreateUserRequest("John", "john@example.com", "password123", Role.USER);

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("John"))
            .andExpect(jsonPath("$.email").value("john@example.com"))
            .andExpect(jsonPath("$.id").exists());
    }

    @Test
    void createUser_invalidEmail_returns400() throws Exception {
        var request = new CreateUserRequest("John", "invalid", "password123", Role.USER);

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.email").exists());
    }

    @Test
    void getUser_notFound_returns404() throws Exception {
        mockMvc.perform(get("/api/v1/users/{id}", UUID.randomUUID()))
            .andExpect(status().isNotFound());
    }
}

// Unit test with mocks
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock UserRepository userRepository;
    @Mock PasswordEncoder passwordEncoder;
    @InjectMocks UserService userService;

    @Test
    void findById_throws_whenNotFound() {
        UUID id = UUID.randomUUID();
        when(userRepository.findById(id)).thenReturn(Optional.empty());
        assertThrows(ResourceNotFoundException.class, () -> userService.findById(id));
    }
}
```

## Additional Resources

- Spring Boot Reference: https://docs.spring.io/spring-boot/reference/
- Spring Data JPA: https://docs.spring.io/spring-data/jpa/reference/
- Spring Security: https://docs.spring.io/spring-security/reference/
- Baeldung Tutorials: https://www.baeldung.com/spring-boot
