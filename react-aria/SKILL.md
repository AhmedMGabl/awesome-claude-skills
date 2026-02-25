---
name: react-aria
description: React Aria accessible components covering hooks-based primitives, React Aria Components, collections, selection, drag and drop, internationalization, forms, overlays, and custom styling patterns.
---

# React Aria

This skill should be used when building accessible UI components with React Aria. It covers hooks, pre-built components, collections, and internationalization.

## When to Use This Skill

Use this skill when you need to:

- Build fully accessible UI components
- Use pre-built accessible patterns (dialogs, menus, combobox)
- Handle keyboard navigation and screen readers
- Implement drag and drop with accessibility
- Support internationalization and RTL layouts

## Setup

```bash
npm install react-aria-components
# Or individual hooks:
npm install react-aria react-stately
```

## React Aria Components

```tsx
import {
  Button, Dialog, DialogTrigger, Modal, ModalOverlay,
  Label, Input, TextField, Form,
} from "react-aria-components";

function LoginDialog() {
  return (
    <DialogTrigger>
      <Button className="btn-primary">Sign In</Button>
      <ModalOverlay className="fixed inset-0 bg-black/50 flex items-center justify-center">
        <Modal className="bg-white rounded-lg p-6 w-96">
          <Dialog className="outline-none">
            {({ close }) => (
              <Form onSubmit={() => close()}>
                <h2 className="text-xl font-bold mb-4">Sign In</h2>
                <TextField className="mb-3" isRequired>
                  <Label className="block text-sm font-medium">Email</Label>
                  <Input className="border rounded px-3 py-2 w-full" type="email" />
                </TextField>
                <TextField className="mb-4" isRequired>
                  <Label className="block text-sm font-medium">Password</Label>
                  <Input className="border rounded px-3 py-2 w-full" type="password" />
                </TextField>
                <div className="flex gap-2 justify-end">
                  <Button onPress={close} className="px-4 py-2">Cancel</Button>
                  <Button type="submit" className="btn-primary px-4 py-2">Sign In</Button>
                </div>
              </Form>
            )}
          </Dialog>
        </Modal>
      </ModalOverlay>
    </DialogTrigger>
  );
}
```

## Select / ComboBox

```tsx
import { Select, Label, Button, SelectValue, Popover, ListBox, ListBoxItem } from "react-aria-components";

function CountrySelect() {
  return (
    <Select className="flex flex-col gap-1">
      <Label className="text-sm font-medium">Country</Label>
      <Button className="border rounded px-3 py-2 flex justify-between items-center">
        <SelectValue />
        <span>▼</span>
      </Button>
      <Popover className="bg-white border rounded shadow-lg">
        <ListBox className="max-h-60 overflow-auto p-1">
          <ListBoxItem id="us" className="px-3 py-2 rounded hover:bg-blue-100 cursor-pointer">
            United States
          </ListBoxItem>
          <ListBoxItem id="uk" className="px-3 py-2 rounded hover:bg-blue-100 cursor-pointer">
            United Kingdom
          </ListBoxItem>
          <ListBoxItem id="de" className="px-3 py-2 rounded hover:bg-blue-100 cursor-pointer">
            Germany
          </ListBoxItem>
        </ListBox>
      </Popover>
    </Select>
  );
}
```

## Table with Sorting and Selection

```tsx
import { Cell, Column, Row, Table, TableBody, TableHeader, useTableOptions } from "react-aria-components";

function UserTable({ users }: { users: User[] }) {
  return (
    <Table aria-label="Users" selectionMode="multiple" className="w-full border-collapse">
      <TableHeader>
        <Column isRowHeader allowsSorting>Name</Column>
        <Column allowsSorting>Email</Column>
        <Column>Role</Column>
      </TableHeader>
      <TableBody items={users}>
        {(user) => (
          <Row id={user.id} className="border-b hover:bg-gray-50">
            <Cell className="p-2">{user.name}</Cell>
            <Cell className="p-2">{user.email}</Cell>
            <Cell className="p-2">{user.role}</Cell>
          </Row>
        )}
      </TableBody>
    </Table>
  );
}
```

## Hooks-Based Approach

```tsx
import { useButton } from "react-aria";
import { useRef } from "react";

function CustomButton(props: { onPress: () => void; children: React.ReactNode }) {
  const ref = useRef<HTMLButtonElement>(null);
  const { buttonProps } = useButton(props, ref);

  return (
    <button {...buttonProps} ref={ref} className="btn">
      {props.children}
    </button>
  );
}
```

## Drag and Drop

```tsx
import { useDragAndDrop } from "react-aria-components";
import { useListData } from "react-stately";

function ReorderableList() {
  const list = useListData({ initialItems: [
    { id: "1", name: "Item 1" },
    { id: "2", name: "Item 2" },
    { id: "3", name: "Item 3" },
  ]});

  const { dragAndDropHooks } = useDragAndDrop({
    getItems: (keys) => [...keys].map((key) => ({
      "text/plain": list.getItem(key).name,
    })),
    onReorder: (e) => {
      if (e.target.dropPosition === "before") {
        list.moveBefore(e.target.key, e.keys);
      } else if (e.target.dropPosition === "after") {
        list.moveAfter(e.target.key, e.keys);
      }
    },
  });

  return (
    <ListBox items={list.items} dragAndDropHooks={dragAndDropHooks} selectionMode="multiple">
      {(item) => <ListBoxItem>{item.name}</ListBoxItem>}
    </ListBox>
  );
}
```

## Additional Resources

- React Aria docs: https://react-spectrum.adobe.com/react-aria/
- Components: https://react-spectrum.adobe.com/react-aria/components.html
- Styling: https://react-spectrum.adobe.com/react-aria/styling.html
