---
name: jodit-editor
description: Jodit Editor patterns covering WYSIWYG editing, toolbar configuration, custom plugins, file browser, content filtering, iframe mode, and React integration.
---

# Jodit Editor

This skill should be used when building WYSIWYG editors with Jodit. It covers toolbar configuration, custom plugins, file browser, content filtering, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Add a full-featured WYSIWYG editor with zero dependencies
- Configure toolbar buttons and editor behavior
- Create custom plugins and buttons
- Use file browser for media management
- Integrate Jodit with React

## Setup

```bash
npm install jodit jodit-react
```

## React Integration

```tsx
import JoditEditor from "jodit-react";
import { useRef, useMemo } from "react";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  const editorRef = useRef(null);

  const config = useMemo(() => ({
    readonly: false,
    height: 500,
    toolbarButtonSize: "middle" as const,
    buttons: [
      "bold", "italic", "underline", "strikethrough", "|",
      "ul", "ol", "|",
      "font", "fontsize", "paragraph", "|",
      "image", "table", "link", "|",
      "align", "undo", "redo", "|",
      "hr", "eraser", "fullsize", "source",
    ],
    uploader: {
      insertImageAsBase64URI: false,
      url: "/api/upload",
      format: "json",
      pathVariableName: "path",
    },
    placeholder: "Start writing...",
    showCharsCounter: true,
    showWordsCounter: true,
  }), []);

  return (
    <JoditEditor
      ref={editorRef}
      value={value}
      config={config}
      onBlur={(newContent) => onChange(newContent)}
    />
  );
}
```

## Vanilla JavaScript

```ts
import { Jodit } from "jodit";
import "jodit/es2021/jodit.min.css";

const editor = Jodit.make("#editor", {
  height: 500,
  buttons: [
    "bold", "italic", "underline", "|",
    "ul", "ol", "|",
    "image", "table", "link", "|",
    "source",
  ],
  placeholder: "Start writing...",
});

// Get content
const html = editor.value;

// Set content
editor.value = "<h1>Hello</h1><p>World</p>";

// Listen for changes
editor.events.on("change", (newValue: string) => {
  console.log("Changed:", newValue);
});

// Destroy
editor.destruct();
```

## Custom Plugin

```ts
import { Jodit } from "jodit";

Jodit.plugins.add("customHighlight", function (editor: Jodit) {
  editor.registerButton({
    name: "customHighlight",
    group: "insert",
  });

  editor.registerCommand("applyHighlight", (_command, _second, _third) => {
    const selection = editor.selection;
    if (selection.isCollapsed()) return;

    editor.selection.applyStyle(undefined, {
      style: { "background-color": "#ffff00" },
    });
  });

  editor.ui.registeredButtons.set("customHighlight", {
    name: "customHighlight",
    iconURL: "",
    text: "Highlight",
    tooltip: "Highlight selected text",
    command: "applyHighlight",
  } as any);
});
```

## Content Filtering

```ts
const config = {
  // Clean pasted content
  cleanHTML: {
    removeEmptyElements: true,
    fillEmptyParagraph: true,
    replaceNBSP: true,
  },
  // Allowed tags
  allowedTags: [
    "p", "br", "h1", "h2", "h3", "h4",
    "strong", "em", "u", "s", "a",
    "ul", "ol", "li",
    "img", "table", "tr", "td", "th",
    "blockquote", "pre", "code", "hr",
  ],
  // Disable specific plugins
  disablePlugins: ["video", "about"],
};
```

## Additional Resources

- Jodit: https://xdsoft.net/jodit/
- API: https://xdsoft.net/jodit/docs/
- React: https://github.com/jodit/jodit-react
