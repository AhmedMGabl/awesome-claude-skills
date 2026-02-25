---
name: draft-js
description: Draft.js patterns covering rich text editing, content state model, entity maps, custom block components, decorator patterns, inline styles, and React integration.
---

# Draft.js

This skill should be used when building rich text editors with Draft.js. It covers content state, entities, custom blocks, decorators, inline styles, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Build rich text editors in React
- Work with the ContentState immutable model
- Create custom block components
- Implement decorator patterns for mentions/hashtags
- Handle entities for links and media

## Setup

```bash
npm install draft-js @types/draft-js
```

## Basic Editor

```tsx
import { Editor, EditorState, RichUtils } from "draft-js";
import "draft-js/dist/Draft.css";
import { useState, useCallback } from "react";

function RichTextEditor() {
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());

  const handleKeyCommand = useCallback((command: string, state: EditorState) => {
    const newState = RichUtils.handleKeyCommand(state, command);
    if (newState) {
      setEditorState(newState);
      return "handled";
    }
    return "not-handled";
  }, []);

  return (
    <div className="editor-container">
      <Toolbar editorState={editorState} onChange={setEditorState} />
      <Editor
        editorState={editorState}
        onChange={setEditorState}
        handleKeyCommand={handleKeyCommand}
        placeholder="Start writing..."
      />
    </div>
  );
}
```

## Toolbar with Inline Styles

```tsx
function Toolbar({ editorState, onChange }: {
  editorState: EditorState;
  onChange: (state: EditorState) => void;
}) {
  const toggleInlineStyle = (style: string) => {
    onChange(RichUtils.toggleInlineStyle(editorState, style));
  };

  const toggleBlockType = (blockType: string) => {
    onChange(RichUtils.toggleBlockType(editorState, blockType));
  };

  const currentStyle = editorState.getCurrentInlineStyle();

  return (
    <div className="toolbar">
      {["BOLD", "ITALIC", "UNDERLINE", "CODE"].map((style) => (
        <button
          key={style}
          onMouseDown={(e) => { e.preventDefault(); toggleInlineStyle(style); }}
          className={currentStyle.has(style) ? "active" : ""}
        >
          {style}
        </button>
      ))}
      {[
        { label: "H1", block: "header-one" },
        { label: "H2", block: "header-two" },
        { label: "UL", block: "unordered-list-item" },
        { label: "OL", block: "ordered-list-item" },
        { label: "Code", block: "code-block" },
        { label: "Quote", block: "blockquote" },
      ].map(({ label, block }) => (
        <button key={block} onMouseDown={(e) => { e.preventDefault(); toggleBlockType(block); }}>
          {label}
        </button>
      ))}
    </div>
  );
}
```

## Entities (Links)

```tsx
import { EditorState, RichUtils, Modifier, ContentState } from "draft-js";

function addLink(editorState: EditorState, url: string): EditorState {
  const contentState = editorState.getCurrentContent();
  const contentWithEntity = contentState.createEntity("LINK", "MUTABLE", { url });
  const entityKey = contentWithEntity.getLastCreatedEntityKey();

  const newEditorState = EditorState.set(editorState, {
    currentContent: contentWithEntity,
  });

  return RichUtils.toggleLink(
    newEditorState,
    newEditorState.getSelection(),
    entityKey
  );
}

function removeLink(editorState: EditorState): EditorState {
  return RichUtils.toggleLink(editorState, editorState.getSelection(), null);
}
```

## Custom Block Component

```tsx
import { ContentBlock, ContentState } from "draft-js";

function ImageBlock({ block, contentState }: {
  block: ContentBlock;
  contentState: ContentState;
}) {
  const entity = contentState.getEntity(block.getEntityAt(0));
  const { src, alt } = entity.getData();

  return (
    <div className="image-block">
      <img src={src} alt={alt} style={{ maxWidth: "100%" }} />
    </div>
  );
}

function blockRendererFn(block: ContentBlock) {
  if (block.getType() === "atomic") {
    return {
      component: ImageBlock,
      editable: false,
    };
  }
  return null;
}

// Use in Editor
<Editor
  editorState={editorState}
  onChange={setEditorState}
  blockRendererFn={blockRendererFn}
/>
```

## Decorator (Mention/Hashtag Highlighting)

```tsx
import { CompositeDecorator, ContentBlock, ContentState } from "draft-js";

function findMentions(
  block: ContentBlock,
  callback: (start: number, end: number) => void,
) {
  const text = block.getText();
  const regex = /@\w+/g;
  let match;
  while ((match = regex.test(text), match !== false && regex.lastIndex > 0)) {
    const start = regex.lastIndex - RegExp.lastMatch.length;
    callback(start, regex.lastIndex);
    if (regex.lastIndex >= text.length) break;
  }
}

function MentionSpan({ children }: { children: React.ReactNode }) {
  return <span className="mention" style={{ color: "#1890ff" }}>{children}</span>;
}

const decorator = new CompositeDecorator([
  { strategy: findMentions, component: MentionSpan },
]);

// Create editor state with decorator
const editorState = EditorState.createEmpty(decorator);
```

## Convert to/from HTML

```tsx
import { convertToRaw, convertFromRaw, ContentState } from "draft-js";
import draftToHtml from "draftjs-to-html";
import htmlToDraft from "html-to-draftjs";

// To HTML
function toHTML(editorState: EditorState): string {
  const rawContent = convertToRaw(editorState.getCurrentContent());
  return draftToHtml(rawContent);
}

// From HTML
function fromHTML(html: string): EditorState {
  const { contentBlocks, entityMap } = htmlToDraft(html);
  const contentState = ContentState.createFromBlockArray(contentBlocks, entityMap);
  return EditorState.createWithContent(contentState);
}

// To/from raw JSON (for storage)
function toJSON(editorState: EditorState) {
  return JSON.stringify(convertToRaw(editorState.getCurrentContent()));
}

function fromJSON(raw: string): EditorState {
  return EditorState.createWithContent(convertFromRaw(JSON.parse(raw)));
}
```

## Additional Resources

- Draft.js: https://draftjs.org/
- API: https://draftjs.org/docs/api-reference-editor
- Examples: https://draftjs.org/docs/advanced-topics-decorators
