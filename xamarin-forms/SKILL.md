---
name: xamarin-forms
description: Xamarin.Forms patterns covering XAML layouts, MVVM data binding, dependency services, custom renderers, effects, navigation, and platform-specific code.
---

# Xamarin.Forms

This skill should be used when building cross-platform mobile apps with Xamarin.Forms. It covers XAML layouts, MVVM, dependency services, custom renderers, effects, and navigation.

## When to Use This Skill

Use this skill when you need to:

- Build cross-platform mobile apps with Xamarin.Forms
- Create XAML-based UI with data binding
- Implement MVVM architecture
- Access platform-specific APIs via DependencyService
- Create custom renderers for native controls

## Project Structure

```
MyApp/
├── MyApp/                    # Shared project
│   ├── App.xaml / App.xaml.cs
│   ├── Models/
│   ├── ViewModels/
│   ├── Views/
│   ├── Services/
│   └── Converters/
├── MyApp.Android/            # Android-specific
│   ├── MainActivity.cs
│   └── Renderers/
├── MyApp.iOS/                # iOS-specific
│   ├── AppDelegate.cs
│   └── Renderers/
└── MyApp.UWP/                # UWP-specific
```

## XAML Page

```xml
<!-- Views/MainPage.xaml -->
<ContentPage xmlns="http://xamarin.com/schemas/2014/forms"
             xmlns:vm="clr-namespace:MyApp.ViewModels"
             Title="Items">
    <ContentPage.BindingContext>
        <vm:MainViewModel />
    </ContentPage.BindingContext>

    <RefreshView IsRefreshing="{Binding IsRefreshing}"
                 Command="{Binding RefreshCommand}">
        <CollectionView ItemsSource="{Binding Items}"
                        SelectionMode="Single"
                        SelectionChangedCommand="{Binding SelectItemCommand}"
                        SelectionChangedCommandParameter="{Binding SelectedItem, Source={RelativeSource Self}}">
            <CollectionView.ItemTemplate>
                <DataTemplate>
                    <Frame Padding="12" Margin="4,2" HasShadow="True">
                        <StackLayout Spacing="4">
                            <Label Text="{Binding Title}" FontSize="18" FontAttributes="Bold" />
                            <Label Text="{Binding Description}" TextColor="Gray" />
                        </StackLayout>
                    </Frame>
                </DataTemplate>
            </CollectionView.ItemTemplate>
            <CollectionView.EmptyView>
                <Label Text="No items found" HorizontalOptions="Center" VerticalOptions="Center" />
            </CollectionView.EmptyView>
        </CollectionView>
    </RefreshView>
</ContentPage>
```

## ViewModel

```csharp
// ViewModels/MainViewModel.cs
public class MainViewModel : BaseViewModel
{
    private readonly IApiService _api;

    public ObservableCollection<Item> Items { get; } = new();

    private bool _isRefreshing;
    public bool IsRefreshing
    {
        get => _isRefreshing;
        set => SetProperty(ref _isRefreshing, value);
    }

    public ICommand RefreshCommand { get; }
    public ICommand SelectItemCommand { get; }

    public MainViewModel(IApiService api)
    {
        _api = api;
        RefreshCommand = new AsyncCommand(LoadItemsAsync);
        SelectItemCommand = new AsyncCommand<Item>(OnItemSelected);
    }

    private async Task LoadItemsAsync()
    {
        IsRefreshing = true;
        try
        {
            var items = await _api.GetItemsAsync();
            Items.Clear();
            foreach (var item in items) Items.Add(item);
        }
        catch (Exception ex)
        {
            await Application.Current.MainPage.DisplayAlert("Error", ex.Message, "OK");
        }
        finally
        {
            IsRefreshing = false;
        }
    }

    private async Task OnItemSelected(Item item)
    {
        if (item == null) return;
        await Shell.Current.GoToAsync($"detail?id={item.Id}");
    }
}
```

## DependencyService

```csharp
// Shared interface
public interface IDeviceInfo
{
    string GetDeviceId();
    string GetPlatform();
}

// Android implementation
[assembly: Dependency(typeof(DeviceInfoService))]
public class DeviceInfoService : IDeviceInfo
{
    public string GetDeviceId() =>
        Android.Provider.Settings.Secure.GetString(
            Android.App.Application.Context.ContentResolver,
            Android.Provider.Settings.Secure.AndroidId);

    public string GetPlatform() => "Android";
}

// Usage
var deviceInfo = DependencyService.Get<IDeviceInfo>();
var id = deviceInfo.GetDeviceId();
```

## Custom Renderer

```csharp
// Shared control
public class RoundedEntry : Entry { }

// Android renderer
[assembly: ExportRenderer(typeof(RoundedEntry), typeof(RoundedEntryRenderer))]
public class RoundedEntryRenderer : EntryRenderer
{
    protected override void OnElementChanged(ElementChangedEventArgs<Entry> e)
    {
        base.OnElementChanged(e);
        if (Control != null)
        {
            var drawable = new GradientDrawable();
            drawable.SetCornerRadius(24f);
            drawable.SetStroke(2, Android.Graphics.Color.Gray);
            drawable.SetColor(Android.Graphics.Color.White);
            Control.Background = drawable;
            Control.SetPadding(32, 16, 32, 16);
        }
    }
}
```

## Navigation (Shell)

```xml
<Shell xmlns="http://xamarin.com/schemas/2014/forms">
    <TabBar>
        <ShellContent Title="Home" Icon="home.png" ContentTemplate="{DataTemplate views:MainPage}" />
        <ShellContent Title="Settings" Icon="settings.png" ContentTemplate="{DataTemplate views:SettingsPage}" />
    </TabBar>
</Shell>
```

```csharp
// Register route
Routing.RegisterRoute("detail", typeof(DetailPage));

// Navigate
await Shell.Current.GoToAsync("detail?id=123");
```

## Additional Resources

- Xamarin.Forms Docs: https://learn.microsoft.com/xamarin/xamarin-forms/
- Shell Navigation: https://learn.microsoft.com/xamarin/xamarin-forms/app-fundamentals/shell/
