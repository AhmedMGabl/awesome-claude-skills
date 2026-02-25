---
name: lexical-editor
description: Lexical editor patterns covering extensible text framework, custom nodes, plugins, decorators, command system, collaboration, markdown support, and React integration.
---

# Lexical Editor

This skill should be used when building text editors with Meta's Lexical framework. It covers nodes, plugins, commands, decorators, collaboration, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build extensible rich text editors
- Create custom node types and plugins
- Handle complex editor commands
- Implement collaborative editing
- Build Markdown or plain text editors

## Setup

```bash
npm install lexical @lexical/react @lexical/rich-text @lexical/list @lexical/code
npm install @lexical/link @lexical/markdown @lexical/utils
```

## Basic React Editor

```tsx
import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { HistoryPlugin } from "@lexical/react/LexicalHistoryPlugin";
import { AutoFocusPlugin } from "@lexical/react/LexicalAutoFocusPlugin";
import { ListPlugin } from "@lexical/react/LexicalListPlugin";
import { LinkPlugin } from "@lexical/react/LexicalLinkPlugin";
import { MarkdownShortcutPlugin } from "@lexical/react/LexicalMarkdownShortcutPlugin";
import { HeadingNode, QuoteNode } from "@lexical/rich-text";
import { ListNode, ListItemNode } from "@lexical/list";
import { CodeNode, CodeHighlightNode } from "@lexical/code";
import { LinkNode, AutoLinkNode } from "@lexical/link";
import { TRANSFORMERS } from "@lexical/markdown";
import LexicalErrorBoundary from "@lexical/react/LexicalErrorBoundary";

const editorConfig = {
  namespace: "MyEditor",
  theme: {
    paragraph: "editor-paragraph",
    heading: { h1: "editor-h1", h2: "editor-h2", h3: "editor-h3" },
    list: { ul: "editor-ul", ol: "editor-ol", listitem: "editor-li" },
    text: { bold: "editor-bold", italic: "editor-italic", code: "editor-code" },
  },
  nodes: [HeadingNode, QuoteNode, ListNode, ListItemNode, CodeNode, CodeHighlightNode, LinkNode, AutoLinkNode],
  onError: (error: Error) => console.error(error),
};

function Editor() {
  return (
    <LexicalComposer initialConfig={editorConfig}>
      <div className="editor-container">
        <ToolbarPlugin />
        <RichTextPlugin
          contentEditable={<ContentEditable className="editor-input" />}
          placeholder={<div className="editor-placeholder">Start writing...</div>}
          ErrorBoundary={LexicalErrorBoundary}
        />
        <HistoryPlugin />
        <AutoFocusPlugin />
        <ListPlugin />
        <LinkPlugin />
        <MarkdownShortcutPlugin transformers={TRANSFORMERS} />
      </div>
    </LexicalComposer>
  );
}
```

## Toolbar Plugin

```tsx
import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { $getSelection, $isRangeSelection, FORMAT_TEXT_COMMAND } from "lexical";
import { $setBlocksType } from "@lexical/selection";
import { $createHeadingNode } from "@lexical/rich-text";
import { INSERT_ORDERED_LIST_COMMAND, INSERT_UNORDERED_LIST_COMMAND } from "@lexical/list";

function ToolbarPlugin() {
  const [editor] = useLexicalComposerContext();
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);

  useEffect(() => {
    return editor.registerUpdateListener(({ editorState }) => {
      editorState.read(() => {
        const selection = $getSelection();
        if ($isRangeSelection(selection)) {
          setIsBold(selection.hasFormat("bold"));
          setIsItalic(selection.hasFormat("italic"));
        }
      });
    });
  }, [editor]);

  return (
    <div className="toolbar">
      <button
        className={isBold ? "active" : ""}
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "bold")}
      >
        Bold
      </button>
      <button
        className={isItalic ? "active" : ""}
        onClick={() => editor.dispatchCommand(FORMAT_TEXT_COMMAND, "italic")}
      >
        Italic
      </button>
      <button onClick={() => {
        editor.update(() => {
          const selection = $getSelection();
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createHeadingNode("h1"));
          }
        });
      }}>
        H1
      </button>
      <button onClick={() => editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined)}>
        Bullet List
      </button>
    </div>
  );
}
```

## Custom Node

```ts
import { DecoratorNode, NodeKey, SerializedLexicalNode, Spread } from "lexical";

type SerializedCalloutNode = Spread<{ calloutType: string }, SerializedLexicalNode>;

export class CalloutNode extends DecoratorNode<JSX.Element> {
  __calloutType: string;

  static getType(): string { return "callout"; }
  static clone(node: CalloutNode): CalloutNode {
    return new CalloutNode(node.__calloutType, node.__key);
  }

  constructor(calloutType: string = "info", key?: NodeKey) {
    super(key);
    this.__calloutType = calloutType;
  }

  createDOM(): HTMLElement {
    const div = document.createElement("div");
    div.className = `callout callout-${this.__calloutType}`;
    return div;
  }

  updateDOM(): boolean { return false; }

  decorate(): JSX.Element {
    return <CalloutComponent type={this.__calloutType} nodeKey={this.__key} />;
  }

  static importJSON(json: SerializedCalloutNode): CalloutNode {
    return new CalloutNode(json.calloutType);
  }

  exportJSON(): SerializedCalloutNode {
    return { ...super.exportJSON(), type: "callout", calloutType: this.__calloutType };
  }
}
```

## OnChange Plugin

```tsx
import { OnChangePlugin } from "@lexical/react/LexicalOnChangePlugin";
import { $generateHtmlFromNodes } from "@lexical/html";

function EditorWithOnChange({ onChange }: { onChange: (html: string) => void }) {
  const [editor] = useLexicalComposerContext();

  return (
    <OnChangePlugin
      onChange={(editorState) => {
        editorState.read(() => {
          const html = $generateHtmlFromNodes(editor);
          onChange(html);
        });
      }}
    />
  );
}
```

## Additional Resources

- Lexical: https://lexical.dev/
- Plugins: https://lexical.dev/docs/react/plugins
- Nodes: https://lexical.dev/docs/concepts/nodes
