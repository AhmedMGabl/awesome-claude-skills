---
name: vuetify-v3
description: Vuetify 3 patterns covering Material Design 3 components, virtual scrolling tables, form validation with Vuelidate, responsive grid system, theme customization, locale support, and Vue 3 Composition API integration.
---

# Vuetify 3

This skill should be used when building Vue 3 applications with Vuetify's Material Design component library. It covers components, data tables, forms, theming, and responsive layouts.

## When to Use This Skill

Use this skill when you need to:

- Build Material Design UIs with Vue 3
- Create data tables with virtual scrolling
- Handle form validation with Vuelidate integration
- Customize Material Design 3 themes
- Build responsive layouts with Vuetify grid

## Setup

```bash
npm install vuetify
```

```ts
// plugins/vuetify.ts
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi-svg";

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#1867C0",
          secondary: "#5CBBF6",
          error: "#B00020",
          surface: "#FFFFFF",
        },
      },
      dark: {
        colors: {
          primary: "#2196F3",
          secondary: "#424242",
          surface: "#121212",
        },
      },
    },
  },
});
```

## Data Table

```vue
<script setup lang="ts">
import { ref, computed } from "vue";

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

const search = ref("");
const page = ref(1);
const itemsPerPage = ref(10);
const sortBy = ref([{ key: "name", order: "asc" as const }]);

const headers = [
  { title: "Name", key: "name", sortable: true },
  { title: "Email", key: "email" },
  { title: "Role", key: "role", sortable: true },
  { title: "Actions", key: "actions", sortable: false },
];

const users = ref<User[]>([
  { id: 1, name: "Alice", email: "alice@test.com", role: "Admin" },
  { id: 2, name: "Bob", email: "bob@test.com", role: "User" },
]);

const loading = ref(false);

async function loadItems({ page, itemsPerPage, sortBy }: any) {
  loading.value = true;
  const response = await fetch(
    `/api/users?page=${page}&limit=${itemsPerPage}&sort=${sortBy[0]?.key}`
  );
  const data = await response.json();
  users.value = data.items;
  loading.value = false;
  return { items: data.items, total: data.total };
}
</script>

<template>
  <v-card>
    <v-card-title>
      <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        density="compact"
      />
    </v-card-title>

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      v-model:page="page"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="users"
      :loading="loading"
      :search="search"
      @update:options="loadItems"
    >
      <template #item.actions="{ item }">
        <v-btn icon="mdi-pencil" variant="text" size="small" @click="editUser(item)" />
        <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="deleteUser(item)" />
      </template>
    </v-data-table-server>
  </v-card>
</template>
```

## Form Validation

```vue
<script setup lang="ts">
import { ref, reactive } from "vue";

const valid = ref(false);
const form = ref<any>(null);

const state = reactive({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const rules = {
  name: [(v: string) => !!v || "Name is required", (v: string) => v.length >= 2 || "Min 2 characters"],
  email: [(v: string) => !!v || "Email is required", (v: string) => /.+@.+\..+/.test(v) || "Invalid email"],
  password: [(v: string) => !!v || "Password is required", (v: string) => v.length >= 8 || "Min 8 characters"],
  confirmPassword: [(v: string) => v === state.password || "Passwords must match"],
};

async function onSubmit() {
  const { valid } = await form.value.validate();
  if (valid) {
    await registerUser(state);
  }
}
</script>

<template>
  <v-form ref="form" v-model="valid" @submit.prevent="onSubmit">
    <v-text-field v-model="state.name" :rules="rules.name" label="Name" required />
    <v-text-field v-model="state.email" :rules="rules.email" label="Email" type="email" required />
    <v-text-field v-model="state.password" :rules="rules.password" label="Password" type="password" />
    <v-text-field
      v-model="state.confirmPassword"
      :rules="rules.confirmPassword"
      label="Confirm Password"
      type="password"
    />
    <v-btn type="submit" color="primary" :disabled="!valid" block>Register</v-btn>
  </v-form>
</template>
```

## Navigation Drawer

```vue
<script setup lang="ts">
const drawer = ref(true);
const rail = ref(false);

const items = [
  { title: "Dashboard", icon: "mdi-view-dashboard", to: "/" },
  { title: "Users", icon: "mdi-account-group", to: "/users" },
  { title: "Reports", icon: "mdi-chart-bar", to: "/reports" },
  { title: "Settings", icon: "mdi-cog", to: "/settings" },
];
</script>

<template>
  <v-navigation-drawer v-model="drawer" :rail="rail">
    <v-list-item
      prepend-icon="mdi-menu"
      @click="rail = !rail"
    />
    <v-divider />
    <v-list nav density="compact">
      <v-list-item
        v-for="item in items"
        :key="item.title"
        :prepend-icon="item.icon"
        :title="item.title"
        :to="item.to"
      />
    </v-list>
  </v-navigation-drawer>
</template>
```

## Dialogs and Bottom Sheets

```vue
<script setup lang="ts">
const dialog = ref(false);
const sheet = ref(false);

function confirm() {
  dialog.value = false;
  performAction();
}
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <template #activator="{ props }">
      <v-btn v-bind="props" color="primary">Open Dialog</v-btn>
    </template>
    <v-card>
      <v-card-title>Confirm Action</v-card-title>
      <v-card-text>Are you sure you want to proceed?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="dialog = false">Cancel</v-btn>
        <v-btn color="primary" @click="confirm">Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-bottom-sheet v-model="sheet">
    <v-card>
      <v-card-title>Choose an option</v-card-title>
      <v-list>
        <v-list-item title="Share" prepend-icon="mdi-share" @click="sheet = false" />
        <v-list-item title="Download" prepend-icon="mdi-download" @click="sheet = false" />
        <v-list-item title="Delete" prepend-icon="mdi-delete" @click="sheet = false" />
      </v-list>
    </v-card>
  </v-bottom-sheet>
</template>
```

## Additional Resources

- Vuetify: https://vuetifyjs.com/
- Components: https://vuetifyjs.com/en/components/all/
- Data Tables: https://vuetifyjs.com/en/components/data-tables/server-side-tables/
