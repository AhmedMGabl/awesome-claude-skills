---
name: quasar-framework
description: Quasar Framework patterns covering cross-platform Vue 3 apps, Material/iOS components, Quasar CLI with Vite, SSR mode, PWA configuration, Electron/Capacitor builds, and responsive layout system.
---

# Quasar Framework

This skill should be used when building cross-platform Vue 3 applications with Quasar Framework. It covers components, layouts, SSR, PWA, Electron, and Capacitor builds.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform apps from a single Vue 3 codebase
- Use Material Design or iOS-style components
- Configure SSR, PWA, or desktop builds
- Create responsive layouts with Quasar grid
- Deploy to web, mobile, and desktop

## Setup

```bash
npm init quasar
# or add to existing Vue project
npm install quasar @quasar/extras
npm install -D @quasar/vite-plugin
```

## Layout System

```vue
<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>My App</q-toolbar-title>
        <q-btn flat round icon="notifications">
          <q-badge color="red" floating>3</q-badge>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Navigation</q-item-label>
        <q-item
          v-for="link in navLinks"
          :key="link.title"
          :to="link.to"
          clickable
          v-ripple
        >
          <q-item-section avatar>
            <q-icon :name="link.icon" />
          </q-item-section>
          <q-item-section>{{ link.title }}</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer elevated>
      <q-toolbar>
        <q-toolbar-title class="text-center text-caption">
          &copy; 2025 My App
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from "vue";

const leftDrawerOpen = ref(false);

const navLinks = [
  { title: "Dashboard", icon: "dashboard", to: "/" },
  { title: "Users", icon: "people", to: "/users" },
  { title: "Settings", icon: "settings", to: "/settings" },
];

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
```

## Table with Server-Side Data

```vue
<script setup lang="ts">
import { ref } from "vue";

const columns = [
  { name: "name", label: "Name", field: "name", sortable: true, align: "left" as const },
  { name: "email", label: "Email", field: "email", align: "left" as const },
  { name: "role", label: "Role", field: "role", sortable: true },
  { name: "actions", label: "Actions", field: "actions" },
];

const rows = ref([]);
const loading = ref(false);
const pagination = ref({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
  sortBy: "name",
  descending: false,
});

async function onRequest(props: any) {
  const { page, rowsPerPage, sortBy, descending } = props.pagination;
  loading.value = true;
  const response = await fetch(
    `/api/users?page=${page}&limit=${rowsPerPage}&sort=${sortBy}&desc=${descending}`
  );
  const data = await response.json();
  rows.value = data.items;
  pagination.value = { ...props.pagination, rowsNumber: data.total };
  loading.value = false;
}
</script>

<template>
  <q-table
    :columns="columns"
    :rows="rows"
    :loading="loading"
    v-model:pagination="pagination"
    row-key="id"
    @request="onRequest"
  >
    <template #body-cell-actions="props">
      <q-td :props="props">
        <q-btn flat round size="sm" icon="edit" @click="editRow(props.row)" />
        <q-btn flat round size="sm" icon="delete" color="negative" @click="deleteRow(props.row)" />
      </q-td>
    </template>
  </q-table>
</template>
```

## Form with Validation

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useQuasar } from "quasar";

const $q = useQuasar();
const name = ref("");
const email = ref("");

function onSubmit() {
  $q.notify({ type: "positive", message: "Form submitted!" });
}

function onReset() {
  name.value = "";
  email.value = "";
}
</script>

<template>
  <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
    <q-input
      v-model="name"
      label="Name *"
      :rules="[(val) => !!val || 'Name is required']"
      lazy-rules
    />
    <q-input
      v-model="email"
      label="Email *"
      type="email"
      :rules="[
        (val) => !!val || 'Email is required',
        (val) => /.+@.+\..+/.test(val) || 'Invalid email',
      ]"
      lazy-rules
    />
    <div>
      <q-btn label="Submit" type="submit" color="primary" />
      <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />
    </div>
  </q-form>
</template>
```

## Dialogs and Notifications

```ts
import { useQuasar } from "quasar";

const $q = useQuasar();

// Confirmation dialog
$q.dialog({
  title: "Confirm",
  message: "Would you like to delete this item?",
  cancel: true,
  persistent: true,
}).onOk(() => {
  deleteItem();
}).onCancel(() => {
  console.log("Cancelled");
});

// Loading indicator
$q.loading.show({ message: "Processing..." });
await processData();
$q.loading.hide();

// Notifications
$q.notify({
  type: "positive",
  message: "Saved successfully",
  position: "top-right",
  timeout: 3000,
  actions: [{ icon: "close", color: "white", round: true }],
});
```

## Additional Resources

- Quasar: https://quasar.dev/
- Components: https://quasar.dev/vue-components
- CLI: https://quasar.dev/quasar-cli-vite/quasar-config-file
