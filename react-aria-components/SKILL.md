---
name: react-aria-components
description: React Aria Components patterns covering accessible form controls, menus, dialogs, date pickers, tables, drag and drop, collections, styling with Tailwind, and custom theme integration for production-ready accessible UIs.
---

# React Aria Components

This skill should be used when building accessible UIs with React Aria Components. It covers form controls, menus, dialogs, date pickers, tables, and styling.

## When to Use This Skill

Use this skill when you need to:

- Build fully accessible UI components (WAI-ARIA compliant)
- Use pre-built components with customizable styling
- Implement complex interactions (date pickers, drag and drop)
- Style accessible components with Tailwind CSS
- Handle internationalization and RTL layouts

## Buttons and Links

```tsx
import { Button, Link, ToggleButton } from "react-aria-components";

function Actions() {
  return (
    <div>
      <Button
        onPress={() => console.log("Pressed")}
        className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 pressed:bg-blue-800"
      >
        Save Changes
      </Button>

      <Link
        href="/settings"
        className="text-blue-600 underline hover:text-blue-800"
      >
        Settings
      </Link>

      <ToggleButton className="rounded-md border px-3 py-1 selected:bg-blue-100 selected:border-blue-500">
        Pin
      </ToggleButton>
    </div>
  );
}
```

## Form Controls

```tsx
import {
  TextField, Label, Input, TextArea, FieldError,
  NumberField, Group,
  Select, SelectValue, Popover, ListBox, ListBoxItem,
  Checkbox, CheckboxGroup,
  RadioGroup, Radio,
  Switch,
} from "react-aria-components";

function SettingsForm() {
  return (
    <form>
      <TextField isRequired>
        <Label>Name</Label>
        <Input className="rounded border px-3 py-2" />
        <FieldError />
      </TextField>

      <TextField>
        <Label>Bio</Label>
        <TextArea className="rounded border px-3 py-2" rows={3} />
      </TextField>

      <NumberField minValue={0} maxValue={100}>
        <Label>Age</Label>
        <Group className="flex">
          <Button slot="decrement">-</Button>
          <Input className="rounded border px-3 py-2 text-center w-20" />
          <Button slot="increment">+</Button>
        </Group>
      </NumberField>

      <Select>
        <Label>Role</Label>
        <Button className="rounded border px-3 py-2">
          <SelectValue />
        </Button>
        <Popover>
          <ListBox>
            <ListBoxItem id="admin">Admin</ListBoxItem>
            <ListBoxItem id="editor">Editor</ListBoxItem>
            <ListBoxItem id="viewer">Viewer</ListBoxItem>
          </ListBox>
        </Popover>
      </Select>

      <CheckboxGroup>
        <Label>Notifications</Label>
        <Checkbox value="email">Email</Checkbox>
        <Checkbox value="sms">SMS</Checkbox>
        <Checkbox value="push">Push</Checkbox>
      </CheckboxGroup>

      <Switch className="group flex items-center gap-2">
        <div className="h-6 w-10 rounded-full bg-gray-300 group-selected:bg-blue-600 transition">
          <div className="h-5 w-5 rounded-full bg-white translate-x-0.5 group-selected:translate-x-4.5 transition" />
        </div>
        Dark mode
      </Switch>
    </form>
  );
}
```

## Dialog / Modal

```tsx
import {
  DialogTrigger, Modal, ModalOverlay, Dialog,
  Heading, Button,
} from "react-aria-components";

function ConfirmDialog() {
  return (
    <DialogTrigger>
      <Button className="rounded bg-red-600 px-4 py-2 text-white">Delete</Button>
      <ModalOverlay className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
        <Modal className="max-w-md rounded-lg bg-white p-6 shadow-xl">
          <Dialog>
            {({ close }) => (
              <>
                <Heading slot="title" className="text-lg font-semibold">
                  Confirm Deletion
                </Heading>
                <p className="mt-2 text-gray-600">
                  This action cannot be undone.
                </p>
                <div className="mt-4 flex gap-2 justify-end">
                  <Button onPress={close} className="rounded px-4 py-2 border">
                    Cancel
                  </Button>
                  <Button
                    onPress={() => { deleteItem(); close(); }}
                    className="rounded bg-red-600 px-4 py-2 text-white"
                  >
                    Delete
                  </Button>
                </div>
              </>
            )}
          </Dialog>
        </Modal>
      </ModalOverlay>
    </DialogTrigger>
  );
}
```

## Date Picker

```tsx
import {
  DatePicker, Label, Group, DateInput, DateSegment,
  Button, Popover, Dialog, Calendar, CalendarGrid,
  CalendarGridBody, CalendarGridHeader, CalendarHeaderCell,
  CalendarCell, Heading,
} from "react-aria-components";

function DatePickerField() {
  return (
    <DatePicker>
      <Label>Date</Label>
      <Group className="flex rounded border">
        <DateInput className="flex px-3 py-2">
          {(segment) => <DateSegment segment={segment} className="px-0.5 focus:bg-blue-100 rounded" />}
        </DateInput>
        <Button className="px-2 border-l">📅</Button>
      </Group>
      <Popover>
        <Dialog>
          <Calendar>
            <header className="flex items-center justify-between px-4 py-2">
              <Button slot="previous">←</Button>
              <Heading />
              <Button slot="next">→</Button>
            </header>
            <CalendarGrid>
              <CalendarGridHeader>
                {(day) => <CalendarHeaderCell>{day}</CalendarHeaderCell>}
              </CalendarGridHeader>
              <CalendarGridBody>
                {(date) => <CalendarCell date={date} className="rounded hover:bg-gray-100 selected:bg-blue-600 selected:text-white p-2" />}
              </CalendarGridBody>
            </CalendarGrid>
          </Calendar>
        </Dialog>
      </Popover>
    </DatePicker>
  );
}
```

## Table

```tsx
import { Table, TableHeader, Column, TableBody, Row, Cell } from "react-aria-components";

function UsersTable({ users }: { users: User[] }) {
  return (
    <Table aria-label="Users" selectionMode="multiple" className="w-full">
      <TableHeader>
        <Column isRowHeader>Name</Column>
        <Column>Email</Column>
        <Column>Role</Column>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <Row key={user.id} className="hover:bg-gray-50 selected:bg-blue-50">
            <Cell className="font-medium">{user.name}</Cell>
            <Cell>{user.email}</Cell>
            <Cell>{user.role}</Cell>
          </Row>
        ))}
      </TableBody>
    </Table>
  );
}
```

## Additional Resources

- React Aria Components: https://react-spectrum.adobe.com/react-aria/components.html
- Styling guide: https://react-spectrum.adobe.com/react-aria/styling.html
- Tailwind plugin: https://react-spectrum.adobe.com/react-aria/styling.html#tailwind-css
