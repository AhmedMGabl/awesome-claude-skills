---
name: froala-editor
description: Froala Editor patterns covering WYSIWYG configuration, custom buttons, image/video upload, event handling, content manipulation, themes, and React integration.
---

# Froala Editor

This skill should be used when integrating Froala WYSIWYG editor into web applications. It covers configuration, custom buttons, uploads, events, and React integration.

## When to Use This Skill

Use this skill when you need to:

- Add a polished WYSIWYG editor with minimal setup
- Configure toolbar and plugin options
- Handle image and video uploads
- Create custom toolbar buttons
- Integrate Froala with React

## Setup

```bash
npm install froala-editor react-froala-wysiwyg
```

## React Integration

```tsx
import FroalaEditorComponent from "react-froala-wysiwyg";
import "froala-editor/css/froala_style.min.css";
import "froala-editor/css/froala_editor.pkgd.min.css";

function RichTextEditor({ value, onChange }: {
  value: string;
  onChange: (html: string) => void;
}) {
  return (
    <FroalaEditorComponent
      model={value}
      onModelChange={onChange}
      config={{
        placeholderText: "Start writing...",
        toolbarButtons: [
          ["bold", "italic", "underline", "strikeThrough"],
          ["formatOL", "formatUL", "outdent", "indent"],
          ["insertLink", "insertImage", "insertVideo", "insertTable"],
          ["paragraphFormat", "align", "color"],
          ["undo", "redo", "html"],
        ],
        heightMin: 300,
        heightMax: 600,
        charCounterCount: true,
        imageUploadURL: "/api/upload/image",
        imageUploadParam: "file",
        videoUploadURL: "/api/upload/video",
        videoUploadParam: "file",
      }}
    />
  );
}
```

## Event Handling

```tsx
<FroalaEditorComponent
  config={{
    events: {
      initialized: function () {
        console.log("Editor initialized");
      },
      contentChanged: function () {
        const html = this.html.get();
        console.log("Content changed:", html);
      },
      focus: function () {
        console.log("Editor focused");
      },
      blur: function () {
        console.log("Editor blurred");
      },
      "image.beforeUpload": function (images: FileList) {
        console.log("Uploading image:", images[0].name);
        return true; // return false to cancel
      },
      "image.uploaded": function (response: string) {
        const data = JSON.parse(response);
        console.log("Image uploaded:", data.link);
      },
      "image.error": function (error: any) {
        console.error("Image upload error:", error);
      },
    },
  }}
/>
```

## Custom Button

```tsx
import FroalaEditor from "froala-editor";

// Define custom button
FroalaEditor.DefineIcon("insertAlert", { NAME: "exclamation-triangle", SVG_KEY: "help" });
FroalaEditor.RegisterCommand("insertAlert", {
  title: "Insert Alert",
  focus: true,
  undo: true,
  refreshAfterCallback: true,
  callback: function () {
    this.html.insert(
      '<div class="alert alert-info" contenteditable="true">Alert content here</div><p></p>'
    );
  },
});

// Use in toolbar
<FroalaEditorComponent
  config={{
    toolbarButtons: [["bold", "italic"], ["insertAlert"]],
  }}
/>
```

## Content Manipulation

```tsx
import { useRef } from "react";

function EditorWithControls() {
  const editorRef = useRef<any>(null);

  const getHTML = () => editorRef.current?.editor?.html?.get();
  const setHTML = (html: string) => editorRef.current?.editor?.html?.set(html);
  const getText = () => editorRef.current?.editor?.html?.get(true); // text only
  const insertHTML = (html: string) => editorRef.current?.editor?.html?.insert(html);
  const clear = () => editorRef.current?.editor?.html?.set("");

  return (
    <>
      <FroalaEditorComponent ref={editorRef} config={{}} />
      <button onClick={() => console.log(getHTML())}>Get HTML</button>
      <button onClick={() => insertHTML("<hr />")}>Insert Divider</button>
      <button onClick={clear}>Clear</button>
    </>
  );
}
```

## Additional Resources

- Froala: https://froala.com/wysiwyg-editor/docs/
- React: https://froala.com/wysiwyg-editor/docs/framework-plugins/react/
- Options: https://froala.com/wysiwyg-editor/docs/options/
