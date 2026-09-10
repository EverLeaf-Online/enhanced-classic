using System.Diagnostics;
using System.IO;
using System.Threading;

namespace EverLeaf.Launcher;

internal static class ClientLaunchPolicy
{
    internal const string ClientMutexName = @"Global\EverLeafMS.Client.SingleInstance";
    internal const string MultiClientMessage = "EverLeaf is already running. Multi-client is not allowed; close the existing game before launching another client.";

    internal static bool IsGameRunning()
    {
        if (Process.GetProcessesByName("EverLeaf").Any(process => process.Id != Environment.ProcessId))
            return true;

        try
        {
            if (Mutex.TryOpenExisting(ClientMutexName, out var mutex))
            {
                mutex.Dispose();
                return true;
            }
        }
        catch (UnauthorizedAccessException)
        {
            // A machine-wide EverLeaf client mutex exists but is owned by a
            // context this launcher cannot inspect. Fail closed rather than
            // allowing a second client.
            return true;
        }

        return false;
    }

    internal static void EnsureCanLaunch()
        => EnsureCanLaunch(IsGameRunning());

    internal static void EnsureCanLaunch(bool gameRunning)
    {
        if (gameRunning)
            throw new IOException(MultiClientMessage);
    }
}
