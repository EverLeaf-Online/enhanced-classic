package soloMapling.server;

import java.util.concurrent.TimeUnit;

/** Delayed task helper backed by SoloMapling's shared executors. */
public final class MethodScheduler {
    private MethodScheduler() {}

    public static void runAfterDelay(Runnable method, long delayMilliseconds) {
        ExecutorServiceManager.getScheduledExecutorService().schedule(
                () -> ExecutorServiceManager.runAsync(() -> {
                    try {
                        method.run();
                    } catch (Exception exception) {
                        System.out.println("runAfterDelay caught exception: " + method);
                        exception.printStackTrace();
                    }
                }), delayMilliseconds, TimeUnit.MILLISECONDS);
    }

    public static void shutdown() {
        // Shared pools are owned by ExecutorServiceManager.
    }

    public static long getPendingTaskCount() {
        return 0;
    }
}
