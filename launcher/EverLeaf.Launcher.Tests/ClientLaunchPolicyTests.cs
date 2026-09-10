using System.IO;
using Xunit;

namespace EverLeaf.Launcher.Tests;

public sealed class ClientLaunchPolicyTests
{
    [Fact]
    public void AllowsLaunchWhenNoClientIsRunning()
    {
        ClientLaunchPolicy.EnsureCanLaunch(false);
    }

    [Fact]
    public void RejectsLaunchWhenAClientIsAlreadyRunning()
    {
        var exception = Assert.Throws<IOException>(() => ClientLaunchPolicy.EnsureCanLaunch(true));
        Assert.Contains("Multi-client is not allowed", exception.Message);
    }

    [Fact]
    public void UsesMachineWideEverLeafClientMutexName()
    {
        Assert.Equal(@"Global\EverLeafMS.Client.SingleInstance", ClientLaunchPolicy.ClientMutexName);
    }
}
