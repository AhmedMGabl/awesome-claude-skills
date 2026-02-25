---
name: kobalte-ui
description: Kobalte UI patterns covering accessible SolidJS components, headless primitives, polymorphic rendering, form controls, dialogs, menus, select, combobox, and WAI-ARIA compliant component composition.
---

# Kobalte UI

This skill should be used when building accessible UIs in SolidJS with Kobalte. It covers headless components, form controls, overlays, and WAI-ARIA patterns.

## When to Use This Skill

Use this skill when you need to:

- Build accessible SolidJS component libraries
- Use headless, unstyled UI primitives
- Create WAI-ARIA compliant form controls
- Build dialogs, menus, and select components
- Compose components with polymorphic rendering

## Setup

```bash
npm install @kobalte/core
```

## Button

```tsx
import { Button } from "@kobalte/core/button";

function MyButton() {
  return (
    <Button
      class="btn btn-primary"
      onClick={() => console.log("clicked")}
    >
      Click me
    </Button>
  );
}

// Polymorphic rendering
<Button as="a" href="/about" class="btn-link">
  About
</Button>
```

## Dialog

```tsx
import { Dialog } from "@kobalte/core/dialog";

function ConfirmDialog() {
  return (
    <Dialog>
      <Dialog.Trigger class="btn">Open Dialog</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay class="dialog-overlay" />
        <Dialog.Content class="dialog-content">
          <Dialog.Title>Confirm Action</Dialog.Title>
          <Dialog.Description>
            Are you sure you want to proceed?
          </Dialog.Description>
          <div class="dialog-actions">
            <Dialog.CloseButton class="btn btn-secondary">
              Cancel
            </Dialog.CloseButton>
            <button class="btn btn-danger" onClick={handleConfirm}>
              Confirm
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog>
  );
}
```

## Select

```tsx
import { Select } from "@kobalte/core/select";

interface Fruit {
  value: string;
  label: string;
  disabled?: boolean;
}

const fruits: Fruit[] = [
  { value: "apple", label: "Apple" },
  { value: "banana", label: "Banana" },
  { value: "cherry", label: "Cherry", disabled: true },
  { value: "grape", label: "Grape" },
];

function FruitSelect() {
  const [value, setValue] = createSignal<Fruit>();

  return (
    <Select<Fruit>
      value={value()}
      onChange={setValue}
      options={fruits}
      optionValue="value"
      optionTextValue="label"
      optionDisabled="disabled"
      placeholder="Select a fruit"
      itemComponent={(props) => (
        <Select.Item item={props.item} class="select-item">
          <Select.ItemLabel>{props.item.rawValue.label}</Select.ItemLabel>
          <Select.ItemIndicator>✓</Select.ItemIndicator>
        </Select.Item>
      )}
    >
      <Select.Trigger class="select-trigger">
        <Select.Value<Fruit>>
          {(state) => state.selectedOption().label}
        </Select.Value>
        <Select.Icon>▼</Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content class="select-content">
          <Select.Listbox class="select-listbox" />
        </Select.Content>
      </Select.Portal>
    </Select>
  );
}
```

## Combobox

```tsx
import { Combobox } from "@kobalte/core/combobox";

function SearchCombobox() {
  const [options, setOptions] = createSignal(allOptions);

  function onInputChange(value: string) {
    setOptions(
      allOptions.filter((opt) =>
        opt.label.toLowerCase().includes(value.toLowerCase())
      )
    );
  }

  return (
    <Combobox
      options={options()}
      optionValue="value"
      optionTextValue="label"
      onInputChange={onInputChange}
      placeholder="Search..."
      itemComponent={(props) => (
        <Combobox.Item item={props.item} class="combobox-item">
          <Combobox.ItemLabel>{props.item.rawValue.label}</Combobox.ItemLabel>
        </Combobox.Item>
      )}
    >
      <Combobox.Control class="combobox-control">
        <Combobox.Input class="combobox-input" />
        <Combobox.Trigger class="combobox-trigger">▼</Combobox.Trigger>
      </Combobox.Control>
      <Combobox.Portal>
        <Combobox.Content class="combobox-content">
          <Combobox.Listbox class="combobox-listbox" />
        </Combobox.Content>
      </Combobox.Portal>
    </Combobox>
  );
}
```

## Tabs

```tsx
import { Tabs } from "@kobalte/core/tabs";

function SettingsTabs() {
  return (
    <Tabs defaultValue="general" class="tabs">
      <Tabs.List class="tabs-list">
        <Tabs.Trigger value="general" class="tabs-trigger">General</Tabs.Trigger>
        <Tabs.Trigger value="security" class="tabs-trigger">Security</Tabs.Trigger>
        <Tabs.Trigger value="notifications" class="tabs-trigger">Notifications</Tabs.Trigger>
        <Tabs.Indicator class="tabs-indicator" />
      </Tabs.List>
      <Tabs.Content value="general" class="tabs-content">
        General settings content
      </Tabs.Content>
      <Tabs.Content value="security" class="tabs-content">
        Security settings content
      </Tabs.Content>
      <Tabs.Content value="notifications" class="tabs-content">
        Notification preferences
      </Tabs.Content>
    </Tabs>
  );
}
```

## TextField and Form Controls

```tsx
import { TextField } from "@kobalte/core/text-field";
import { Checkbox } from "@kobalte/core/checkbox";

function ContactForm() {
  return (
    <form>
      <TextField class="text-field" validationState={nameError() ? "invalid" : "valid"}>
        <TextField.Label>Name</TextField.Label>
        <TextField.Input
          placeholder="Enter your name"
          onInput={(e) => setName(e.currentTarget.value)}
        />
        <TextField.ErrorMessage>{nameError()}</TextField.ErrorMessage>
      </TextField>

      <Checkbox class="checkbox" onChange={setAgreed}>
        <Checkbox.Input />
        <Checkbox.Control class="checkbox-control">
          <Checkbox.Indicator>✓</Checkbox.Indicator>
        </Checkbox.Control>
        <Checkbox.Label>I agree to the terms</Checkbox.Label>
      </Checkbox>
    </form>
  );
}
```

## Additional Resources

- Kobalte: https://kobalte.dev/
- Component docs: https://kobalte.dev/docs/core/overview/introduction
- SolidJS: https://www.solidjs.com/
