---
name: plate-editor
description: Plate editor patterns covering Slate-based rich text, plugin system, custom elements, serialization, toolbar components, mention/emoji plugins, and shadcn/ui styled editor components.
---

# Plate Editor

This skill should be used when building rich text editors with Plate (Slate-based). It covers plugins, custom elements, serialization, toolbars, and UI components.

## When to Use This Skill

Use this skill when you need to:

- Build rich text editors with Slate.js
- Use pre-built editor plugins
- Create custom element and leaf types
- Serialize content to HTML/Markdown
- Build editors with shadcn/ui components

## Setup

```bash
npm install @udecode/plate @udecode/plate-common
npm install @udecode/plate-heading @udecode/plate-list @udecode/plate-basic-marks
npm install @udecode/plate-link @udecode/plate-code-block @udecode/plate-block-quote
npm install @udecode/plate-media @udecode/plate-mention @udecode/plate-table
```

## Basic Editor

```tsx
import { Plate, PlateContent, PlateEditor } from "@udecode/plate/react";
import { createPlateEditor } from "@udecode/plate/react";
import { BasicMarksPlugin } from "@udecode/plate-basic-marks/react";
import { HeadingPlugin } from "@udecode/plate-heading/react";
import { ListPlugin } from "@udecode/plate-list/react";
import { LinkPlugin } from "@udecode/plate-link/react";
import { BlockquotePlugin } from "@udecode/plate-block-quote/react";
import { CodeBlockPlugin } from "@udecode/plate-code-block/react";
import { ImagePlugin } from "@udecode/plate-media/react";

const editor = createPlateEditor({
  plugins: [
    HeadingPlugin,
    BasicMarksPlugin,
    ListPlugin,
    LinkPlugin,
    BlockquotePlugin,
    CodeBlockPlugin,
    ImagePlugin,
  ],
});

function RichTextEditor({ initialValue, onChange }: {
  initialValue?: any[];
  onChange?: (value: any[]) => void;
}) {
  return (
    <Plate
      editor={editor}
      initialValue={initialValue}
      onChange={({ value }) => onChange?.(value)}
    >
      <FixedToolbar />
      <PlateContent placeholder="Start writing..." className="prose" />
    </Plate>
  );
}
```

## Toolbar

```tsx
import { useEditorState, useEditorRef } from "@udecode/plate/react";
import { MarkToolbarButton, TurnIntoDropdownMenu } from "@udecode/plate-ui";

function FixedToolbar() {
  const editor = useEditorRef();

  return (
    <div className="toolbar">
      <TurnIntoDropdownMenu />
      <MarkToolbarButton nodeType="bold" tooltip="Bold (Ctrl+B)">
        B
      </MarkToolbarButton>
      <MarkToolbarButton nodeType="italic" tooltip="Italic (Ctrl+I)">
        I
      </MarkToolbarButton>
      <MarkToolbarButton nodeType="underline" tooltip="Underline (Ctrl+U)">
        U
      </MarkToolbarButton>
      <MarkToolbarButton nodeType="code" tooltip="Inline Code">
        {"</>"}
      </MarkToolbarButton>
      <button onClick={() => {
        editor.tf.toggle.list({ type: "ul" });
      }}>
        Bullet List
      </button>
      <button onClick={() => {
        editor.tf.toggle.list({ type: "ol" });
      }}>
        Ordered List
      </button>
    </div>
  );
}
```

## Custom Element Plugin

```tsx
import { createPluginFactory, PlateElement } from "@udecode/plate/react";

// Define the callout element type
interface CalloutElement {
  type: "callout";
  calloutType: "info" | "warning" | "tip";
  children: any[];
}

// Create the plugin
const CalloutPlugin = createPluginFactory({
  key: "callout",
  isElement: true,
  component: CalloutElement,
});

// Render component
function CalloutElement({ attributes, children, element }: any) {
  const styles: Record<string, string> = {
    info: "bg-blue-50 border-blue-400",
    warning: "bg-yellow-50 border-yellow-400",
    tip: "bg-green-50 border-green-400",
  };

  return (
    <div {...attributes} className={`p-4 border-l-4 rounded my-2 ${styles[element.calloutType] || styles.info}`}>
      {children}
    </div>
  );
}
```

## Mention Plugin

```tsx
import { MentionPlugin, MentionInputPlugin } from "@udecode/plate-mention/react";
import { MentionCombobox } from "@udecode/plate-ui";

const plugins = [
  MentionPlugin.configure({
    options: {
      triggerPreviousCharPattern: /^$|^[\s"']$/,
    },
  }),
  MentionInputPlugin,
];

function EditorWithMentions() {
  const users = [
    { key: "1", text: "Alice" },
    { key: "2", text: "Bob" },
    { key: "3", text: "Carol" },
  ];

  return (
    <Plate editor={editor}>
      <PlateContent />
      <MentionCombobox items={users} />
    </Plate>
  );
}
```

## Serialization

```ts
import { serializeHtml } from "@udecode/plate-serializer-html";
import { serializeMd } from "@udecode/plate-serializer-md";

// To HTML
const html = serializeHtml(editor, { nodes: editor.children });

// To Markdown
const markdown = serializeMd(editor, { nodes: editor.children });

// From HTML
import { deserializeHtml } from "@udecode/plate-serializer-html";
const nodes = deserializeHtml(editor, { element: htmlString });
editor.tf.setValue(nodes);
```

## Table Plugin

```tsx
import { TablePlugin } from "@udecode/plate-table/react";

const plugins = [
  TablePlugin.configure({
    options: {
      enableMerging: true,
    },
  }),
];

// Insert table
editor.tf.insert.table({ rows: 3, columns: 3 });

// Add row/column
editor.tf.insert.tableRow();
editor.tf.insert.tableColumn();

// Delete row/column
editor.tf.remove.tableRow();
editor.tf.remove.tableColumn();
```

## Additional Resources

- Plate: https://platejs.org/
- Plugins: https://platejs.org/docs/plugins
- Components: https://platejs.org/docs/components
