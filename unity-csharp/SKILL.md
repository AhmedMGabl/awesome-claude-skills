---
name: unity-csharp
description: Unity game development patterns covering C# scripting, MonoBehaviour lifecycle, physics, input system, UI Toolkit, ScriptableObjects, addressables, and editor extensions.
---

# Unity C#

This skill should be used when developing games with Unity Engine and C#. It covers MonoBehaviour lifecycle, physics, input system, UI Toolkit, ScriptableObjects, addressables, and editor tools.

## When to Use This Skill

Use this skill when you need to:

- Build games with Unity Engine using C#
- Implement gameplay systems and character controllers
- Configure physics, collisions, and raycasting
- Create UI with UI Toolkit or uGUI
- Use ScriptableObjects for data-driven design

## MonoBehaviour Lifecycle

```csharp
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;

    [Header("Ground Check")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundRadius = 0.2f;
    [SerializeField] private LayerMask groundLayer;

    private Rigidbody2D rb;
    private Animator animator;
    private bool isGrounded;
    private float moveInput;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();
    }

    private void Update()
    {
        moveInput = Input.GetAxisRaw("Horizontal");

        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.velocity = new Vector2(rb.velocity.x, jumpForce);
        }

        animator.SetFloat("Speed", Mathf.Abs(moveInput));
        animator.SetBool("IsGrounded", isGrounded);

        if (moveInput != 0)
            transform.localScale = new Vector3(Mathf.Sign(moveInput), 1, 1);
    }

    private void FixedUpdate()
    {
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, groundRadius, groundLayer);
        rb.velocity = new Vector2(moveInput * moveSpeed, rb.velocity.y);
    }
}
```

## New Input System

```csharp
using UnityEngine.InputSystem;

public class PlayerInput : MonoBehaviour
{
    private PlayerControls controls;
    private Vector2 moveInput;

    private void OnEnable()
    {
        controls = new PlayerControls();
        controls.Gameplay.Enable();

        controls.Gameplay.Move.performed += ctx => moveInput = ctx.ReadValue<Vector2>();
        controls.Gameplay.Move.canceled += ctx => moveInput = Vector2.zero;
        controls.Gameplay.Jump.performed += ctx => OnJump();
        controls.Gameplay.Attack.performed += ctx => OnAttack();
    }

    private void OnDisable() => controls.Gameplay.Disable();

    private void OnJump() { /* jump logic */ }
    private void OnAttack() { /* attack logic */ }
}
```

## ScriptableObjects

```csharp
[CreateAssetMenu(fileName = "NewWeapon", menuName = "Game/Weapon Data")]
public class WeaponData : ScriptableObject
{
    public string weaponName;
    public int damage;
    public float attackSpeed;
    public float range;
    public Sprite icon;
    public AudioClip attackSound;
    public GameObject projectilePrefab;
}

// Usage
public class WeaponSystem : MonoBehaviour
{
    [SerializeField] private WeaponData currentWeapon;

    public void Attack()
    {
        Debug.Log($"Attacking with {currentWeapon.weaponName} for {currentWeapon.damage} damage");
    }
}
```

## Object Pooling

```csharp
public class ObjectPool<T> where T : MonoBehaviour
{
    private readonly Queue<T> pool = new();
    private readonly T prefab;
    private readonly Transform parent;

    public ObjectPool(T prefab, int initialSize, Transform parent = null)
    {
        this.prefab = prefab;
        this.parent = parent;

        for (int i = 0; i < initialSize; i++)
        {
            var obj = Object.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }

    public T Get()
    {
        var obj = pool.Count > 0 ? pool.Dequeue() : Object.Instantiate(prefab, parent);
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

## Event System

```csharp
// GameEvents.cs (static event bus)
public static class GameEvents
{
    public static event Action<int> OnScoreChanged;
    public static event Action OnPlayerDied;
    public static event Action<string> OnLevelLoaded;

    public static void ScoreChanged(int newScore) => OnScoreChanged?.Invoke(newScore);
    public static void PlayerDied() => OnPlayerDied?.Invoke();
    public static void LevelLoaded(string levelName) => OnLevelLoaded?.Invoke(levelName);
}

// Usage
public class ScoreUI : MonoBehaviour
{
    private void OnEnable() => GameEvents.OnScoreChanged += UpdateScore;
    private void OnDisable() => GameEvents.OnScoreChanged -= UpdateScore;

    private void UpdateScore(int score)
    {
        GetComponent<TMP_Text>().text = $"Score: {score}";
    }
}
```

## Coroutines and Async

```csharp
private IEnumerator SpawnWave(int enemyCount, float delay)
{
    for (int i = 0; i < enemyCount; i++)
    {
        SpawnEnemy();
        yield return new WaitForSeconds(delay);
    }
    yield return new WaitUntil(() => FindObjectsOfType<Enemy>().Length == 0);
    Debug.Log("Wave cleared!");
}

// Async with UniTask
private async UniTaskVoid LoadLevelAsync(string sceneName)
{
    var operation = SceneManager.LoadSceneAsync(sceneName);
    await operation.ToUniTask(Progress.Create<float>(p => loadingBar.value = p));
}
```

## Additional Resources

- Unity Docs: https://docs.unity3d.com/
- Unity Learn: https://learn.unity.com/
- Scripting Reference: https://docs.unity3d.com/ScriptReference/
