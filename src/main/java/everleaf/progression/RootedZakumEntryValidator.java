package everleaf.progression;

import java.util.List;

/** Pure entry validation used before an engine instance is allocated. */
public final class RootedZakumEntryValidator {
    private RootedZakumEntryValidator() {}

    public record Member(int characterId, int accountId, int level, boolean online) {}
    public record Result(boolean allowed, String reason) {
        public static Result allow() { return new Result(true, "ok"); }
        public static Result deny(String reason) { return new Result(false, reason); }
    }

    public static Result validate(List<Member> members) {
        if (members == null || !RootedZakumPolicy.partySizeEligible(members.size())) {
            return Result.deny("Rooted Zakum requires 3-6 party members.");
        }
        if (members.stream().anyMatch(member -> !member.online())) {
            return Result.deny("Every party member must be online before the instance starts.");
        }
        if (members.stream().anyMatch(member -> !RootedZakumPolicy.levelEligible(member.level()))) {
            return Result.deny("Every party member must be level 200 or higher.");
        }
        long uniqueCharacters = members.stream().map(Member::characterId).distinct().count();
        if (uniqueCharacters != members.size()) {
            return Result.deny("Duplicate characters cannot enter the same encounter.");
        }
        return Result.allow();
    }
}
