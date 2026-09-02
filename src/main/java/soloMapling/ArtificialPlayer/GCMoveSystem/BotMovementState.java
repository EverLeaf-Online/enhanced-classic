package soloMapling.ArtificialPlayer.GCMoveSystem;

import client.Character;
import server.maps.Foothold;
import server.maps.Rope;

import java.awt.Point;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ThreadLocalRandom;

// Adapted from GreenCatMS - GCMoveSystem movement slice plus the contact-damage fields. Credit: NutNNut.
/*
 * Per-bot movement state for the GCMoveSystem dynamic (calculation-based) movement engine.
 *
 * This is the movement slice of GreenCat's BotEntry: only the physics/nav/broadcast
 * fields the GCMove core reads or writes, with unrelated social/economy state removed.
 */
class BotMovementState {
    final Character bot;
    volatile Character owner;
    volatile boolean following = false;
    volatile int followTargetId = 0;
    ScheduledFuture<?> task;
    BotMovementProfile movementProfile = BotMovementProfile.base();
    long lastProfileRefreshMs = 0L;

    float velY = 0f;
    double hspeed = 0.0;
    double physX = 0.0;
    double physY = 0.0;
    double groundPhysicsCarryMs = 0.0;
    double fallPeakPhysY = Double.POSITIVE_INFINITY;
    boolean inAir = false;
    int jumpCooldownMs = 0;
    int movementVelX = 0;
    int movementVelY = 0;
    int facingDir = 1;
    boolean crouching = false;
    boolean swimming = false;

    int swimMoveDir = 0;
    int swimVerticalHold = 0;
    boolean swimJumpRequested = false;
    long swimNextJumpAtMs = 0L;

    int moveDir = 0;
    int groundBrakeDir = 0;

    boolean climbing = false;
    Rope climbRope = null;
    Rope blockedRopeGrab = null;
    int climbVerticalDir = 0;
    boolean wasMovingX = false;

    int airVelX = 0;
    double airSteerVelX = 0.0;
    boolean fixedAirArc = false;
    boolean pendingFlashJump = false;
    boolean flashJumpFired = false;
    float flashJumpScale = 1f;
    boolean climbUpIntent = false;
    int ropeGrabCooldownMs = 0;

    boolean downJumpPending = false;
    long downJumpGracePeriodMS = 0;
    boolean ropeEntryPending = false;
    Rope ropeEntryRope = null;
    int ropeEntryY = 0;

    volatile boolean grinding = false;
    volatile boolean resting = false;
    int attackCooldownMs = 0;
    volatile boolean shopVisitPending = false;
    int followTravelTargetMapId = -1;

    long portalUseCooldownUntilMs = 0L;
    int portalEnterReadyTicks = -1;

    long alertedUntilMs = 0L;
    boolean alertResetScheduled = false;

    int mobHitCooldownMs = 0;
    Point lastMobTouchCheckPos = null;
    int lastMobTouchMapId = -1;

    int lastMapId = -1;
    Map<Integer, Foothold> fhIndex = new HashMap<>();

    int followOffsetX = 0;
    int skipDelayMs = ThreadLocalRandom.current().nextInt(0, 501);
    int spawnWarmupMs = 2_000 + ThreadLocalRandom.current().nextInt(0, 5_001);
    int aiTickAccumulatorMs = 0;
    volatile boolean tickStopped = false;

    MovementPlan coarsePlan = null;
    long coarsePlanStartMs = 0L;
    Point coarsePlanTarget = null;
    int coarsePlanMapId = -1;
    boolean coarseActive = false;
    long portalDropAtMs = 0L;
    long duckUntilMs = 0L;

    long reactingUntilMs = 0L;
    long nextPlayerScanMs = 0L;

    Point moveTarget = null;
    boolean moveTargetPrecise = false;
    String moveTargetSource = null;
    int moveBestDist = Integer.MAX_VALUE;
    long moveProgressAtMs = 0L;
    Point farmAnchor = null;
    int farmAnchorMapId = -1;

    String lastEdgeBlockReason = null;
    Point navTargetPos = null;
    BotNavigationGraph navGraph = null;
    BotNavigationGraph.Edge navEdge = null;
    BotNavigationGraph.Edge navJumpLaunchEdge = null;
    int navJumpLaunchX = Integer.MIN_VALUE;
    int navJumpLaunchDelaySteps = Integer.MIN_VALUE;
    int navTargetRegionId = -1;
    boolean navPreciseTarget = false;
    int navBlockedPosTicks = 0;
    int navBlockedPosGiveUpTicks = 0;
    int navBlockedPosX = Integer.MIN_VALUE;
    int navBlockedPosY = Integer.MIN_VALUE;
    boolean graphWarmupFallback = false;
    int observedOwnerStepX = 0;
    int observedOwnerStepY = 0;
    String lastNavDecision = "-";

    int stuckMs = 0;
    int unstuckCooldownMs = 0;
    int stuckCheckX = Integer.MIN_VALUE;
    int stuckCheckY = Integer.MIN_VALUE;
    int airStuckTicks = 0;
    int airStuckX = Integer.MIN_VALUE;
    int airStuckY = Integer.MIN_VALUE;

    boolean movementBroadcastValid = false;
    int lastBroadcastX = 0;
    int lastBroadcastY = 0;
    int lastBroadcastVelX = 0;
    int lastBroadcastVelY = 0;
    int lastBroadcastStance = 0;
    int lastBroadcastFh = 0;
    int lastGroundFhId = 0;

    BotMovementState(Character bot, Character owner) {
        this.bot = bot;
        this.owner = owner;
    }
}
