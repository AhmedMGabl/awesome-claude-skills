---
name: milkdown-editor
description: Milkdown editor patterns covering plugin-driven Markdown editing, ProseMirror integration, custom node schemas, collaborative editing, slash commands, toolbar customization, and React/Vue integration.
---

# Milkdown Editor

This skill should be used when building Markdown editors with Milkdown. It covers plugins, custom nodes, slash commands, collaborative editing, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build WYSIWYG Markdown editors
- Add custom block types and inline marks
- Implement slash commands and toolbars
- Enable collaborative editing
- Integrate with React or Vue

## Setup

```bash
npm install @milkdown/core @milkdown/preset-commonmark @milkdown/theme-nord
npm install @milkdown/react # for React
npm install @milkdown/plugin-slash @milkdown/plugin-tooltip @milkdown/plugin-history
```

## Basic React Setup

```tsx
import { Editor, rootCtx, defaultValueCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";
import { nord } from "@milkdown/theme-nord";
import { history } from "@milkdown/plugin-history";
import { Milkdown, MilkdownProvider, useEditor } from "@milkdown/react";

function MilkdownEditor({ defaultValue, onChange }: {
  defaultValue?: string;
  onChange?: (markdown: string) => void;
}) {
  useEditor((root) =>
    Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root);
        if (defaultValue) ctx.set(defaultValueCtx, defaultValue);
      })
      .use(nord)
      .use(commonmark)
      .use(history),
    []
  );

  return <Milkdown />;
}

export default function MarkdownEditor(props: { defaultValue?: string }) {
  return (
    <MilkdownProvider>
      <MilkdownEditor {...props} />
    </MilkdownProvider>
  );
}
```

## Slash Commands

```tsx
import { slashFactory } from "@milkdown/plugin-slash";

const slash = slashFactory("my-slash");

// Configure slash commands
const slashPlugin = slash.configure({
  config: (ctx) => ({
    content: document.createElement("div"),
    shouldShow: (view, prevState) => {
      const { selection } = view.state;
      const node = view.state.doc.nodeAt(selection.from - 1);
      return node?.textContent === "/";
    },
  }),
  items: [
    {
      label: "Heading 1",
      icon: "H1",
      onSelect: (ctx) => {
        const commands = ctx.get(commandsCtx);
        commands.call(turnIntoTextCommand.key, { level: 1 });
      },
    },
    {
      label: "Bullet List",
      icon: "List",
      onSelect: (ctx) => {
        const commands = ctx.get(commandsCtx);
        commands.call(wrapInBulletListCommand.key);
      },
    },
    {
      label: "Code Block",
      icon: "Code",
      onSelect: (ctx) => {
        const commands = ctx.get(commandsCtx);
        commands.call(createCodeBlockCommand.key);
      },
    },
  ],
});
```

## Custom Node Plugin

```ts
import { $node, $command } from "@milkdown/utils";
import { InputRule } from "@milkdown/prose/inputrules";

// Custom callout block
const calloutNode = $node("callout", () => ({
  content: "block+",
  group: "block",
  defining: true,
  attrs: {
    type: { default: "info" },
  },
  parseDOM: [
    {
      tag: "div[data-callout]",
      getAttrs: (dom: HTMLElement) => ({
        type: dom.getAttribute("data-callout-type") || "info",
      }),
    },
  ],
  toDOM: (node) => [
    "div",
    { "data-callout": "", "data-callout-type": node.attrs.type, class: `callout callout-${node.attrs.type}` },
    0,
  ],
  parseMarkdown: {
    match: (node) => node.type === "containerDirective" && node.name === "callout",
    runner: (state, node, type) => {
      state.openNode(type, { type: node.attributes?.type || "info" });
      state.next(node.children);
      state.closeNode();
    },
  },
  toMarkdown: {
    match: (node) => node.type.name === "callout",
    runner: (state, node) => {
      state.openNode("containerDirective", undefined, { name: "callout", attributes: { type: node.attrs.type } });
      state.next(node.content);
      state.closeNode();
    },
  },
}));

// Register with editor
Editor.make()
  .use(commonmark)
  .use(calloutNode);
```

## Toolbar Plugin

```tsx
import { tooltipFactory } from "@milkdown/plugin-tooltip";

const tooltip = tooltipFactory("toolbar");

const toolbarPlugin = tooltip.configure({
  config: (ctx) => ({
    content: (view) => {
      const div = document.createElement("div");
      div.className = "toolbar";

      const boldBtn = document.createElement("button");
      boldBtn.textContent = "B";
      boldBtn.onclick = () => {
        const commands = ctx.get(commandsCtx);
        commands.call(toggleStrongCommand.key);
      };

      const italicBtn = document.createElement("button");
      italicBtn.textContent = "I";
      italicBtn.onclick = () => {
        const commands = ctx.get(commandsCtx);
        commands.call(toggleEmphasisCommand.key);
      };

      div.append(boldBtn, italicBtn);
      return div;
    },
    shouldShow: (view) => {
      const { selection } = view.state;
      return !selection.empty;
    },
  }),
});
```

## Get/Set Markdown Content

```tsx
import { editorViewCtx, serializerCtx, parserCtx } from "@milkdown/core";

function EditorWithControls() {
  const { get } = useEditor(/* ... */);

  function getMarkdown() {
    const editor = get();
    if (!editor) return "";
    const ctx = editor.ctx;
    const view = ctx.get(editorViewCtx);
    const serializer = ctx.get(serializerCtx);
    return serializer(view.state.doc);
  }

  function setMarkdown(content: string) {
    const editor = get();
    if (!editor) return;
    const ctx = editor.ctx;
    const view = ctx.get(editorViewCtx);
    const parser = ctx.get(parserCtx);
    const doc = parser(content);
    const tr = view.state.tr.replaceWith(0, view.state.doc.content.size, doc.content);
    view.dispatch(tr);
  }

  return (
    <div>
      <Milkdown />
      <button onClick={() => console.log(getMarkdown())}>Get Markdown</button>
    </div>
  );
}
```

## Additional Resources

- Milkdown: https://milkdown.dev/
- Plugins: https://milkdown.dev/docs/plugin/using-plugins
- React: https://milkdown.dev/docs/recipes/react
