---
name: php-laravel-livewire
description: Laravel Livewire patterns covering reactive components, form handling, real-time validation, file uploads, polling, Alpine.js integration, and SPA-like interactions.
---

# Laravel Livewire

This skill should be used when building reactive interfaces with Laravel Livewire. It covers components, forms, validation, file uploads, polling, and Alpine.js integration.

## When to Use This Skill

Use this skill when you need to:

- Build reactive components without writing JavaScript
- Handle forms with real-time validation
- Create dynamic interfaces in Laravel
- Implement file uploads and polling
- Integrate with Alpine.js for client-side behavior

## Component Basics

```php
// app/Livewire/UserList.php
<?php

namespace App\Livewire;

use App\Models\User;
use Livewire\Component;
use Livewire\WithPagination;

class UserList extends Component
{
    use WithPagination;

    public string $search = '';
    public string $sortBy = 'name';
    public string $sortDirection = 'asc';

    public function updatedSearch(): void
    {
        $this->resetPage();
    }

    public function sort(string $column): void
    {
        if ($this->sortBy === $column) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortBy = $column;
            $this->sortDirection = 'asc';
        }
    }

    public function render()
    {
        return view('livewire.user-list', [
            'users' => User::query()
                ->when($this->search, fn ($q) => $q->where('name', 'like', "%{$this->search}%"))
                ->orderBy($this->sortBy, $this->sortDirection)
                ->paginate(20),
        ]);
    }
}
```

```blade
{{-- resources/views/livewire/user-list.blade.php --}}
<div>
    <input wire:model.live.debounce.300ms="search" type="text" placeholder="Search users..." />

    <table>
        <thead>
            <tr>
                <th wire:click="sort('name')" class="cursor-pointer">Name</th>
                <th wire:click="sort('email')" class="cursor-pointer">Email</th>
            </tr>
        </thead>
        <tbody>
            @foreach ($users as $user)
                <tr wire:key="{{ $user->id }}">
                    <td>{{ $user->name }}</td>
                    <td>{{ $user->email }}</td>
                </tr>
            @endforeach
        </tbody>
    </table>

    {{ $users->links() }}
</div>
```

## Form Component

```php
class CreateUser extends Component
{
    public string $name = '';
    public string $email = '';
    public string $role = 'user';

    protected function rules(): array
    {
        return [
            'name' => 'required|min:2|max:100',
            'email' => 'required|email|unique:users,email',
            'role' => 'required|in:user,admin,editor',
        ];
    }

    public function updated(string $property): void
    {
        $this->validateOnly($property);
    }

    public function save(): void
    {
        $validated = $this->validate();
        User::create($validated);
        $this->reset();
        $this->dispatch('user-created');
        session()->flash('message', 'User created successfully.');
    }

    public function render()
    {
        return view('livewire.create-user');
    }
}
```

## File Upload

```php
use Livewire\WithFileUploads;

class AvatarUpload extends Component
{
    use WithFileUploads;

    public $photo;

    public function updatedPhoto(): void
    {
        $this->validate(['photo' => 'image|max:2048']);
    }

    public function save(): void
    {
        $path = $this->photo->store('avatars', 'public');
        auth()->user()->update(['avatar' => $path]);
    }

    public function render()
    {
        return view('livewire.avatar-upload');
    }
}
```

## Polling and Events

```php
// Auto-refresh every 5 seconds
// In blade: <div wire:poll.5s>

// Listen for events
#[On('user-created')]
public function refreshList(): void
{
    // Component re-renders automatically
}

// Dispatch browser events
$this->dispatch('notify', message: 'Saved!');
```

## Alpine.js Integration

```blade
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>

    <div x-show="open" x-transition>
        <livewire:user-details :user-id="$userId" />
    </div>
</div>

{{-- Wire and Alpine together --}}
<div x-data="{ count: @entangle('count') }">
    <span x-text="count"></span>
    <button @click="count++">+</button>
</div>
```

## Additional Resources

- Livewire: https://livewire.laravel.com/docs/
- Alpine.js: https://alpinejs.dev/
- Laravel: https://laravel.com/docs/
