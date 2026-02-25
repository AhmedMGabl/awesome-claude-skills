---
name: nativescript-patterns
description: NativeScript patterns covering native UI components, data binding, navigation, plugins, platform-specific code, and integration with Angular, Vue, and React.
---

# NativeScript Patterns

This skill should be used when building native mobile apps with NativeScript. It covers native UI components, data binding, navigation, plugins, platform APIs, and framework integrations.

## When to Use This Skill

Use this skill when you need to:

- Build truly native mobile apps with JavaScript/TypeScript
- Access native platform APIs directly
- Use NativeScript with Angular, Vue, or React
- Create custom native UI components
- Implement navigation and data binding

## Project Setup

```bash
# Create with TypeScript
ns create myapp --template @nativescript/template-hello-world-ts

# Create with Angular
ns create myapp --template @nativescript/template-blank-ng

# Create with Vue
ns create myapp --template @nativescript-vue/template-blank

# Run
ns run android
ns run ios
```

## Core UI Components

```xml
<!-- app/main-page.xml (NativeScript Core) -->
<Page xmlns="http://schemas.nativescript.org/tns.xsd"
      navigatingTo="onNavigatingTo">
    <ActionBar title="My App">
        <ActionItem text="Add" tap="onAddTap" ios.position="right" />
    </ActionBar>

    <GridLayout rows="auto, *" columns="*">
        <SearchBar hint="Search..." text="{{ searchQuery }}"
                   submit="onSearch" row="0" />

        <ListView items="{{ items }}" row="1" itemTap="onItemTap">
            <ListView.itemTemplate>
                <GridLayout columns="auto, *" padding="12" class="item-row">
                    <Image src="{{ imageUrl }}" width="50" height="50"
                           borderRadius="25" col="0" />
                    <StackLayout col="1" marginLeft="12">
                        <Label text="{{ title }}" class="title" />
                        <Label text="{{ subtitle }}" class="subtitle" />
                    </StackLayout>
                </GridLayout>
            </ListView.itemTemplate>
        </ListView>
    </GridLayout>
</Page>
```

## View Model

```typescript
// app/main-view-model.ts
import { Observable, ObservableArray } from "@nativescript/core";

export class MainViewModel extends Observable {
  private _items: ObservableArray<Item>;
  private _searchQuery: string = "";

  constructor() {
    super();
    this._items = new ObservableArray<Item>();
    this.loadItems();
  }

  get items(): ObservableArray<Item> {
    return this._items;
  }

  get searchQuery(): string {
    return this._searchQuery;
  }

  set searchQuery(value: string) {
    if (this._searchQuery !== value) {
      this._searchQuery = value;
      this.notifyPropertyChange("searchQuery", value);
    }
  }

  async loadItems() {
    const response = await fetch("https://api.example.com/items");
    const data = await response.json();
    this._items.splice(0, this._items.length, ...data);
  }

  onSearch() {
    const filtered = this._items.filter((item) =>
      item.title.toLowerCase().includes(this._searchQuery.toLowerCase())
    );
    this._items.splice(0, this._items.length, ...filtered);
  }
}
```

## Navigation

```typescript
import { Frame, NavigatedData, Page } from "@nativescript/core";

// Navigate forward
Frame.topmost().navigate({
  moduleName: "detail-page",
  context: { itemId: "123" },
  animated: true,
  transition: {
    name: "slide",
    duration: 300,
    curve: "easeInOut",
  },
});

// Receive context
export function onNavigatingTo(args: NavigatedData) {
  const page = args.object as Page;
  const context = page.navigationContext;
  console.log("Item ID:", context.itemId);
}

// Navigate back
Frame.topmost().goBack();
```

## NativeScript with Vue

```vue
<template>
  <Page>
    <ActionBar title="Tasks" />
    <GridLayout rows="auto, *">
      <TextField v-model="newTask" hint="Add task..." row="0"
                 @returnPress="addTask" />
      <ListView :items="tasks" row="1" @itemTap="onItemTap">
        <template #default="{ item }">
          <GridLayout columns="*, auto" padding="12">
            <Label :text="item.title" col="0"
                   :class="{ completed: item.done }" />
            <Switch :checked="item.done" col="1"
                    @checkedChange="toggleTask(item)" />
          </GridLayout>
        </template>
      </ListView>
    </GridLayout>
  </Page>
</template>

<script lang="ts" setup>
import { ref } from "nativescript-vue";

const newTask = ref("");
const tasks = ref<Task[]>([]);

function addTask() {
  if (!newTask.value.trim()) return;
  tasks.value.push({ title: newTask.value, done: false });
  newTask.value = "";
}

function toggleTask(task: Task) {
  task.done = !task.done;
}
</script>
```

## Platform-Specific Code

```typescript
import { isAndroid, isIOS, Device } from "@nativescript/core";

if (isAndroid) {
  const context = android.app.Application.context;
  // Android-specific API calls
}

if (isIOS) {
  const device = UIDevice.currentDevice;
  // iOS-specific API calls
}

// Platform files
// main-page.android.css  — Android-specific styles
// main-page.ios.css      — iOS-specific styles
```

## Plugins

```bash
# Install plugins
ns plugin add @nativescript/camera
ns plugin add @nativescript/geolocation
ns plugin add @nativescript/local-notifications
```

```typescript
import { requestPermissions, takePicture } from "@nativescript/camera";
import * as geolocation from "@nativescript/geolocation";

// Camera
await requestPermissions();
const image = await takePicture({ width: 300, height: 300, keepAspectRatio: true });

// Geolocation
const location = await geolocation.getCurrentLocation({
  desiredAccuracy: 3,
  maximumAge: 5000,
  timeout: 10000,
});
```

## Additional Resources

- NativeScript Docs: https://docs.nativescript.org/
- Plugins: https://market.nativescript.org/
- NativeScript-Vue: https://nativescript-vue.org/
