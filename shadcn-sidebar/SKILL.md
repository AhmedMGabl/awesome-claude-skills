---
name: shadcn-sidebar
description: shadcn/ui sidebar patterns covering collapsible navigation, sidebar provider, menu items, groups, submenus, mobile responsive drawer, keyboard shortcuts, and persistent state management.
---

# shadcn Sidebar

This skill should be used when building sidebar navigation with shadcn/ui. It covers collapsible sidebars, menu items, groups, responsive behavior, and state management.

## When to Use This Skill

Use this skill when you need to:

- Build collapsible sidebar navigation
- Create hierarchical menu structures
- Handle responsive sidebar behavior
- Persist sidebar open/collapsed state
- Add keyboard shortcuts for sidebar toggle

## Setup

```bash
npx shadcn@latest add sidebar
```

## Basic Sidebar

```tsx
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup,
  SidebarGroupContent, SidebarGroupLabel, SidebarHeader,
  SidebarMenu, SidebarMenuButton, SidebarMenuItem,
  SidebarProvider, SidebarTrigger,
} from "@/components/ui/sidebar";
import { Home, Settings, Users, FileText, BarChart } from "lucide-react";

const menuItems = [
  { title: "Dashboard", icon: Home, url: "/" },
  { title: "Users", icon: Users, url: "/users" },
  { title: "Documents", icon: FileText, url: "/documents" },
  { title: "Analytics", icon: BarChart, url: "/analytics" },
  { title: "Settings", icon: Settings, url: "/settings" },
];

function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-2">
          <span className="font-bold text-lg">My App</span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton>
              <Settings />
              <span>Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}

// Layout wrapper
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1">
        <header className="flex items-center gap-2 p-4 border-b">
          <SidebarTrigger />
          <h1>Page Title</h1>
        </header>
        <div className="p-4">{children}</div>
      </main>
    </SidebarProvider>
  );
}
```

## Collapsible Groups

```tsx
import {
  Collapsible, CollapsibleContent, CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";

function CollapsibleSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <Collapsible defaultOpen className="group/collapsible">
          <SidebarGroup>
            <SidebarGroupLabel asChild>
              <CollapsibleTrigger className="flex w-full items-center justify-between">
                Team
                <ChevronDown className="transition-transform group-data-[state=open]/collapsible:rotate-180" />
              </CollapsibleTrigger>
            </SidebarGroupLabel>
            <CollapsibleContent>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton>Members</SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton>Roles</SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton>Invitations</SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </SidebarGroup>
        </Collapsible>
      </SidebarContent>
    </Sidebar>
  );
}
```

## Sidebar with Submenus

```tsx
import {
  SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem,
} from "@/components/ui/sidebar";

function SidebarWithSubmenus() {
  return (
    <SidebarMenu>
      <Collapsible asChild defaultOpen>
        <SidebarMenuItem>
          <CollapsibleTrigger asChild>
            <SidebarMenuButton>
              <FileText />
              <span>Documents</span>
              <ChevronDown className="ml-auto transition-transform group-data-[state=open]:rotate-180" />
            </SidebarMenuButton>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <SidebarMenuSub>
              <SidebarMenuSubItem>
                <SidebarMenuSubButton asChild>
                  <a href="/docs/drafts">Drafts</a>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
              <SidebarMenuSubItem>
                <SidebarMenuSubButton asChild>
                  <a href="/docs/published">Published</a>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
              <SidebarMenuSubItem>
                <SidebarMenuSubButton asChild>
                  <a href="/docs/archived">Archived</a>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            </SidebarMenuSub>
          </CollapsibleContent>
        </SidebarMenuItem>
      </Collapsible>
    </SidebarMenu>
  );
}
```

## Controlled State

```tsx
"use client";
import { useSidebar } from "@/components/ui/sidebar";

function SidebarControls() {
  const { open, setOpen, toggleSidebar, isMobile } = useSidebar();

  return (
    <div>
      <button onClick={toggleSidebar}>
        {open ? "Collapse" : "Expand"} Sidebar
      </button>
      {isMobile && <p>Mobile view active</p>}
    </div>
  );
}
```

## Additional Resources

- shadcn Sidebar: https://ui.shadcn.com/docs/components/sidebar
- shadcn/ui: https://ui.shadcn.com/
