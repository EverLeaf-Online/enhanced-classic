package net.server.world;

public final class TransportationTimePolicy {
    public static final int INSTANT_RIDE_TIME_MS = 1_000;

    private TransportationTimePolicy() {
    }

    public static int scaledTime(int travelTime, int travelRate) {
        return (int) Math.ceil((double) travelTime / Math.max(1, travelRate));
    }

    public static int rideTime(int travelTime, int travelRate, boolean instantTravel) {
        return instantTravel ? INSTANT_RIDE_TIME_MS : scaledTime(travelTime, travelRate);
    }
}
