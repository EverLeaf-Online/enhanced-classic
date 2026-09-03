package soloMapling.server;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/** Shared executors used by the staged SoloMapling runtime. */
public final class ExecutorServiceManager {
    private static final ExecutorService executorService = Executors.newFixedThreadPool(8);
    private static final ScheduledExecutorService scheduledExecutorService = Executors.newScheduledThreadPool(10);
    private static final ExecutorService virtualThreadExecutor = Executors.newVirtualThreadPerTaskExecutor();

    private ExecutorServiceManager() {}

    public static ExecutorService getExecutorService() { return executorService; }
    public static ScheduledExecutorService getScheduledExecutorService() { return scheduledExecutorService; }
    public static ExecutorService getVirtualThreadExecutorService() { return virtualThreadExecutor; }
    public static void runAsync(Runnable task) { virtualThreadExecutor.submit(task); }
    public static void scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit) {
        scheduledExecutorService.scheduleAtFixedRate(command, initialDelay, period, unit);
    }

    public static void shutdown() {
        shutdownExecutor(executorService);
        shutdownExecutor(scheduledExecutorService);
        shutdownExecutor(virtualThreadExecutor);
    }

    private static void shutdownExecutor(ExecutorService executor) {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
                if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                    System.err.println("Executor did not terminate");
                }
            }
        } catch (InterruptedException interrupted) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
