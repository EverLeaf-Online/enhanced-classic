using System.IO;
using System.Net.Http;
using System.Windows;
using System.Windows.Media;

namespace EverLeaf.Launcher;

public partial class MainWindow : Window
{
    private readonly LauncherApi _api = new();
    private readonly string _gameDirectory = AppContext.BaseDirectory;
    private bool _busy;

    public MainWindow()
    {
        InitializeComponent();
        GameDirectoryText.Text = _gameDirectory;
        Loaded += MainWindow_Loaded;
        Closed += (_, _) => _api.Dispose();
    }

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        if (!File.Exists(Path.Combine(_gameDirectory, LauncherConfiguration.GameExecutable)))
        {
            ErrorText.Text = "MapleStory.exe is not in this folder. Extract the EverLeaf client, then place this portable launcher beside MapleStory.exe.";
        }

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
            await RepairInternalAsync();
            PatchStatusText.Text = "Launching EverLeaf…";
            GameLauncher.Start(_gameDirectory);
            Close();
        }
        catch (Exception ex)
        {
            ErrorText.Text = FriendlyError(ex);
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
            ErrorText.Text = FriendlyError(ex);
            PatchStatusText.Text = "Repair failed";
        }
        finally
        {
            SetBusy(false);
        }
    }

    private async Task RepairInternalAsync()
    {
        if (!File.Exists(Path.Combine(_gameDirectory, LauncherConfiguration.GameExecutable)))
            throw new InvalidOperationException("MapleStory.exe was not found beside the launcher. Put EverLeafLauncher.exe in your supported v83 game folder.");

        var progress = new Progress<(double Percent, string Status)>(value =>
        {
            PatchProgress.Value = Math.Clamp(value.Percent, 0, 100);
            PatchStatusText.Text = value.Status;
        });

        using var patcher = new PatchService(_gameDirectory);
        await patcher.VerifyAndRepairAsync(progress, CancellationToken.None);
        PatchProgress.Value = 100;
        PatchStatusText.Text = "All 36 required EverLeaf game files verified.";
    }

    private static string FriendlyError(Exception ex)
    {
        if (ex is UnauthorizedAccessException)
            return "EverLeaf could not update this folder. Close the game and make sure you have permission to write to the game directory.";
        if (ex is IOException)
            return "A game file is in use or could not be replaced. Close MapleStory and try Repair again.";
        if (ex is HttpRequestException)
            return "The EverLeaf update server could not be reached. Check your connection and try again.";
        return ex.Message;
    }

    private void SetBusy(bool busy)
    {
        _busy = busy;
        PlayButton.IsEnabled = !busy;
        RepairButton.IsEnabled = !busy;
        PlayButton.Content = busy ? "UPDATING…" : "PLAY EVERLEAF";
    }
}
