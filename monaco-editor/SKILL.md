---
name: monaco-editor
description: Monaco Editor patterns covering VS Code editor component, language services, IntelliSense, custom themes, diff editor, multi-model editing, markers, and React/webpack integration.
---

# Monaco Editor

This skill should be used when embedding VS Code's editor component with Monaco Editor. It covers language configuration, IntelliSense, themes, diff editing, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Embed VS Code's editor in web apps
- Configure language-specific IntelliSense
- Create custom themes and syntax highlighting
- Build diff editors for code comparison
- Integrate Monaco with React and webpack

## Setup

```bash
npm install monaco-editor
# For React:
npm install @monaco-editor/react
```

## React Integration

```tsx
import Editor, { DiffEditor, useMonaco } from "@monaco-editor/react";
import { useRef } from "react";

function CodeEditor({ value, onChange, language = "typescript" }: {
  value: string;
  onChange: (value: string) => void;
  language?: string;
}) {
  const editorRef = useRef<any>(null);

  function handleEditorDidMount(editor: any, monaco: any) {
    editorRef.current = editor;

    // Configure TypeScript
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ESNext,
      module: monaco.languages.typescript.ModuleKind.ESNext,
      strict: true,
      jsx: monaco.languages.typescript.JsxEmit.ReactJSX,
    });
  }

  return (
    <Editor
      height="400px"
      language={language}
      value={value}
      onChange={(val) => onChange(val || "")}
      onMount={handleEditorDidMount}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        tabSize: 2,
        wordWrap: "on",
        automaticLayout: true,
        scrollBeyondLastLine: false,
        padding: { top: 16 },
      }}
    />
  );
}
```

## Diff Editor

```tsx
function DiffViewer({ original, modified }: { original: string; modified: string }) {
  return (
    <DiffEditor
      height="500px"
      language="typescript"
      original={original}
      modified={modified}
      theme="vs-dark"
      options={{
        readOnly: true,
        renderSideBySide: true,
        originalEditable: false,
      }}
    />
  );
}
```

## Custom Theme

```ts
import { useMonaco } from "@monaco-editor/react";

function ThemeSetup() {
  const monaco = useMonaco();

  useEffect(() => {
    if (!monaco) return;

    monaco.editor.defineTheme("myTheme", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "comment", foreground: "6A9955", fontStyle: "italic" },
        { token: "keyword", foreground: "C586C0" },
        { token: "string", foreground: "CE9178" },
        { token: "number", foreground: "B5CEA8" },
        { token: "type", foreground: "4EC9B0" },
      ],
      colors: {
        "editor.background": "#1E1E2E",
        "editor.foreground": "#CDD6F4",
        "editor.lineHighlightBackground": "#2A2B3C",
        "editorCursor.foreground": "#F5E0DC",
      },
    });

    monaco.editor.setTheme("myTheme");
  }, [monaco]);
}
```

## Custom Completions

```ts
monaco.languages.registerCompletionItemProvider("typescript", {
  provideCompletionItems: (model, position) => {
    const word = model.getWordUntilPosition(position);
    const range = {
      startLineNumber: position.lineNumber,
      endLineNumber: position.lineNumber,
      startColumn: word.startColumn,
      endColumn: word.endColumn,
    };

    return {
      suggestions: [
        {
          label: "useState",
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: "const [${1:state}, set${2:State}] = useState(${3:initialValue});",
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: "React useState hook",
          range,
        },
        {
          label: "useEffect",
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: "useEffect(() => {\n\t${1}\n}, [${2}]);",
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: "React useEffect hook",
          range,
        },
      ],
    };
  },
});
```

## Markers (Error Highlighting)

```ts
// Set error markers
const model = editor.getModel();
if (model) {
  monaco.editor.setModelMarkers(model, "myApp", [
    {
      severity: monaco.MarkerSeverity.Error,
      message: "Type 'string' is not assignable to type 'number'",
      startLineNumber: 5,
      startColumn: 1,
      endLineNumber: 5,
      endColumn: 20,
    },
    {
      severity: monaco.MarkerSeverity.Warning,
      message: "Variable 'x' is declared but never used",
      startLineNumber: 3,
      startColumn: 7,
      endLineNumber: 3,
      endColumn: 8,
    },
  ]);
}
```

## Additional Resources

- Monaco Editor: https://microsoft.github.io/monaco-editor/
- API: https://microsoft.github.io/monaco-editor/docs.html
- React wrapper: https://github.com/suren-atoyan/monaco-react
