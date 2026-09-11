using System.ComponentModel;
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
    private bool _clientReady;
    private bool _installMode;
    private bool _serverOnline;
    private bool _launcherReady;

    public MainWindow()
    {
        InitializeComponent();
        GameDirectoryText.Text = _gameDirectory;
        Loaded += MainWindow_Loaded;
        Closed += (_, _) => _api.Dispose();
    }

    private bool IsGameRunning()
        => ClientLaunchPolicy.IsGameRunning();

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        _launcherReady = false;

        // .everleaf-launch is a transient one-time ticket. Older clients or an
        // interrupted launch can leave it behind. It must never participate in
        // launcher self-update or managed-file repair state.
        if (!IsGameRunning())
        {
            try
            {
                LaunchTicket.CleanupStale(_gameDirectory);
            }
            catch (Exception ex)
            {
                ErrorText.Text = FriendlyError(ex);
                PatchStatusText.Text = "Could not clear stale launch state";
                SetBusy(false);
                return;
            }
        }

        try
        {
            PatchStatusText.Text = "Checking for launcher updates…";
            using var updater = new LauncherUpdateService(_gameDirectory);
            if (await updater.TryBeginUpdateAsync(CancellationToken.None))
            {
                PatchStatusText.Text = "Restarting the updated launcher…";
                Application.Current.Shutdown();
                return;
            }

            _launcherReady = true;
        }
        catch (Exception ex)
        {
            ErrorText.Text = $"Launcher update check failed: {FriendlyError(ex)} Repair is still available, but Play is disabled until the launcher update check succeeds.";
            PatchStatusText.Text = "Launcher update check required";
        }

        var gameExists = File.Exists(Path.Combine(_gameDirectory, LauncherConfiguration.GameExecutable))
                         || File.Exists(Path.Combine(_gameDirectory, LauncherConfiguration.RuntimeExecutable));
        if (!gameExists)
        {
            _installMode = true;
            PatchStatusText.Text = _launcherReady
                ? "Ready to install the complete EverLeaf client in this folder."
                : "Launcher update check required before Play. Repair remains available.";
        }

        try
        {
            var status = await _api.GetStatusAsync(CancellationToken.None);
            _serverOnline = status.Online;
            ServerStatusText.Text = status.Online ? "EverLeaf is online" : "EverLeaf is offline";
            AnnouncementText.Text = status.Message;
            VersionText.Text = status.Version;
            ServerDot.Fill = new SolidColorBrush(status.Online
                ? Color.FromRgb(114, 226, 155)
                : Color.FromRgb(255, 112, 112));
        }
        catch
        {
            _serverOnline = false;
            ServerStatusText.Text = "Status unavailable";
            AnnouncementText.Text = "The launcher service could not be reached.";
            ServerDot.Fill = new SolidColorBrush(Color.FromRgb(217, 164, 65));
        }

        SetBusy(false);

        if (!gameExists) return;

        if (IsGameRunning())
        {
            ErrorText.Text = ClientLaunchPolicy.MultiClientMessage;
            PatchStatusText.Text = "EverLeaf is already running";
            _clientReady = true;
            SetBusy(false);
            return;
        }

        try
        {
            SetBusy(true);
            await RepairInternalAsync();
        }
        catch (Exception ex)
        {
            ErrorText.Text = FriendlyError(ex);
            PatchStatusText.Text = _launcherReady
                ? "Automatic repair failed"
                : "Launcher update check required before Play";
        }
        finally
        {
            SetBusy(false);
        }
    }

    private async void PlayButton_Click(object sender, RoutedEventArgs e)
    {
        if (_busy) return;
        ErrorText.Text = string.Empty;

        if (!_launcherReady)
        {
            ErrorText.Text = "Launcher update check must succeed before Play is enabled. Restart EverLeaf Launcher and try again.";
            PatchStatusText.Text = "Launcher update check required";
            SetBusy(false);
            return;
        }

        string? launchTicket = null;
        try
        {
            ClientLaunchPolicy.EnsureCanLaunch();
            SetBusy(true);
            if (!_clientReady)
                await RepairInternalAsync();

            // Allow a clean install/repair while the game is offline, but never
            // launch a client into a maintenance/offline server state.
            if (!_serverOnline)
            {
                PatchStatusText.Text = "EverLeaf files are ready. The server is currently offline.";
                return;
            }

            // Check again immediately before issuing the single-use ticket. This
            // closes the window where another launcher instance could start a
            // client while this launcher was repairing/checking files.
            ClientLaunchPolicy.EnsureCanLaunch();

            PatchStatusText.Text = "Launching EverLeaf…";
            launchTicket = LaunchTicket.Create(_gameDirectory);
            GameLauncher.Start(_gameDirectory);
            launchTicket = null; // EverLeaf.exe consumes and deletes the one-time ticket.
            Close();
        }
        catch (Exception ex)
        {
            LaunchTicket.Delete(launchTicket);
            ErrorText.Text = FriendlyError(ex);
            PatchStatusText.Text = IsGameRunning() ? "EverLeaf is already running" : "Ready";
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
            _clientReady = false;
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
        if (IsGameRunning())
            throw new IOException(ClientLaunchPolicy.MultiClientMessage);

        // Do this before PatchService creates probes/temp files. A stale launch
        // ticket is session state and must not affect folder writability or repair.
        LaunchTicket.CleanupStale(_gameDirectory);

        var progress = new Progress<(double Percent, string Status)>(value =>
        {
            PatchProgress.Value = Math.Clamp(value.Percent, 0, 100);
            PatchStatusText.Text = value.Status;
        });

        using var patcher = new PatchService(_gameDirectory);
        await patcher.VerifyAndRepairAsync(progress, CancellationToken.None);
        PatchProgress.Value = 100;
        PatchStatusText.Text = _launcherReady
            ? "All 40 required EverLeaf game files verified."
            : "All 40 required EverLeaf game files verified. Launcher update check is still required before Play.";
        _clientReady = true;
        _installMode = false;
    }

    private static string FriendlyError(Exception ex)
    {
        if (ex is Win32Exception { NativeErrorCode: 1223 })
            return "Windows permission was canceled. Press Play again and approve the Windows permission prompt to start EverLeaf.";
        if (ex is Win32Exception)
            return "Windows could not start EverLeaf.exe. Close any running game process, then press Play again.";
        if (ex is UnauthorizedAccessException)
            return "EverLeaf could not update this folder. Close the game and make sure you have permission to write to the game directory.";
        if (ex is InsufficientDiskSpaceException)
            return ex.Message;
        if (ex is IOException && ex.Message.Contains("EverLeaf", StringComparison.OrdinalIgnoreCase))
            return ex.Message;
        if (ex is IOException)
            return "A game file is in use or could not be replaced. Close EverLeaf and try Repair again.";
        if (ex is HttpRequestException)
            return "The EverLeaf update server could not be reached. Check your connection and try again.";
        return ex.Message;
    }

    private void SetBusy(bool busy)
    {
        _busy = busy;
        PlayButton.IsEnabled = !busy && _launcherReady && (_installMode || _serverOnline) && !IsGameRunning();
        RepairButton.IsEnabled = !busy;
        PlayButton.Content = busy
            ? (_installMode ? "INSTALLING…" : "UPDATING…")
            : !_launcherReady
                ? "LAUNCHER CHECK REQUIRED"
                : IsGameRunning()
                    ? "EVERLEAF ALREADY RUNNING"
                    : _installMode
                        ? "INSTALL EVERLEAF"
                        : _serverOnline
                            ? "PLAY EVERLEAF"
                            : "SERVER OFFLINE";
    }
}