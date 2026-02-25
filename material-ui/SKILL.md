---
name: material-ui
description: Material UI (MUI) component library covering theme customization, styled components, sx prop, responsive breakpoints, data grid, autocomplete, form components, dark mode, custom variants, and integration with React Hook Form and Next.js.
---

# Material UI (MUI)

This skill should be used when building React applications with Material UI. It covers theming, component customization, data grids, forms, and responsive design.

## When to Use This Skill

Use this skill when you need to:

- Build React UIs with Material Design components
- Customize MUI themes and create design systems
- Implement data tables with MUI DataGrid
- Create responsive layouts with the Grid system
- Integrate MUI with form libraries

## Theme Configuration

```typescript
// theme.ts
import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#6366f1", light: "#818cf8", dark: "#4f46e5" },
    secondary: { main: "#ec4899" },
    background: { default: "#fafafa", paper: "#ffffff" },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h1: { fontSize: "2.5rem", fontWeight: 700 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 8, padding: "8px 20px" },
      },
      variants: [
        {
          props: { variant: "dashed" as any },
          style: { border: "2px dashed", borderColor: "#6366f1" },
        },
      ],
    },
    MuiTextField: {
      defaultProps: { variant: "outlined", size: "small" },
    },
    MuiCard: {
      styleOverrides: {
        root: { boxShadow: "0 1px 3px rgba(0,0,0,0.12)" },
      },
    },
  },
});

export default theme;
```

## ThemeProvider Setup

```tsx
// App.tsx or layout.tsx
import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./theme";

function App({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
```

## Responsive Layout

```tsx
import { Box, Grid, Container, Stack, Typography } from "@mui/material";

function Dashboard() {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" sx={{ mb: 3 }}>Dashboard</Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard title="Revenue" value="$12,400" />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard title="Users" value="1,234" />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard title="Orders" value="567" />
        </Grid>
      </Grid>

      {/* Responsive hiding */}
      <Box sx={{ display: { xs: "none", md: "block" } }}>
        Desktop-only content
      </Box>
    </Container>
  );
}

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <Box sx={{ p: 3, bgcolor: "background.paper", borderRadius: 2, boxShadow: 1 }}>
      <Typography color="text.secondary" variant="body2">{title}</Typography>
      <Typography variant="h4" sx={{ mt: 1 }}>{value}</Typography>
    </Box>
  );
}
```

## DataGrid

```tsx
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { Chip } from "@mui/material";

const columns: GridColDef[] = [
  { field: "id", headerName: "ID", width: 80 },
  { field: "name", headerName: "Name", flex: 1, minWidth: 150 },
  { field: "email", headerName: "Email", flex: 1 },
  {
    field: "status",
    headerName: "Status",
    width: 120,
    renderCell: (params: GridRenderCellParams) => (
      <Chip
        label={params.value}
        color={params.value === "active" ? "success" : "default"}
        size="small"
      />
    ),
  },
];

function UsersTable({ rows }: { rows: any[] }) {
  return (
    <DataGrid
      rows={rows}
      columns={columns}
      pageSizeOptions={[10, 25, 50]}
      initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
      checkboxSelection
      disableRowSelectionOnClick
      sx={{ border: 0 }}
    />
  );
}
```

## Form with React Hook Form

```tsx
import { TextField, Button, MenuItem, Stack } from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  role: z.enum(["user", "admin"]),
});

type FormData = z.infer<typeof schema>;

function UserForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", role: "user" },
  });

  return (
    <Stack component="form" onSubmit={handleSubmit(onSubmit)} spacing={2} sx={{ maxWidth: 400 }}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Name" error={!!errors.name} helperText={errors.name?.message} />
        )}
      />
      <Controller
        name="email"
        control={control}
        render={({ field }) => (
          <TextField {...field} label="Email" error={!!errors.email} helperText={errors.email?.message} />
        )}
      />
      <Controller
        name="role"
        control={control}
        render={({ field }) => (
          <TextField {...field} select label="Role">
            <MenuItem value="user">User</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
          </TextField>
        )}
      />
      <Button type="submit" variant="contained">Save</Button>
    </Stack>
  );
}
```

## Dark Mode Toggle

```tsx
import { useState, useMemo } from "react";
import { ThemeProvider, createTheme, CssBaseline, IconButton } from "@mui/material";
import { DarkMode, LightMode } from "@mui/icons-material";

function App() {
  const [mode, setMode] = useState<"light" | "dark">("light");

  const theme = useMemo(() => createTheme({
    palette: { mode },
  }), [mode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <IconButton onClick={() => setMode(mode === "light" ? "dark" : "light")}>
        {mode === "light" ? <DarkMode /> : <LightMode />}
      </IconButton>
    </ThemeProvider>
  );
}
```

## Additional Resources

- MUI docs: https://mui.com/material-ui/getting-started/
- MUI X DataGrid: https://mui.com/x/react-data-grid/
- MUI theme builder: https://zenoo.github.io/mui-theme-creator/
