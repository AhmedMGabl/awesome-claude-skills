---
name: shadcn-patterns
description: shadcn/ui advanced patterns covering component composition, form integration with React Hook Form and Zod, data table patterns, theme customization, command palette, toast notifications, and custom component variants.
---

# shadcn/ui Patterns

This skill should be used when building advanced UI patterns with shadcn/ui. It covers component composition, form integration, data tables, theming, and custom variants.

## When to Use This Skill

Use this skill when you need to:

- Build complex forms with shadcn/ui and Zod validation
- Create data tables with sorting, filtering, and pagination
- Compose components for advanced UI patterns
- Customize themes and create component variants
- Build command palettes, sheets, and dialog flows

## Form with Validation

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const schema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  role: z.enum(["admin", "user", "editor"]),
});

function UserForm({ onSubmit }: { onSubmit: (data: z.infer<typeof schema>) => void }) {
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", role: "user" },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl><Input placeholder="John Doe" {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl><Input type="email" {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="editor">Editor</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
```

## Data Table

```tsx
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, ArrowUpDown } from "lucide-react";

interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

function DataTable<T extends { id: string }>({
  data,
  columns,
  onEdit,
  onDelete,
}: {
  data: T[];
  columns: Column<T>[];
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
}) {
  const [sortKey, setSortKey] = useState<keyof T | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sorted = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortKey], bVal = b[sortKey];
      const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((col) => (
            <TableHead key={String(col.key)}>
              {col.sortable ? (
                <Button variant="ghost" onClick={() => {
                  if (sortKey === col.key) setSortDir(sortDir === "asc" ? "desc" : "asc");
                  else { setSortKey(col.key); setSortDir("asc"); }
                }}>
                  {col.label} <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
              ) : col.label}
            </TableHead>
          ))}
          <TableHead />
        </TableRow>
      </TableHeader>
      <TableBody>
        {sorted.map((row) => (
          <TableRow key={row.id}>
            {columns.map((col) => (
              <TableCell key={String(col.key)}>
                {col.render ? col.render(row[col.key], row) : String(row[col.key])}
              </TableCell>
            ))}
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon"><MoreHorizontal /></Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  {onEdit && <DropdownMenuItem onClick={() => onEdit(row)}>Edit</DropdownMenuItem>}
                  {onDelete && <DropdownMenuItem onClick={() => onDelete(row)}>Delete</DropdownMenuItem>}
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

## Command Palette

```tsx
import {
  CommandDialog, CommandEmpty, CommandGroup,
  CommandInput, CommandItem, CommandList,
} from "@/components/ui/command";

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
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => router.push("/dashboard")}>Dashboard</CommandItem>
          <CommandItem onSelect={() => router.push("/settings")}>Settings</CommandItem>
        </CommandGroup>
        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => { setOpen(false); createNew(); }}>Create New</CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

## Toast Notifications

```tsx
import { useToast } from "@/hooks/use-toast";

function SaveButton() {
  const { toast } = useToast();

  const handleSave = async () => {
    try {
      await saveData();
      toast({ title: "Saved", description: "Changes saved successfully." });
    } catch {
      toast({
        title: "Error",
        description: "Failed to save. Please try again.",
        variant: "destructive",
      });
    }
  };

  return <Button onClick={handleSave}>Save</Button>;
}
```

## Additional Resources

- shadcn/ui docs: https://ui.shadcn.com/docs
- Components: https://ui.shadcn.com/docs/components
- Themes: https://ui.shadcn.com/themes
