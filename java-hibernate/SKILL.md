---
name: java-hibernate
description: Hibernate ORM patterns covering entity mapping, relationships, JPQL/Criteria queries, caching, lazy loading, batch operations, and Spring Data JPA integration.
---

# Java Hibernate ORM

This skill should be used when working with Hibernate ORM in Java applications. It covers entity mapping, relationships, queries, caching, lazy loading, and Spring Data JPA.

## When to Use This Skill

Use this skill when you need to:

- Map Java entities to database tables
- Define relationships (OneToMany, ManyToMany)
- Write JPQL and Criteria API queries
- Configure first/second-level caching
- Optimize with batch fetching and lazy loading

## Entity Mapping

```java
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String name;

    @Enumerated(EnumType.STRING)
    private Role role = Role.USER;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Post> posts = new ArrayList<>();

    @ManyToMany
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<RoleEntity> roles = new HashSet<>();
}

@Entity
@Table(name = "posts")
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String content;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;

    @ManyToMany
    @JoinTable(
        name = "post_tags",
        joinColumns = @JoinColumn(name = "post_id"),
        inverseJoinColumns = @JoinColumn(name = "tag_id")
    )
    private Set<Tag> tags = new HashSet<>();

    @Version
    private Long version;
}
```

## Spring Data JPA Repository

```java
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.posts WHERE u.id = :id")
    Optional<User> findByIdWithPosts(@Param("id") Long id);

    @Query("SELECT u FROM User u WHERE u.role = :role ORDER BY u.createdAt DESC")
    Page<User> findByRole(@Param("role") Role role, Pageable pageable);

    @Modifying
    @Query("UPDATE User u SET u.role = :role WHERE u.id = :id")
    int updateRole(@Param("id") Long id, @Param("role") Role role);

    boolean existsByEmail(String email);
}

public interface PostRepository extends JpaRepository<Post, Long> {

    @EntityGraph(attributePaths = {"author", "tags"})
    List<Post> findByAuthorId(Long authorId);

    @Query("""
        SELECT p FROM Post p
        JOIN p.tags t
        WHERE t.name IN :tagNames
        GROUP BY p
        HAVING COUNT(DISTINCT t) = :tagCount
        """)
    List<Post> findByAllTags(@Param("tagNames") List<String> tagNames,
                             @Param("tagCount") long tagCount);
}
```

## Criteria API

```java
public class PostSpecifications {

    public static Specification<Post> hasTitle(String title) {
        return (root, query, cb) ->
            title == null ? null : cb.like(cb.lower(root.get("title")), "%" + title.toLowerCase() + "%");
    }

    public static Specification<Post> hasTag(String tagName) {
        return (root, query, cb) -> {
            Join<Post, Tag> tags = root.join("tags");
            return cb.equal(tags.get("name"), tagName);
        };
    }

    public static Specification<Post> createdAfter(LocalDateTime date) {
        return (root, query, cb) ->
            date == null ? null : cb.greaterThan(root.get("createdAt"), date);
    }
}

// Usage
List<Post> posts = postRepository.findAll(
    hasTitle("spring").and(hasTag("java")).and(createdAfter(lastWeek)),
    PageRequest.of(0, 20, Sort.by("createdAt").descending())
).getContent();
```

## Batch Operations

```java
@Transactional
public void batchInsert(List<UserDto> users) {
    int batchSize = 50;
    for (int i = 0; i < users.size(); i++) {
        entityManager.persist(toEntity(users.get(i)));
        if (i % batchSize == 0) {
            entityManager.flush();
            entityManager.clear();
        }
    }
}
```

```properties
# application.properties
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

## Second-Level Cache

```properties
spring.jpa.properties.hibernate.cache.use_second_level_cache=true
spring.jpa.properties.hibernate.cache.region.factory_class=org.hibernate.cache.jcache.JCacheRegionFactory
spring.jpa.properties.hibernate.javax.cache.provider=org.ehcache.jsr107.EhcacheCachingProvider
```

```java
@Entity
@Cacheable
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Tag {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    private String name;
}
```

## N+1 Prevention

```java
// EntityGraph approach
@EntityGraph(attributePaths = {"author", "tags"})
@Query("SELECT p FROM Post p")
List<Post> findAllWithRelations();

// JOIN FETCH approach
@Query("SELECT DISTINCT p FROM Post p LEFT JOIN FETCH p.tags WHERE p.author.id = :authorId")
List<Post> findByAuthorWithTags(@Param("authorId") Long authorId);

// Batch size approach
@Entity
public class User {
    @OneToMany(mappedBy = "author")
    @BatchSize(size = 25)
    private List<Post> posts;
}
```

## Additional Resources

- Hibernate: https://hibernate.org/orm/documentation/
- Spring Data JPA: https://docs.spring.io/spring-data/jpa/reference/
- JPA Specification: https://jakarta.ee/specifications/persistence/
