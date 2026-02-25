---
name: cmdk-command
description: cmdk command palette patterns covering Command component setup, groups, items, search filtering, keyboard navigation, nested pages, async loading, custom rendering, and integration with shadcn/ui and Next.js.
---

# cmdk Command Palette

This skill should be used when building command palette interfaces with cmdk. It covers component setup, groups, search, keyboard navigation, nested pages, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build a command palette (Cmd+K) interface
- Add keyboard-navigable command menus
- Implement nested command pages
- Load async search results in command palette
- Integrate cmdk with shadcn/ui

## Basic Command Palette

```tsx
import { Command } from "cmdk";
import { useState, useEffect } from "react";

function CommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command Menu"
      className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
    >
      <div className="w-full max-w-lg rounded-lg bg-white shadow-2xl border">
        <Command.Input
          placeholder="Type a command or search..."
          className="w-full border-b px-4 py-3 text-lg outline-none"
        />
        <Command.List className="max-h-80 overflow-y-auto p-2">
          <Command.Empty className="p-4 text-center text-gray-500">
            No results found.
          </Command.Empty>

          <Command.Group heading="Actions" className="px-2 py-1 text-xs text-gray-500">
            <Command.Item
              onSelect={() => { createNewDocument(); setOpen(false); }}
              className="flex items-center gap-2 rounded px-3 py-2 cursor-pointer aria-selected:bg-blue-50"
            >
              📄 New Document
            </Command.Item>
            <Command.Item
              onSelect={() => { openSettings(); setOpen(false); }}
              className="flex items-center gap-2 rounded px-3 py-2 cursor-pointer aria-selected:bg-blue-50"
            >
              ⚙️ Settings
            </Command.Item>
          </Command.Group>

          <Command.Separator className="my-1 border-t" />

          <Command.Group heading="Navigation">
            <Command.Item onSelect={() => router.push("/dashboard")}>
              📊 Dashboard
            </Command.Item>
            <Command.Item onSelect={() => router.push("/projects")}>
              📁 Projects
            </Command.Item>
            <Command.Item onSelect={() => router.push("/team")}>
              👥 Team
            </Command.Item>
          </Command.Group>
        </Command.List>
      </div>
    </Command.Dialog>
  );
}
```

## Nested Pages

```tsx
import { Command } from "cmdk";
import { useState } from "react";

function NestedCommand() {
  const [pages, setPages] = useState<string[]>([]);
  const page = pages[pages.length - 1];

  return (
    <Command
      onKeyDown={(e) => {
        if (e.key === "Backspace" && !inputValue) {
          e.preventDefault();
          setPages((p) => p.slice(0, -1));
        }
      }}
    >
      <Command.Input placeholder="What do you need?" />
      <Command.List>
        {!page && (
          <>
            <Command.Item onSelect={() => setPages([...pages, "projects"])}>
              Search projects...
            </Command.Item>
            <Command.Item onSelect={() => setPages([...pages, "team"])}>
              Search team members...
            </Command.Item>
            <Command.Item onSelect={() => setPages([...pages, "settings"])}>
              Go to settings...
            </Command.Item>
          </>
        )}

        {page === "projects" && (
          <>
            <Command.Item>Project Alpha</Command.Item>
            <Command.Item>Project Beta</Command.Item>
            <Command.Item>Project Gamma</Command.Item>
          </>
        )}

        {page === "team" && (
          <>
            <Command.Item>Alice (Engineering)</Command.Item>
            <Command.Item>Bob (Design)</Command.Item>
            <Command.Item>Carol (Product)</Command.Item>
          </>
        )}
      </Command.List>
    </Command>
  );
}
```

## Async Search

```tsx
import { Command } from "cmdk";
import { useState, useEffect } from "react";

function AsyncCommand() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const controller = new AbortController();
    setLoading(true);

    fetch(`/api/search?q=${encodeURIComponent(query)}`, {
      signal: controller.signal,
    })
      .then((r) => r.json())
      .then((data) => {
        setResults(data.results);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => controller.abort();
  }, [query]);

  return (
    <Command shouldFilter={false}>
      <Command.Input value={query} onValueChange={setQuery} placeholder="Search..." />
      <Command.List>
        {loading && <Command.Loading>Searching...</Command.Loading>}
        <Command.Empty>No results found.</Command.Empty>
        {results.map((result) => (
          <Command.Item key={result.id} value={result.title}>
            <span>{result.title}</span>
            <span className="text-gray-400">{result.description}</span>
          </Command.Item>
        ))}
      </Command.List>
    </Command>
  );
}
```

## shadcn/ui Integration

```tsx
// Using shadcn/ui CommandDialog (built on cmdk)
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";

function ShadcnCommand() {
  const [open, setOpen] = useState(false);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>
            <span>Calendar</span>
            <CommandShortcut>⌘C</CommandShortcut>
          </CommandItem>
          <CommandItem>
            <span>Search</span>
            <CommandShortcut>⌘S</CommandShortcut>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Settings">
          <CommandItem>Profile</CommandItem>
          <CommandItem>Billing</CommandItem>
          <CommandItem>Preferences</CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

## Additional Resources

- cmdk docs: https://cmdk.paco.me/
- GitHub: https://github.com/pacocoursey/cmdk
- shadcn/ui Command: https://ui.shadcn.com/docs/components/command
