---
name: codemirror-v6
description: CodeMirror 6 patterns covering modular editor architecture, extensions, syntax highlighting, language support, autocompletion, linting, themes, keybindings, and React integration.
---

# CodeMirror 6

This skill should be used when building code editors with CodeMirror 6. It covers extensions, language support, autocompletion, linting, themes, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build code editors in web applications
- Add syntax highlighting and language support
- Implement autocompletion and linting
- Create custom extensions and keybindings
- Integrate CodeMirror with React

## Setup

```bash
npm install @codemirror/state @codemirror/view @codemirror/commands
npm install @codemirror/language @codemirror/autocomplete @codemirror/lint
npm install @codemirror/lang-javascript @codemirror/lang-python @codemirror/lang-html
npm install @codemirror/theme-one-dark
```

## Basic Setup

```ts
import { EditorState } from "@codemirror/state";
import { EditorView, keymap, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { javascript } from "@codemirror/lang-javascript";
import { oneDark } from "@codemirror/theme-one-dark";
import { syntaxHighlighting, defaultHighlightStyle } from "@codemirror/language";

const state = EditorState.create({
  doc: "console.log('Hello, world!');\n",
  extensions: [
    lineNumbers(),
    highlightActiveLine(),
    history(),
    syntaxHighlighting(defaultHighlightStyle),
    javascript({ typescript: true, jsx: true }),
    oneDark,
    keymap.of([...defaultKeymap, ...historyKeymap]),
  ],
});

const view = new EditorView({
  state,
  parent: document.getElementById("editor")!,
});
```

## React Integration

```tsx
import { useEffect, useRef } from "react";
import { EditorState } from "@codemirror/state";
import { EditorView, keymap, lineNumbers } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { javascript } from "@codemirror/lang-javascript";
import { oneDark } from "@codemirror/theme-one-dark";

function CodeEditor({ value, onChange, language = "javascript" }: {
  value: string;
  onChange?: (value: string) => void;
  language?: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        onChange?.(update.state.doc.toString());
      }
    });

    const state = EditorState.create({
      doc: value,
      extensions: [
        lineNumbers(),
        history(),
        javascript({ typescript: true }),
        oneDark,
        keymap.of([...defaultKeymap, ...historyKeymap]),
        updateListener,
      ],
    });

    const view = new EditorView({ state, parent: containerRef.current });
    viewRef.current = view;

    return () => view.destroy();
  }, []);

  return <div ref={containerRef} />;
}
```

## Autocompletion

```ts
import { autocompletion, CompletionContext } from "@codemirror/autocomplete";

function myCompletions(context: CompletionContext) {
  const word = context.matchBefore(/\w*/);
  if (!word || (word.from === word.to && !context.explicit)) return null;

  return {
    from: word.from,
    options: [
      { label: "console", type: "variable", info: "Console object" },
      { label: "document", type: "variable", info: "Document object" },
      { label: "function", type: "keyword" },
      { label: "const", type: "keyword" },
      { label: "let", type: "keyword" },
    ],
  };
}

const extensions = [
  autocompletion({ override: [myCompletions] }),
];
```

## Linting

```ts
import { linter, Diagnostic } from "@codemirror/lint";

const myLinter = linter((view) => {
  const diagnostics: Diagnostic[] = [];
  const doc = view.state.doc;

  for (let i = 1; i <= doc.lines; i++) {
    const line = doc.line(i);
    if (line.text.includes("TODO")) {
      diagnostics.push({
        from: line.from,
        to: line.to,
        severity: "warning",
        message: "TODO comment found",
      });
    }
  }

  return diagnostics;
});
```

## Custom Theme

```ts
import { EditorView } from "@codemirror/view";

const customTheme = EditorView.theme({
  "&": {
    color: "#e0e0e0",
    backgroundColor: "#1e1e1e",
    fontSize: "14px",
  },
  ".cm-content": { caretColor: "#528bff" },
  ".cm-cursor": { borderLeftColor: "#528bff" },
  ".cm-activeLine": { backgroundColor: "#2c313a" },
  ".cm-gutters": {
    backgroundColor: "#1e1e1e",
    color: "#636d83",
    border: "none",
  },
  ".cm-activeLineGutter": { backgroundColor: "#2c313a" },
});
```

## Read-Only and Dispatching

```ts
// Read-only mode
const readOnly = EditorState.readOnly.of(true);

// Dispatch changes programmatically
view.dispatch({
  changes: { from: 0, to: view.state.doc.length, insert: "new content" },
});

// Insert text at cursor
const cursor = view.state.selection.main.head;
view.dispatch({
  changes: { from: cursor, insert: "inserted text" },
});

// Get current content
const content = view.state.doc.toString();
```

## Additional Resources

- CodeMirror 6: https://codemirror.net/
- Extensions: https://codemirror.net/docs/extensions/
- Language Packages: https://codemirror.net/docs/community/
