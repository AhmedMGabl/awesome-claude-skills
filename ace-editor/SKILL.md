---
name: ace-editor
description: Ace Editor patterns covering embeddable code editor, language modes, themes, autocomplete, snippets, search/replace, split view, and custom key bindings.
---

# Ace Editor

This skill should be used when embedding code editors with Ace. It covers language modes, themes, autocomplete, snippets, and custom configurations.

## When to Use This Skill

Use this skill when you need to:

- Embed lightweight code editors in web apps
- Support 100+ programming language modes
- Add autocomplete and snippet expansion
- Customize themes and key bindings
- Build split-pane editor layouts

## Setup

```bash
npm install ace-builds
# For React:
npm install react-ace
```

## React Integration

```tsx
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/mode-typescript";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/ext-searchbox";

function CodeEditor({ value, onChange, language = "typescript" }: {
  value: string;
  onChange: (value: string) => void;
  language?: string;
}) {
  return (
    <AceEditor
      mode={language}
      theme="monokai"
      value={value}
      onChange={onChange}
      name="code-editor"
      width="100%"
      height="400px"
      fontSize={14}
      showPrintMargin={false}
      showGutter={true}
      highlightActiveLine={true}
      setOptions={{
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        showLineNumbers: true,
        tabSize: 2,
        useWorker: false,
      }}
      editorProps={{ $blockScrolling: true }}
    />
  );
}
```

## Vanilla JavaScript Setup

```ts
import ace from "ace-builds";
import "ace-builds/src-noconflict/mode-javascript";
import "ace-builds/src-noconflict/theme-monokai";

const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/javascript");

// Configuration
editor.setOptions({
  fontSize: "14px",
  showPrintMargin: false,
  tabSize: 2,
  useSoftTabs: true,
  wrap: true,
  showGutter: true,
  highlightActiveLine: true,
  readOnly: false,
});

// Listen for changes
editor.session.on("change", () => {
  const content = editor.getValue();
  console.log("Content changed:", content);
});
```

## Custom Autocomplete

```ts
import "ace-builds/src-noconflict/ext-language_tools";

const customCompleter = {
  getCompletions: (editor: any, session: any, pos: any, prefix: string, callback: any) => {
    const completions = [
      { caption: "useState", value: "useState", meta: "React Hook", score: 1000 },
      { caption: "useEffect", value: "useEffect", meta: "React Hook", score: 999 },
      { caption: "useCallback", value: "useCallback", meta: "React Hook", score: 998 },
      { caption: "useMemo", value: "useMemo", meta: "React Hook", score: 997 },
    ];

    callback(null, completions.filter((c) => c.caption.startsWith(prefix)));
  },
};

editor.completers = [customCompleter, ...editor.completers];
```

## Annotations (Error Markers)

```ts
editor.session.setAnnotations([
  { row: 4, column: 0, text: "Missing semicolon", type: "error" },
  { row: 10, column: 0, text: "Unused variable 'x'", type: "warning" },
  { row: 15, column: 0, text: "Consider using const", type: "info" },
]);

// Clear annotations
editor.session.clearAnnotations();
```

## Key Bindings

```ts
editor.commands.addCommand({
  name: "saveFile",
  bindKey: { win: "Ctrl-S", mac: "Cmd-S" },
  exec: (editor) => {
    const content = editor.getValue();
    saveToServer(content);
  },
});

editor.commands.addCommand({
  name: "formatCode",
  bindKey: { win: "Ctrl-Shift-F", mac: "Cmd-Shift-F" },
  exec: async (editor) => {
    const formatted = await formatCode(editor.getValue());
    editor.setValue(formatted, -1);
  },
});
```

## Additional Resources

- Ace Editor: https://ace.c9.io/
- API Reference: https://ace.c9.io/#nav=api
- Kitchen Sink: https://ace.c9.io/build/kitchen-sink.html
