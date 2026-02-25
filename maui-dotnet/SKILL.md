---
name: maui-dotnet
description: .NET MAUI patterns covering cross-platform UI, XAML layouts, MVVM with CommunityToolkit, platform-specific code, dependency injection, and app lifecycle.
---

# .NET MAUI

This skill should be used when building cross-platform apps with .NET MAUI. It covers XAML layouts, MVVM, CommunityToolkit, platform-specific code, DI, and app lifecycle.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile and desktop apps with .NET
- Create XAML-based UI layouts with data binding
- Implement MVVM pattern with CommunityToolkit.Mvvm
- Access platform-specific APIs
- Configure dependency injection and app services

## Project Structure

```
MyApp/
├── App.xaml / App.xaml.cs
├── AppShell.xaml / AppShell.cs
├── MauiProgram.cs
├── Models/
├── ViewModels/
├── Views/
├── Services/
├── Platforms/
│   ├── Android/
│   ├── iOS/
│   ├── MacCatalyst/
│   └── Windows/
└── Resources/
    ├── Images/
    ├── Fonts/
    └── Styles/
```

## App Configuration

```csharp
// MauiProgram.cs
using CommunityToolkit.Maui;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // Services
        builder.Services.AddSingleton<IApiService, ApiService>();
        builder.Services.AddSingleton<ISettingsService, SettingsService>();

        // ViewModels
        builder.Services.AddTransient<MainViewModel>();
        builder.Services.AddTransient<DetailViewModel>();

        // Pages
        builder.Services.AddTransient<MainPage>();
        builder.Services.AddTransient<DetailPage>();

        return builder.Build();
    }
}
```

## Shell Navigation

```xml
<!-- AppShell.xaml -->
<Shell xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
       xmlns:views="clr-namespace:MyApp.Views">

    <TabBar>
        <ShellContent Title="Home" Icon="home.png"
                      ContentTemplate="{DataTemplate views:MainPage}" />
        <ShellContent Title="Settings" Icon="settings.png"
                      ContentTemplate="{DataTemplate views:SettingsPage}" />
    </TabBar>
</Shell>
```

```csharp
// Navigation
await Shell.Current.GoToAsync("//detail", new Dictionary<string, object>
{
    { "Item", selectedItem }
});

// Route registration
Routing.RegisterRoute("detail", typeof(DetailPage));
```

## XAML Page with Data Binding

```xml
<!-- Views/MainPage.xaml -->
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:vm="clr-namespace:MyApp.ViewModels"
             x:DataType="vm:MainViewModel">

    <RefreshView IsRefreshing="{Binding IsRefreshing}"
                 Command="{Binding RefreshCommand}">
        <CollectionView ItemsSource="{Binding Items}"
                        SelectionMode="Single"
                        SelectionChangedCommand="{Binding SelectItemCommand}"
                        SelectionChangedCommandParameter="{Binding SelectedItem, Source={RelativeSource Self}}">
            <CollectionView.ItemTemplate>
                <DataTemplate x:DataType="models:Item">
                    <Frame Padding="12" Margin="4">
                        <VerticalStackLayout Spacing="4">
                            <Label Text="{Binding Title}" FontSize="18" FontAttributes="Bold" />
                            <Label Text="{Binding Description}" TextColor="Gray" />
                        </VerticalStackLayout>
                    </Frame>
                </DataTemplate>
            </CollectionView.ItemTemplate>
        </CollectionView>
    </RefreshView>
</ContentPage>
```

## ViewModel with CommunityToolkit

```csharp
// ViewModels/MainViewModel.cs
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class MainViewModel : ObservableObject
{
    private readonly IApiService _api;

    [ObservableProperty]
    private ObservableCollection<Item> _items = new();

    [ObservableProperty]
    private bool _isRefreshing;

    public MainViewModel(IApiService api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        IsRefreshing = true;
        var results = await _api.GetItemsAsync();
        Items = new ObservableCollection<Item>(results);
        IsRefreshing = false;
    }

    [RelayCommand]
    private async Task SelectItemAsync(Item item)
    {
        if (item is null) return;
        await Shell.Current.GoToAsync("detail", new Dictionary<string, object>
        {
            { "Item", item }
        });
    }
}
```

## Platform-Specific Code

```csharp
// Conditional compilation
#if ANDROID
    var intent = new Android.Content.Intent(Android.Content.Intent.ActionView);
#elif IOS
    UIKit.UIApplication.SharedApplication.OpenUrl(new NSUrl(url));
#endif

// Platform service
public partial class DeviceService
{
    public partial string GetDeviceId();
}

// Platforms/Android/DeviceService.cs
public partial class DeviceService
{
    public partial string GetDeviceId() =>
        Android.Provider.Settings.Secure.GetString(
            Android.App.Application.Context.ContentResolver,
            Android.Provider.Settings.Secure.AndroidId);
}
```

## Additional Resources

- .NET MAUI Docs: https://learn.microsoft.com/dotnet/maui/
- CommunityToolkit.Mvvm: https://learn.microsoft.com/dotnet/communitytoolkit/mvvm/
- MAUI Samples: https://github.com/dotnet/maui-samples
