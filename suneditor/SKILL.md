---
name: suneditor
description: SunEditor patterns covering lightweight WYSIWYG editing, toolbar customization, plugin system, image upload, content manipulation, responsive design, and React integration.
---

# SunEditor

This skill should be used when building lightweight WYSIWYG editors with SunEditor. It covers toolbar customization, plugins, image upload, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Add a lightweight WYSIWYG editor with no framework dependencies
- Customize toolbar buttons and layouts
- Handle image and file uploads
- Integrate SunEditor with React
- Build multi-language editors

## Setup

```bash
npm install suneditor suneditor-react
```

## React Integration

```tsx
import SunEditor from "suneditor-react";
import "suneditor/dist/css/suneditor.min.css";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  return (
    <SunEditor
      defaultValue={value}
      onChange={onChange}
      setOptions={{
        height: "400px",
        buttonList: [
          ["undo", "redo"],
          ["font", "fontSize", "formatBlock"],
          ["bold", "underline", "italic", "strike"],
          ["fontColor", "hiliteColor"],
          ["align", "list", "lineHeight"],
          ["outdent", "indent"],
          ["table", "link", "image", "video"],
          ["fullScreen", "showBlocks", "codeView"],
          ["removeFormat"],
        ],
        font: ["Arial", "Georgia", "Tahoma", "Verdana", "Courier New"],
        fontSize: [12, 14, 16, 18, 20, 24, 28, 36],
      }}
      setDefaultStyle="font-family: Arial; font-size: 16px;"
    />
  );
}
```

## Image Upload

```tsx
<SunEditor
  onImageUploadBefore={(files, info, uploadHandler) => {
    const file = files[0];
    const formData = new FormData();
    formData.append("file", file);

    fetch("/api/upload", { method: "POST", body: formData })
      .then((res) => res.json())
      .then(({ url }) => {
        const response = {
          result: [{ url, name: file.name, size: file.size }],
        };
        uploadHandler(response);
      })
      .catch(() => uploadHandler("Upload failed"));

    return undefined;
  }}
  onImageUpload={(targetElement, index, state, info, remainingFilesCount) => {
    console.log("Image uploaded:", info.src);
  }}
  onImageUploadError={(errorMessage) => {
    console.error("Upload error:", errorMessage);
  }}
/>
```

## Event Handling

```tsx
<SunEditor
  onChange={(content) => console.log("Changed:", content)}
  onBlur={(event, content) => console.log("Blur:", content)}
  onFocus={(event) => console.log("Focused")}
  onLoad={(reload) => console.log("Loaded, reload:", reload)}
  onInput={(event) => console.log("Input event")}
  onKeyDown={(event) => console.log("Key:", event.key)}
  onPaste={(event, cleanData, maxCharCount) => {
    console.log("Pasted:", cleanData);
  }}
/>
```

## Editor Instance Methods

```tsx
import { useRef } from "react";
import SunEditor from "suneditor-react";
import SunEditorCore from "suneditor/src/lib/core";

function EditorWithControls() {
  const editorRef = useRef<SunEditorCore>();

  const getSunEditorInstance = (sunEditor: SunEditorCore) => {
    editorRef.current = sunEditor;
  };

  const getContent = () => editorRef.current?.getContents(false);
  const setContent = (html: string) => editorRef.current?.setContents(html);
  const insertHTML = (html: string) => editorRef.current?.insertHTML(html);
  const getText = () => editorRef.current?.getText();
  const disable = () => editorRef.current?.disabled();
  const enable = () => editorRef.current?.enabled();
  const readOnly = (on: boolean) => editorRef.current?.readOnly(on);

  return (
    <>
      <SunEditor getSunEditorInstance={getSunEditorInstance} />
      <button onClick={() => console.log(getContent())}>Get Content</button>
      <button onClick={() => insertHTML("<hr />")}>Insert Divider</button>
    </>
  );
}
```

## Additional Resources

- SunEditor: https://github.com/JiHong88/SunEditor
- React: https://github.com/mkhstar/suneditor-react
- Options: http://suneditor.com/sample/html/options.html
