namespace EverLeaf.Launcher;

public partial class App : System.Windows.Application
{
    protected override void OnStartup(System.Windows.StartupEventArgs e)
    {
        base.OnStartup(e);

        if (LauncherUpdateApplier.TryApply(e.Args))
        {
            Shutdown();
            return;
        }

        LauncherUpdateApplier.ScheduleCleanup(e.Args);
        new MainWindow().Show();
    }
}
