---
name: laravel-development
description: Laravel PHP development covering Eloquent ORM, migrations, controllers, routing, Blade templates, middleware, authentication with Sanctum, queues, event broadcasting, testing with Pest, and deployment.
---

# Laravel Development

This skill should be used when building web applications with Laravel. It covers Eloquent models, controllers, authentication, queues, events, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build PHP web applications with Laravel
- Design database schemas with Eloquent ORM
- Implement API authentication with Sanctum
- Set up queues and event broadcasting
- Test Laravel applications with Pest

## Model with Relationships

```php
// app/Models/Post.php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\SoftDeletes;

class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = ['title', 'body', 'published', 'user_id'];

    protected $casts = [
        'published' => 'boolean',
        'published_at' => 'datetime',
    ];

    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    public function tags()
    {
        return $this->belongsToMany(Tag::class);
    }

    public function scopePublished($query)
    {
        return $query->where('published', true);
    }
}
```

## Migration

```php
// database/migrations/2024_01_01_000000_create_posts_table.php
return new class extends Migration {
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('body');
            $table->boolean('published')->default(false);
            $table->timestamp('published_at')->nullable();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->timestamps();
            $table->softDeletes();

            $table->index(['user_id', 'published']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

## Controller

```php
// app/Http/Controllers/PostController.php
namespace App\Http\Controllers;

use App\Models\Post;
use App\Http\Requests\StorePostRequest;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index(Request $request)
    {
        $posts = Post::published()
            ->with('author:id,name')
            ->latest()
            ->paginate(20);

        return view('posts.index', compact('posts'));
    }

    public function store(StorePostRequest $request)
    {
        $post = $request->user()->posts()->create($request->validated());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post created.');
    }

    public function show(Post $post)
    {
        $post->load(['author', 'comments.user', 'tags']);
        return view('posts.show', compact('post'));
    }

    public function update(StorePostRequest $request, Post $post)
    {
        $this->authorize('update', $post);
        $post->update($request->validated());

        return redirect()->route('posts.show', $post)
            ->with('success', 'Post updated.');
    }

    public function destroy(Post $post)
    {
        $this->authorize('delete', $post);
        $post->delete();

        return redirect()->route('posts.index')
            ->with('success', 'Post deleted.');
    }
}
```

## API with Sanctum

```php
// routes/api.php
Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('posts', Api\PostController::class);
    Route::get('/user', fn (Request $request) => $request->user());
});

// app/Http/Controllers/Api/PostController.php
namespace App\Http\Controllers\Api;

use App\Models\Post;
use App\Http\Resources\PostResource;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index()
    {
        return PostResource::collection(
            Post::published()->with('author')->latest()->paginate(20)
        );
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'title' => 'required|string|max:200',
            'body' => 'required|string',
        ]);

        $post = $request->user()->posts()->create($validated);
        return new PostResource($post);
    }
}

// app/Http/Resources/PostResource.php
class PostResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'title' => $this->title,
            'body' => $this->body,
            'author' => $this->whenLoaded('author', fn () => $this->author->name),
            'created_at' => $this->created_at->toISOString(),
        ];
    }
}
```

## Queues and Jobs

```php
// app/Jobs/ProcessImage.php
namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessImage implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $backoff = 60;

    public function __construct(public readonly string $imagePath) {}

    public function handle(): void
    {
        // Process image...
    }
}

// Dispatch
ProcessImage::dispatch($path)->onQueue('images');
ProcessImage::dispatch($path)->delay(now()->addMinutes(5));
```

## Testing with Pest

```php
// tests/Feature/PostTest.php
use App\Models\Post;
use App\Models\User;

test('guests can view published posts', function () {
    $post = Post::factory()->published()->create();

    $this->get(route('posts.show', $post))
        ->assertOk()
        ->assertSee($post->title);
});

test('authenticated users can create posts', function () {
    $user = User::factory()->create();

    $this->actingAs($user)
        ->post(route('posts.store'), [
            'title' => 'My Post',
            'body' => 'Content here',
        ])
        ->assertRedirect();

    $this->assertDatabaseHas('posts', ['title' => 'My Post', 'user_id' => $user->id]);
});

test('guests cannot create posts', function () {
    $this->post(route('posts.store'), ['title' => 'Test', 'body' => 'Test'])
        ->assertRedirect(route('login'));
});
```

## Artisan Commands

```bash
php artisan make:model Post -mfc       # Model + migration + factory + controller
php artisan make:request StorePostRequest
php artisan migrate
php artisan serve
php artisan tinker
php artisan queue:work
php artisan route:list
```

## Additional Resources

- Laravel docs: https://laravel.com/docs
- Pest PHP: https://pestphp.com/
- Laravel Sanctum: https://laravel.com/docs/sanctum
