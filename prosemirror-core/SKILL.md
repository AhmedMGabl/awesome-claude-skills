---
name: prosemirror-core
description: ProseMirror patterns covering document model, schema definitions, transactions, plugins, decorations, input rules, key bindings, custom node views, and collaborative editing.
---

# ProseMirror Core

This skill should be used when building custom rich text editors with ProseMirror. It covers schemas, transactions, plugins, node views, and collaborative editing.

## When to Use This Skill

Use this skill when you need to:

- Build custom structured text editors
- Define document schemas with typed nodes/marks
- Create editor plugins and decorations
- Implement custom node views
- Handle collaborative editing with steps

## Setup

```bash
npm install prosemirror-model prosemirror-state prosemirror-view prosemirror-transform
npm install prosemirror-schema-basic prosemirror-schema-list prosemirror-history
npm install prosemirror-keymap prosemirror-inputrules prosemirror-commands
```

## Schema Definition

```ts
import { Schema, NodeSpec, MarkSpec } from "prosemirror-model";

const nodes: Record<string, NodeSpec> = {
  doc: { content: "block+" },
  paragraph: { content: "inline*", group: "block", parseDOM: [{ tag: "p" }], toDOM: () => ["p", 0] },
  heading: {
    attrs: { level: { default: 1 } },
    content: "inline*",
    group: "block",
    defining: true,
    parseDOM: [1, 2, 3].map((level) => ({ tag: `h${level}`, attrs: { level } })),
    toDOM: (node) => [`h${node.attrs.level}`, 0],
  },
  blockquote: { content: "block+", group: "block", defining: true, parseDOM: [{ tag: "blockquote" }], toDOM: () => ["blockquote", 0] },
  code_block: { content: "text*", marks: "", group: "block", code: true, defining: true, parseDOM: [{ tag: "pre", preserveWhitespace: "full" }], toDOM: () => ["pre", ["code", 0]] },
  text: { group: "inline" },
  hard_break: { inline: true, group: "inline", selectable: false, parseDOM: [{ tag: "br" }], toDOM: () => ["br"] },
};

const marks: Record<string, MarkSpec> = {
  strong: { parseDOM: [{ tag: "strong" }, { tag: "b" }, { style: "font-weight=bold" }], toDOM: () => ["strong", 0] },
  em: { parseDOM: [{ tag: "em" }, { tag: "i" }], toDOM: () => ["em", 0] },
  code: { parseDOM: [{ tag: "code" }], toDOM: () => ["code", 0] },
  link: {
    attrs: { href: {}, title: { default: null } },
    inclusive: false,
    parseDOM: [{ tag: "a[href]", getAttrs: (dom: HTMLElement) => ({ href: dom.getAttribute("href"), title: dom.getAttribute("title") }) }],
    toDOM: (mark) => ["a", mark.attrs, 0],
  },
};

const schema = new Schema({ nodes, marks });
```

## Editor Setup

```ts
import { EditorState } from "prosemirror-state";
import { EditorView } from "prosemirror-view";
import { history, undo, redo } from "prosemirror-history";
import { keymap } from "prosemirror-keymap";
import { baseKeymap } from "prosemirror-commands";

const state = EditorState.create({
  schema,
  plugins: [
    history(),
    keymap({ "Mod-z": undo, "Mod-y": redo, "Mod-Shift-z": redo }),
    keymap(baseKeymap),
  ],
});

const view = new EditorView(document.querySelector("#editor")!, {
  state,
  dispatchTransaction(transaction) {
    const newState = view.state.apply(transaction);
    view.updateState(newState);
    if (transaction.docChanged) {
      onDocChange(newState.doc.toJSON());
    }
  },
});
```

## Plugins

```ts
import { Plugin, PluginKey } from "prosemirror-state";
import { Decoration, DecorationSet } from "prosemirror-view";

const placeholderKey = new PluginKey("placeholder");

const placeholderPlugin = new Plugin({
  key: placeholderKey,
  props: {
    decorations(state) {
      const doc = state.doc;
      if (doc.childCount === 1 && doc.firstChild?.isTextblock && doc.firstChild.content.size === 0) {
        return DecorationSet.create(doc, [
          Decoration.widget(1, () => {
            const span = document.createElement("span");
            span.className = "placeholder";
            span.textContent = "Start writing...";
            return span;
          }),
        ]);
      }
      return DecorationSet.empty;
    },
  },
});
```

## Input Rules

```ts
import { inputRules, wrappingInputRule, textblockTypeInputRule } from "prosemirror-inputrules";

const headingRule = textblockTypeInputRule(
  /^(#{1,3})\s$/,
  schema.nodes.heading,
  (match) => ({ level: match[1].length })
);

const blockquoteRule = wrappingInputRule(/^\s*>\s$/, schema.nodes.blockquote);

const rules = inputRules({ rules: [headingRule, blockquoteRule] });
```

## Additional Resources

- ProseMirror: https://prosemirror.net/
- Guide: https://prosemirror.net/docs/guide/
- Reference: https://prosemirror.net/docs/ref/
