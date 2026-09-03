package soloMapling.ArtificialPlayer;

import client.Character;
import client.QuestStatus;
import server.quest.Quest;

import java.util.List;

/** Server-authoritative quest acceptance/completion helpers for controlled SoloMapling QA. */
public final class BotQuestDriver {
    private BotQuestDriver() {}

    public static QuestResult status(Character bot, int questId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        QuestStatus status = bot.getQuest(quest);
        int startNpc = quest.getNpcRequirement(false);
        int endNpc = quest.getNpcRequirement(true);
        return new QuestResult(true, questId, status.getStatus().getId(), startNpc, endNpc,
                quest.getRelevantMobs(), quest.canComplete(bot, endNpc), "status");
    }

    public static QuestResult start(Character bot, int questId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        int npcId = quest.getNpcRequirement(false);
        if (npcId < 0) return QuestResult.fail(questId, "no-start-npc");
        return start(bot, questId, npcId);
    }

    public static QuestResult start(Character bot, int questId, int npcId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        if (quest.getNpcRequirement(false) >= 0 && BotNpcDriver.findNpc(bot, npcId) == null) {
            return QuestResult.fail(questId, "start-npc-not-on-map");
        }
        if (!quest.canStart(bot, npcId) && !quest.isAutoStart()) {
            return QuestResult.fail(questId, "start-requirements-not-met");
        }
        quest.start(bot, npcId);
        QuestStatus status = bot.getQuest(quest);
        boolean started = status.getStatus() == QuestStatus.Status.STARTED;
        return new QuestResult(started, questId, status.getStatus().getId(), quest.getNpcRequirement(false),
                quest.getNpcRequirement(true), quest.getRelevantMobs(), false,
                started ? "started" : "start-rejected");
    }

    public static QuestResult complete(Character bot, int questId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        int npcId = quest.getNpcRequirement(true);
        if (npcId < 0) return QuestResult.fail(questId, "no-complete-npc");
        return complete(bot, questId, npcId);
    }

    public static QuestResult complete(Character bot, int questId, int npcId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        if (quest.getNpcRequirement(true) >= 0 && BotNpcDriver.findNpc(bot, npcId) == null) {
            return QuestResult.fail(questId, "complete-npc-not-on-map");
        }
        if (!quest.canComplete(bot, npcId) && !quest.isAutoComplete()) {
            return QuestResult.fail(questId, "complete-requirements-not-met");
        }
        quest.complete(bot, npcId);
        QuestStatus status = bot.getQuest(quest);
        boolean completed = status.getStatus() == QuestStatus.Status.COMPLETED;
        return new QuestResult(completed, questId, status.getStatus().getId(), quest.getNpcRequirement(false),
                quest.getNpcRequirement(true), quest.getRelevantMobs(), completed,
                completed ? "completed" : "completion-rejected");
    }

    public static QuestResult forfeit(Character bot, int questId) {
        if (!eligible(bot)) return QuestResult.fail(questId, "not-eligible");
        Quest quest = Quest.getInstance(questId);
        boolean forfeited = quest.forfeit(bot);
        QuestStatus status = bot.getQuest(quest);
        return new QuestResult(forfeited, questId, status.getStatus().getId(), quest.getNpcRequirement(false),
                quest.getNpcRequirement(true), quest.getRelevantMobs(), false,
                forfeited ? "forfeited" : "forfeit-rejected");
    }

    private static boolean eligible(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.isLoggedinWorld()
                && bot.getMap() != null && bot.isAlive();
    }

    public record QuestResult(boolean success, int questId, int status, int startNpcId, int completeNpcId,
                              List<Integer> relevantMobs, boolean completable, String reason) {
        static QuestResult fail(int questId, String reason) {
            return new QuestResult(false, questId, -1, -1, -1, List.of(), false, reason);
        }
    }
}
