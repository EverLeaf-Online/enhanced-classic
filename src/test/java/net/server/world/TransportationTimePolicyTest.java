package net.server.world;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class TransportationTimePolicyTest {
    @Test
    void scalesBoardingTimeWithoutChangingExistingBehavior() {
        assertEquals(150_000, TransportationTimePolicy.scaledTime(300_000, 2));
    }

    @Test
    void instantRideUsesSafeTransitionDelay() {
        assertEquals(1_000, TransportationTimePolicy.rideTime(600_000, 2, true));
    }

    @Test
    void normalRideStillUsesWorldTravelRate() {
        assertEquals(300_000, TransportationTimePolicy.rideTime(600_000, 2, false));
    }
}
