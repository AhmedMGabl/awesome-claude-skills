---
name: zeego-menus
description: Zeego cross-platform menu patterns covering dropdown menus, context menus, menu items with icons, checkboxes, submenus, and native iOS/Android menu rendering with React Native and Expo.
---

# Zeego Menus

This skill should be used when building native menus in React Native with Zeego. It covers dropdown menus, context menus, items, checkboxes, submenus, and platform-native rendering.

## When to Use This Skill

Use this skill when you need to:

- Add native dropdown menus to React Native apps
- Build context menus with long-press triggers
- Create menu items with icons and checkboxes
- Support nested submenus
- Render platform-native menus on iOS and Android

## Setup

```bash
npx expo install zeego
```

## Dropdown Menu

```tsx
import * as DropdownMenu from "zeego/dropdown-menu";

function UserMenu() {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <TouchableOpacity style={styles.trigger}>
          <Text>Options</Text>
          <ChevronDown size={16} />
        </TouchableOpacity>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content>
        <DropdownMenu.Item key="profile" onSelect={() => navigateTo("profile")}>
          <DropdownMenu.ItemIcon ios={{ name: "person.circle" }}>
            <UserIcon size={16} />
          </DropdownMenu.ItemIcon>
          <DropdownMenu.ItemTitle>Profile</DropdownMenu.ItemTitle>
        </DropdownMenu.Item>

        <DropdownMenu.Item key="settings" onSelect={() => navigateTo("settings")}>
          <DropdownMenu.ItemIcon ios={{ name: "gear" }}>
            <SettingsIcon size={16} />
          </DropdownMenu.ItemIcon>
          <DropdownMenu.ItemTitle>Settings</DropdownMenu.ItemTitle>
        </DropdownMenu.Item>

        <DropdownMenu.Separator />

        <DropdownMenu.Item key="logout" onSelect={handleLogout} destructive>
          <DropdownMenu.ItemIcon ios={{ name: "arrow.right.square" }}>
            <LogOutIcon size={16} />
          </DropdownMenu.ItemIcon>
          <DropdownMenu.ItemTitle>Log Out</DropdownMenu.ItemTitle>
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  );
}
```

## Context Menu

```tsx
import * as ContextMenu from "zeego/context-menu";

function MessageBubble({ message }: { message: Message }) {
  return (
    <ContextMenu.Root>
      <ContextMenu.Trigger>
        <View style={styles.bubble}>
          <Text>{message.text}</Text>
        </View>
      </ContextMenu.Trigger>

      <ContextMenu.Content>
        <ContextMenu.Item key="reply" onSelect={() => replyTo(message)}>
          <ContextMenu.ItemTitle>Reply</ContextMenu.ItemTitle>
        </ContextMenu.Item>

        <ContextMenu.Item key="copy" onSelect={() => copyText(message.text)}>
          <ContextMenu.ItemTitle>Copy</ContextMenu.ItemTitle>
        </ContextMenu.Item>

        <ContextMenu.Item key="forward" onSelect={() => forward(message)}>
          <ContextMenu.ItemTitle>Forward</ContextMenu.ItemTitle>
        </ContextMenu.Item>

        <ContextMenu.Separator />

        <ContextMenu.Item key="delete" onSelect={() => deleteMessage(message.id)} destructive>
          <ContextMenu.ItemTitle>Delete</ContextMenu.ItemTitle>
        </ContextMenu.Item>
      </ContextMenu.Content>
    </ContextMenu.Root>
  );
}
```

## Checkbox Items

```tsx
function FilterMenu({ filters, onToggle }: FilterMenuProps) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <TouchableOpacity>
          <Text>Filters</Text>
        </TouchableOpacity>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content>
        <DropdownMenu.CheckboxItem
          key="unread"
          value={filters.unread ? "on" : "off"}
          onValueChange={() => onToggle("unread")}
        >
          <DropdownMenu.ItemIndicator />
          <DropdownMenu.ItemTitle>Unread Only</DropdownMenu.ItemTitle>
        </DropdownMenu.CheckboxItem>

        <DropdownMenu.CheckboxItem
          key="starred"
          value={filters.starred ? "on" : "off"}
          onValueChange={() => onToggle("starred")}
        >
          <DropdownMenu.ItemIndicator />
          <DropdownMenu.ItemTitle>Starred</DropdownMenu.ItemTitle>
        </DropdownMenu.CheckboxItem>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  );
}
```

## Submenus

```tsx
function SortMenu() {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <TouchableOpacity>
          <Text>Sort</Text>
        </TouchableOpacity>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content>
        <DropdownMenu.Sub>
          <DropdownMenu.SubTrigger key="sort-by">
            <DropdownMenu.ItemTitle>Sort By</DropdownMenu.ItemTitle>
          </DropdownMenu.SubTrigger>
          <DropdownMenu.SubContent>
            <DropdownMenu.Item key="name" onSelect={() => sortBy("name")}>
              <DropdownMenu.ItemTitle>Name</DropdownMenu.ItemTitle>
            </DropdownMenu.Item>
            <DropdownMenu.Item key="date" onSelect={() => sortBy("date")}>
              <DropdownMenu.ItemTitle>Date</DropdownMenu.ItemTitle>
            </DropdownMenu.Item>
            <DropdownMenu.Item key="size" onSelect={() => sortBy("size")}>
              <DropdownMenu.ItemTitle>Size</DropdownMenu.ItemTitle>
            </DropdownMenu.Item>
          </DropdownMenu.SubContent>
        </DropdownMenu.Sub>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  );
}
```

## Additional Resources

- Zeego: https://zeego.dev/
- Dropdown Menu: https://zeego.dev/components/dropdown-menu
- Context Menu: https://zeego.dev/components/context-menu
