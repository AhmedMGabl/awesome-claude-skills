---
name: avalonia-ui
description: Avalonia UI patterns covering cross-platform XAML, MVVM with ReactiveUI, styles, control templates, data templates, and platform-specific rendering.
---

# Avalonia UI

This skill should be used when building cross-platform desktop and mobile apps with Avalonia UI. It covers XAML layouts, MVVM with ReactiveUI, styles, control templates, and platform rendering.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform .NET desktop apps (Windows, macOS, Linux)
- Create XAML-based UIs with data binding
- Implement MVVM with ReactiveUI or CommunityToolkit
- Design custom controls with styles and templates
- Target mobile platforms with Avalonia

## Project Setup

```bash
# Install template
dotnet new install Avalonia.Templates

# Create app
dotnet new avalonia.app -o MyApp
dotnet new avalonia.mvvm -o MyApp  # With MVVM template

cd MyApp
dotnet run
```

## Main Window

```xml
<!-- Views/MainWindow.axaml -->
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="using:MyApp.ViewModels"
        x:Class="MyApp.Views.MainWindow"
        x:DataType="vm:MainWindowViewModel"
        Title="MyApp" Width="800" Height="600">

    <Design.DataContext>
        <vm:MainWindowViewModel />
    </Design.DataContext>

    <DockPanel>
        <Menu DockPanel.Dock="Top">
            <MenuItem Header="_File">
                <MenuItem Header="_Open" Command="{Binding OpenCommand}" InputGesture="Ctrl+O" />
                <MenuItem Header="_Save" Command="{Binding SaveCommand}" InputGesture="Ctrl+S" />
                <Separator />
                <MenuItem Header="E_xit" Command="{Binding ExitCommand}" />
            </MenuItem>
        </Menu>

        <Grid ColumnDefinitions="250, 5, *" Margin="8">
            <ListBox Grid.Column="0"
                     ItemsSource="{Binding Items}"
                     SelectedItem="{Binding SelectedItem}">
                <ListBox.ItemTemplate>
                    <DataTemplate>
                        <StackPanel Spacing="4">
                            <TextBlock Text="{Binding Title}" FontWeight="Bold" />
                            <TextBlock Text="{Binding Description}" Foreground="Gray" FontSize="12" />
                        </StackPanel>
                    </DataTemplate>
                </ListBox.ItemTemplate>
            </ListBox>

            <GridSplitter Grid.Column="1" />

            <ContentControl Grid.Column="2"
                            Content="{Binding SelectedItem}"
                            Margin="8,0,0,0" />
        </Grid>
    </DockPanel>
</Window>
```

## ViewModel with ReactiveUI

```csharp
// ViewModels/MainWindowViewModel.cs
using ReactiveUI;
using System.Collections.ObjectModel;
using System.Reactive;
using System.Reactive.Linq;

public class MainWindowViewModel : ViewModelBase
{
    private Item? _selectedItem;
    private string _searchText = "";

    public ObservableCollection<Item> Items { get; } = new();

    public Item? SelectedItem
    {
        get => _selectedItem;
        set => this.RaiseAndSetIfChanged(ref _selectedItem, value);
    }

    public string SearchText
    {
        get => _searchText;
        set => this.RaiseAndSetIfChanged(ref _searchText, value);
    }

    public ReactiveCommand<Unit, Unit> OpenCommand { get; }
    public ReactiveCommand<Unit, Unit> SaveCommand { get; }
    public ReactiveCommand<Unit, Unit> ExitCommand { get; }

    public MainWindowViewModel()
    {
        var hasSelection = this.WhenAnyValue(x => x.SelectedItem)
            .Select(item => item != null);

        SaveCommand = ReactiveCommand.CreateFromTask(SaveAsync, hasSelection);
        OpenCommand = ReactiveCommand.CreateFromTask(OpenAsync);
        ExitCommand = ReactiveCommand.Create(() => { });

        // Auto-filter on search text change
        this.WhenAnyValue(x => x.SearchText)
            .Throttle(TimeSpan.FromMilliseconds(300))
            .ObserveOn(RxApp.MainThreadScheduler)
            .Subscribe(FilterItems);
    }

    private async Task OpenAsync()
    {
        // File picker via platform storage
    }

    private async Task SaveAsync()
    {
        // Save logic
    }

    private void FilterItems(string query)
    {
        // Filter items based on search text
    }
}
```

## Styles and Themes

```xml
<!-- App.axaml -->
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App">
    <Application.Styles>
        <FluentTheme />

        <!-- Custom styles -->
        <Style Selector="Button.primary">
            <Setter Property="Background" Value="#0066CC" />
            <Setter Property="Foreground" Value="White" />
            <Setter Property="CornerRadius" Value="6" />
            <Setter Property="Padding" Value="16,8" />
        </Style>

        <Style Selector="Button.primary:pointerover /template/ ContentPresenter">
            <Setter Property="Background" Value="#0052A3" />
        </Style>

        <Style Selector="TextBlock.heading">
            <Setter Property="FontSize" Value="24" />
            <Setter Property="FontWeight" Value="Bold" />
            <Setter Property="Margin" Value="0,0,0,8" />
        </Style>
    </Application.Styles>
</Application>
```

## Custom Control

```csharp
// Controls/StatusBadge.cs
public class StatusBadge : TemplatedControl
{
    public static readonly StyledProperty<string> TextProperty =
        AvaloniaProperty.Register<StatusBadge, string>(nameof(Text));

    public static readonly StyledProperty<BadgeType> TypeProperty =
        AvaloniaProperty.Register<StatusBadge, BadgeType>(nameof(Type));

    public string Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    public BadgeType Type
    {
        get => GetValue(TypeProperty);
        set => SetValue(TypeProperty, value);
    }
}

public enum BadgeType { Success, Warning, Error, Info }
```

```xml
<!-- Styles/StatusBadge.axaml -->
<Style Selector="local|StatusBadge">
    <Setter Property="Template">
        <ControlTemplate>
            <Border CornerRadius="12" Padding="8,4"
                    Background="{TemplateBinding Background}">
                <TextBlock Text="{TemplateBinding Text}"
                           FontSize="12" Foreground="White" />
            </Border>
        </ControlTemplate>
    </Setter>
</Style>
```

## Platform Storage (File Dialogs)

```csharp
var topLevel = TopLevel.GetTopLevel(this);
var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
{
    Title = "Open File",
    AllowMultiple = false,
    FileTypeFilter = new[]
    {
        new FilePickerFileType("Text Files") { Patterns = new[] { "*.txt", "*.md" } },
        FilePickerFileTypes.All,
    },
});

if (files.Count > 0)
{
    await using var stream = await files[0].OpenReadAsync();
    using var reader = new StreamReader(stream);
    var content = await reader.ReadToEndAsync();
}
```

## Additional Resources

- Avalonia Docs: https://docs.avaloniaui.net/
- Avalonia Samples: https://github.com/AvaloniaUI/Avalonia/tree/master/samples
- ReactiveUI: https://www.reactiveui.net/
