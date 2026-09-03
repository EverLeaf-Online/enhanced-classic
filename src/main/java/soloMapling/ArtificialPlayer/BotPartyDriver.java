package soloMapling.ArtificialPlayer;

import client.Character;
import net.server.world.Party;
import net.server.world.PartyCharacter;
import net.server.world.PartyOperation;

/** Server-authoritative party operations for controlled SoloMapling QA bots. */
public final class BotPartyDriver {
    private BotPartyDriver() {}

    public static PartyResult create(Character bot) {
        if (!eligible(bot)) return PartyResult.fail("not-eligible");
        if (bot.getParty() != null) return PartyResult.fail("already-in-party");
        boolean created = Party.createParty(bot, true);
        Party party = bot.getParty();
        return created && party != null
                ? new PartyResult(true, party.getId(), party.getLeaderId(), party.getMembers().size(), "created")
                : PartyResult.fail("create-rejected");
    }

    public static PartyResult join(Character bot, Character leader) {
        if (!eligible(bot) || !eligible(leader)) return PartyResult.fail("not-eligible");
        if (bot == leader) return PartyResult.fail("same-character");
        if (bot.getWorld() != leader.getWorld()) return PartyResult.fail("different-world");
        Party party = leader.getParty();
        if (party == null) return PartyResult.fail("leader-has-no-party");
        if (bot.getParty() != null) return PartyResult.fail("already-in-party");
        boolean joined = Party.joinParty(bot, party.getId(), true);
        Party current = bot.getParty();
        return joined && current != null
                ? new PartyResult(true, current.getId(), current.getLeaderId(), current.getMembers().size(), "joined")
                : PartyResult.fail("join-rejected");
    }

    public static PartyResult leave(Character bot) {
        if (!eligible(bot)) return PartyResult.fail("not-eligible");
        Party party = bot.getParty();
        if (party == null) return PartyResult.fail("not-in-party");
        int partyId = party.getId();
        Party.leaveParty(party, bot.getClient());
        return new PartyResult(bot.getParty() == null, partyId, -1, 0,
                bot.getParty() == null ? "left" : "leave-rejected");
    }

    public static PartyResult transferLeader(Character leader, Character newLeader) {
        if (!eligible(leader) || !eligible(newLeader)) return PartyResult.fail("not-eligible");
        Party party = leader.getParty();
        if (party == null || newLeader.getParty() != party) return PartyResult.fail("not-same-party");
        if (party.getLeaderId() != leader.getId()) return PartyResult.fail("not-party-leader");
        PartyCharacter target = party.getMemberById(newLeader.getId());
        if (target == null) return PartyResult.fail("target-not-member");
        leader.getWorldServer().updateParty(party.getId(), PartyOperation.CHANGE_LEADER, target);
        return new PartyResult(party.getLeaderId() == newLeader.getId(), party.getId(), party.getLeaderId(),
                party.getMembers().size(), party.getLeaderId() == newLeader.getId() ? "leader-transferred" : "leader-transfer-rejected");
    }

    public static PartyResult status(Character bot) {
        if (!eligible(bot)) return PartyResult.fail("not-eligible");
        Party party = bot.getParty();
        if (party == null) return PartyResult.fail("not-in-party");
        return new PartyResult(true, party.getId(), party.getLeaderId(), party.getMembers().size(), "active");
    }

    private static boolean eligible(Character chr) {
        return chr != null && chr.getClient() != null && chr.isLoggedinWorld() && chr.getMap() != null;
    }

    public record PartyResult(boolean success, int partyId, int leaderId, int members, String reason) {
        static PartyResult fail(String reason) { return new PartyResult(false, -1, -1, 0, reason); }
    }
}
