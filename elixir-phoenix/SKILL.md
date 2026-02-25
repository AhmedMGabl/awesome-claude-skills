---
name: elixir-phoenix
description: Elixir Phoenix patterns covering LiveView, Ecto schemas, channels, PubSub, GenServer, supervision trees, authentication, and real-time web applications.
---

# Elixir Phoenix

This skill should be used when building web applications with Elixir and Phoenix. It covers LiveView, Ecto, channels, PubSub, GenServer, supervision, and real-time features.

## When to Use This Skill

Use this skill when you need to:

- Build real-time web apps with Phoenix LiveView
- Use Ecto for database queries and schemas
- Implement WebSocket channels and PubSub
- Create GenServer processes for state management
- Design fault-tolerant supervision trees

## LiveView

```elixir
defmodule MyAppWeb.UserListLive do
  use MyAppWeb, :live_view

  def mount(_params, _session, socket) do
    users = MyApp.Accounts.list_users()
    {:ok, assign(socket, users: users, search: "")}
  end

  def handle_event("search", %{"query" => query}, socket) do
    users = MyApp.Accounts.search_users(query)
    {:noreply, assign(socket, users: users, search: query)}
  end

  def handle_event("delete", %{"id" => id}, socket) do
    MyApp.Accounts.delete_user(id)
    users = MyApp.Accounts.list_users()
    {:noreply, assign(socket, users: users)}
  end

  def render(assigns) do
    ~H"""
    <div>
      <form phx-change="search" phx-submit="search">
        <input type="text" name="query" value={@search} placeholder="Search..." phx-debounce="300" />
      </form>

      <ul>
        <li :for={user <- @users} id={"user-#{user.id}"}>
          <span><%= user.name %></span>
          <button phx-click="delete" phx-value-id={user.id}>Delete</button>
        </li>
      </ul>
    </div>
    """
  end
end
```

## Ecto Schema and Queries

```elixir
defmodule MyApp.Accounts.User do
  use Ecto.Schema
  import Ecto.Changeset

  schema "users" do
    field :name, :string
    field :email, :string
    field :role, Ecto.Enum, values: [:user, :admin, :editor]
    has_many :posts, MyApp.Content.Post
    timestamps()
  end

  def changeset(user, attrs) do
    user
    |> cast(attrs, [:name, :email, :role])
    |> validate_required([:name, :email])
    |> validate_format(:email, ~r/@/)
    |> unique_constraint(:email)
  end
end

defmodule MyApp.Accounts do
  import Ecto.Query
  alias MyApp.Repo
  alias MyApp.Accounts.User

  def list_users do
    User |> order_by(desc: :inserted_at) |> Repo.all()
  end

  def search_users(query) do
    User
    |> where([u], ilike(u.name, ^"%#{query}%"))
    |> order_by(desc: :inserted_at)
    |> Repo.all()
  end

  def create_user(attrs) do
    %User{}
    |> User.changeset(attrs)
    |> Repo.insert()
  end

  def get_user_with_posts(id) do
    User
    |> where(id: ^id)
    |> preload(:posts)
    |> Repo.one()
  end
end
```

## Channels

```elixir
defmodule MyAppWeb.RoomChannel do
  use MyAppWeb, :channel

  def join("room:" <> room_id, _payload, socket) do
    {:ok, assign(socket, :room_id, room_id)}
  end

  def handle_in("new_message", %{"body" => body}, socket) do
    broadcast!(socket, "new_message", %{
      body: body,
      user: socket.assigns.current_user.name,
      timestamp: DateTime.utc_now()
    })
    {:noreply, socket}
  end
end
```

## GenServer

```elixir
defmodule MyApp.RateLimiter do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def check(key), do: GenServer.call(__MODULE__, {:check, key})

  @impl true
  def init(opts) do
    {:ok, %{limits: %{}, max: Keyword.get(opts, :max, 100), window: Keyword.get(opts, :window, 60_000)}}
  end

  @impl true
  def handle_call({:check, key}, _from, state) do
    now = System.monotonic_time(:millisecond)
    {count, timestamps} = Map.get(state.limits, key, {0, []})
    valid = Enum.filter(timestamps, &(&1 > now - state.window))

    if length(valid) < state.max do
      new_limits = Map.put(state.limits, key, {length(valid) + 1, [now | valid]})
      {:reply, :ok, %{state | limits: new_limits}}
    else
      {:reply, {:error, :rate_limited}, state}
    end
  end
end
```

## Migration

```elixir
defmodule MyApp.Repo.Migrations.CreateUsers do
  use Ecto.Migration

  def change do
    create table(:users) do
      add :name, :string, null: false
      add :email, :string, null: false
      add :role, :string, default: "user"
      timestamps()
    end

    create unique_index(:users, [:email])
    create index(:users, [:role])
  end
end
```

## Additional Resources

- Phoenix: https://hexdocs.pm/phoenix/
- LiveView: https://hexdocs.pm/phoenix_live_view/
- Ecto: https://hexdocs.pm/ecto/
