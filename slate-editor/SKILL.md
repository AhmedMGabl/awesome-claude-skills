---
name: slate-editor
description: Slate editor patterns covering customizable rich text framework, custom elements, leaves, plugins, serialization, normalizing, collaborative editing, and React integration.
---

# Slate Editor

This skill should be used when building rich text editors with Slate. It covers custom elements, leaves, plugins, serialization, normalizing, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build fully customizable rich text editors
- Create custom element and leaf types
- Implement complex editing behaviors
- Serialize content to/from HTML or Markdown
- Integrate with React applications

## Setup

```bash
npm install slate slate-react slate-history
```

## Basic Editor

```tsx
import { createEditor, Descendant } from "slate";
import { Slate, Editable, withReact } from "slate-react";
import { withHistory } from "slate-history";
import { useState, useMemo, useCallback } from "react";

function RichTextEditor() {
  const editor = useMemo(() => withHistory(withReact(createEditor())), []);
  const [value, setValue] = useState<Descendant[]>([
    { type: "paragraph", children: [{ text: "Start writing..." }] },
  ]);

  const renderElement = useCallback((props: any) => {
    switch (props.element.type) {
      case "heading-one": return <h1 {...props.attributes}>{props.children}</h1>;
      case "heading-two": return <h2 {...props.attributes}>{props.children}</h2>;
      case "block-quote": return <blockquote {...props.attributes}>{props.children}</blockquote>;
      case "bulleted-list": return <ul {...props.attributes}>{props.children}</ul>;
      case "list-item": return <li {...props.attributes}>{props.children}</li>;
      default: return <p {...props.attributes}>{props.children}</p>;
    }
  }, []);

  const renderLeaf = useCallback((props: any) => {
    let { children } = props;
    if (props.leaf.bold) children = <strong>{children}</strong>;
    if (props.leaf.italic) children = <em>{children}</em>;
    if (props.leaf.underline) children = <u>{children}</u>;
    if (props.leaf.code) children = <code>{children}</code>;
    return <span {...props.attributes}>{children}</span>;
  }, []);

  return (
    <Slate editor={editor} initialValue={value} onChange={setValue}>
      <Editable
        renderElement={renderElement}
        renderLeaf={renderLeaf}
        placeholder="Enter some text..."
      />
    </Slate>
  );
}
```

## Custom Elements

```tsx
import { Editor, Transforms, Element as SlateElement } from "slate";

// Define custom types
type CustomElement =
  | { type: "paragraph"; children: CustomText[] }
  | { type: "code-block"; language: string; children: CustomText[] }
  | { type: "image"; url: string; alt: string; children: CustomText[] };

type CustomText = {
  text: string;
  bold?: boolean;
  italic?: boolean;
  code?: boolean;
};

// Toggle block type
function toggleBlock(editor: Editor, format: string) {
  const isActive = isBlockActive(editor, format);
  Transforms.setNodes(
    editor,
    { type: isActive ? "paragraph" : format } as Partial<SlateElement>,
    { match: (n) => SlateElement.isElement(n) && Editor.isBlock(editor, n) }
  );
}

function isBlockActive(editor: Editor, format: string) {
  const [match] = Editor.nodes(editor, {
    match: (n) => SlateElement.isElement(n) && n.type === format,
  });
  return !!match;
}

// Toggle mark (inline format)
function toggleMark(editor: Editor, format: string) {
  const isActive = isMarkActive(editor, format);
  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
}

function isMarkActive(editor: Editor, format: string) {
  const marks = Editor.marks(editor);
  return marks ? (marks as any)[format] === true : false;
}
```

## Keyboard Shortcuts

```tsx
import { KeyboardEvent } from "react";

function onKeyDown(event: KeyboardEvent, editor: Editor) {
  if (!event.ctrlKey && !event.metaKey) return;

  switch (event.key) {
    case "b": {
      event.preventDefault();
      toggleMark(editor, "bold");
      break;
    }
    case "i": {
      event.preventDefault();
      toggleMark(editor, "italic");
      break;
    }
    case "u": {
      event.preventDefault();
      toggleMark(editor, "underline");
      break;
    }
  }
}

// Use in Editable
<Editable onKeyDown={(e) => onKeyDown(e, editor)} />
```

## Serialization

```ts
import { Descendant, Text } from "slate";

// Serialize to HTML
function serializeToHTML(nodes: Descendant[]): string {
  return nodes.map((node) => {
    if (Text.isText(node)) {
      let text = node.text;
      if ((node as any).bold) text = `<strong>${text}</strong>`;
      if ((node as any).italic) text = `<em>${text}</em>`;
      return text;
    }

    const children = serializeToHTML(node.children);
    switch ((node as any).type) {
      case "heading-one": return `<h1>${children}</h1>`;
      case "heading-two": return `<h2>${children}</h2>`;
      case "block-quote": return `<blockquote>${children}</blockquote>`;
      case "paragraph": return `<p>${children}</p>`;
      default: return children;
    }
  }).join("");
}
```

## Additional Resources

- Slate: https://docs.slatejs.org/
- Concepts: https://docs.slatejs.org/concepts
- Walkthroughs: https://docs.slatejs.org/walkthroughs
