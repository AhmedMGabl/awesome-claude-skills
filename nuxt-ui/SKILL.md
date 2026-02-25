---
name: nuxt-ui
description: Nuxt UI patterns covering component library setup, form validation with Zod, table components, modal and slideover overlays, command palette, theming with Tailwind, and Nuxt 3 integration.
---

# Nuxt UI

This skill should be used when building Vue/Nuxt applications with Nuxt UI component library. It covers components, forms, tables, overlays, theming, and Nuxt 3 integration.

## When to Use This Skill

Use this skill when you need to:

- Build Nuxt 3 UIs with pre-built components
- Handle form validation with Zod/Yup
- Create data tables with sorting and pagination
- Add modals, slideovers, and command palette
- Customize theme with Tailwind CSS

## Setup

```bash
npx nuxi module add @nuxt/ui
```

## Form with Validation

```vue
<script setup lang="ts">
import { z } from "zod";
import type { FormSubmitEvent } from "#ui/types";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
  role: z.enum(["admin", "user", "editor"]),
  bio: z.string().max(300).optional(),
});

type Schema = z.output<typeof schema>;

const state = reactive({
  name: "",
  email: "",
  role: "user" as const,
  bio: "",
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
  console.log(event.data);
}
</script>

<template>
  <UForm :schema="schema" :state="state" @submit="onSubmit" class="space-y-4">
    <UFormGroup label="Name" name="name">
      <UInput v-model="state.name" placeholder="Enter name" />
    </UFormGroup>

    <UFormGroup label="Email" name="email">
      <UInput v-model="state.email" type="email" placeholder="you@example.com" />
    </UFormGroup>

    <UFormGroup label="Role" name="role">
      <USelect
        v-model="state.role"
        :options="['admin', 'user', 'editor']"
      />
    </UFormGroup>

    <UFormGroup label="Bio" name="bio">
      <UTextarea v-model="state.bio" placeholder="Tell us about yourself" />
    </UFormGroup>

    <UButton type="submit">Submit</UButton>
  </UForm>
</template>
```

## Table

```vue
<script setup lang="ts">
const columns = [
  { key: "name", label: "Name", sortable: true },
  { key: "email", label: "Email" },
  { key: "role", label: "Role", sortable: true },
  { key: "actions", label: "" },
];

const users = ref([
  { id: 1, name: "Alice", email: "alice@test.com", role: "Admin" },
  { id: 2, name: "Bob", email: "bob@test.com", role: "User" },
  { id: 3, name: "Carol", email: "carol@test.com", role: "Editor" },
]);

const page = ref(1);
const pageCount = 10;

const actions = (row: any) => [
  [{ label: "Edit", icon: "i-heroicons-pencil", click: () => editUser(row) }],
  [{ label: "Delete", icon: "i-heroicons-trash", click: () => deleteUser(row) }],
];
</script>

<template>
  <UTable :columns="columns" :rows="users">
    <template #actions-data="{ row }">
      <UDropdown :items="actions(row)">
        <UButton icon="i-heroicons-ellipsis-horizontal" variant="ghost" />
      </UDropdown>
    </template>
  </UTable>
  <UPagination v-model="page" :page-count="pageCount" :total="users.length" />
</template>
```

## Modal and Slideover

```vue
<script setup lang="ts">
const isOpen = ref(false);
const isSlideoverOpen = ref(false);
</script>

<template>
  <UButton @click="isOpen = true">Open Modal</UButton>
  <UModal v-model="isOpen">
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold">Confirm Action</h3>
      </template>
      <p>Are you sure you want to proceed?</p>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="ghost" @click="isOpen = false">Cancel</UButton>
          <UButton color="red" @click="handleConfirm">Confirm</UButton>
        </div>
      </template>
    </UCard>
  </UModal>

  <UButton @click="isSlideoverOpen = true">Open Panel</UButton>
  <USlideover v-model="isSlideoverOpen">
    <UCard class="h-full">
      <template #header>Details Panel</template>
      <p>Side panel content here</p>
    </UCard>
  </USlideover>
</template>
```

## Notifications

```vue
<script setup lang="ts">
const toast = useToast();

function showNotification() {
  toast.add({
    title: "Success!",
    description: "Your changes have been saved.",
    icon: "i-heroicons-check-circle",
    color: "green",
    timeout: 3000,
  });
}
</script>
```

## Command Palette

```vue
<script setup lang="ts">
const isOpen = ref(false);
const groups = [
  {
    key: "actions",
    label: "Actions",
    commands: [
      { id: "new", label: "New Document", icon: "i-heroicons-document-plus" },
      { id: "settings", label: "Settings", icon: "i-heroicons-cog" },
    ],
  },
  {
    key: "users",
    label: "Users",
    search: async (q: string) => {
      const users = await searchUsers(q);
      return users.map((u) => ({ id: u.id, label: u.name }));
    },
  },
];

defineShortcuts({ meta_k: { handler: () => { isOpen.value = true; } } });
</script>

<template>
  <UCommandPalette v-model="isOpen" :groups="groups" />
</template>
```

## Additional Resources

- Nuxt UI: https://ui.nuxt.com/
- Components: https://ui.nuxt.com/components
- Forms: https://ui.nuxt.com/components/form
