using System.IO;
using System.Windows;
using System.Windows.Media;

namespace EverLeaf.Launcher;

public partial class MainWindow : Window
{
    private readonly LauncherApi _api = new();
    private readonly string _gameDirectory = AppContext.BaseDirectory;
    private LauncherSession? _session;
    private bool _busy;

    public MainWindow()
    {
        InitializeComponent();
        Loaded += MainWindow_Loaded;
        Closed += (_, _) => _api.Dispose();

        var remembered = UserPreferences.LoadRememberedUsername();
        if (!string.IsNullOrWhiteSpace(remembered))
        {
            UsernameBox.Text = remembered;
            RememberUsernameBox.IsChecked = true;
        }
    }

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        try
        {
            var status = await _api.GetStatusAsync(CancellationToken.None);
            ServerStatusText.Text = status.Online ? "EverLeaf is online" : "EverLeaf is offline";
            AnnouncementText.Text = status.Message;
            VersionText.Text = status.Version;
            ServerDot.Fill = new SolidColorBrush(status.Online
                ? Color.FromRgb(114, 226, 155)
                : Color.FromRgb(255, 112, 112));
        }
        catch
        {
            ServerStatusText.Text = "Status unavailable";
            AnnouncementText.Text = "The launcher service could not be reached.";
            ServerDot.Fill = new SolidColorBrush(Color.FromRgb(217, 164, 65));
        }
    }

    private async void PlayButton_Click(object sender, RoutedEventArgs e)
    {
        if (_busy) return;
        ErrorText.Text = string.Empty;

        try
        {
            SetBusy(true);
            if (_session is null || _session.ExpiresAt <= DateTimeOffset.UtcNow)
            {
                if (string.IsNullOrWhiteSpace(UsernameBox.Text) || PasswordInput.Password.Length == 0)
                    throw new InvalidOperationException("Enter your username and password.");

                PatchStatusText.Text = "Signing in securely…";
                _session = await _api.LoginAsync(
                    UsernameBox.Text.Trim(), PasswordInput.Password, CancellationToken.None);
                PasswordInput.Clear();
                SaveRememberedUsername();
            }

            await RepairInternalAsync();
            PatchStatusText.Text = "Launching EverLeaf…";
            GameLauncher.Start(_gameDirectory, _session);
            Close();
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            PatchStatusText.Text = "Ready";
        }
        finally
        {
            SetBusy(false);
        }
    }

    private async void RepairButton_Click(object sender, RoutedEventArgs e)
    {
        if (_busy) return;
        ErrorText.Text = string.Empty;
        try
        {
            SetBusy(true);
            await RepairInternalAsync();
        }
        catch (Exception ex)
        {
            ErrorText.Text = ex.Message;
            PatchStatusText.Text = "Repair failed";
        }
        finally
        {
            SetBusy(false);
        }
    }

    private async Task RepairInternalAsync()
    {
        var progress = new Progress<(double Percent, string Status)>(value =>
        {
            PatchProgress.Value = value.Percent;
            PatchStatusText.Text = value.Status;
        });
        await new PatchService(_gameDirectory).VerifyAndRepairAsync(progress, CancellationToken.None);
    }

    private void SaveRememberedUsername()
    {
        UserPreferences.SaveRememberedUsername(
            RememberUsernameBox.IsChecked == true ? UsernameBox.Text.Trim() : string.Empty);
    }

    private void SetBusy(bool busy)
    {
        _busy = busy;
        PlayButton.IsEnabled = !busy;
        RepairButton.IsEnabled = !busy;
        UsernameBox.IsEnabled = !busy;
        PasswordInput.IsEnabled = !busy;
        PlayButton.Content = busy ? "WORKING…" : "SIGN IN & PLAY";
    }
}
