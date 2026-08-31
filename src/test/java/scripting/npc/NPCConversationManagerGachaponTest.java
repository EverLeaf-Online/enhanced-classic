package scripting.npc;

import client.Client;
import constants.id.ItemId;
import constants.id.NpcId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.doReturn;

class NPCConversationManagerGachaponTest {
    @Test
    void fullRewardInventoryDoesNotConsumeTicket() {
        NPCConversationManager cm = spy(new NPCConversationManager(mock(Client.class), NpcId.GACHAPON_HENESYS, "gachapon"));
        doReturn(true).when(cm).haveItem(ItemId.GACHAPON_TICKET);
        doReturn(false).when(cm).canHold(anyInt(), anyInt(), anyInt(), anyInt());
        doNothing().when(cm).sendOk(anyString());

        boolean awarded = cm.doGachapon(ItemId.GACHAPON_TICKET);

        assertFalse(awarded);
        verify(cm, never()).gainItem(ItemId.GACHAPON_TICKET, (short) -1, false, true);
    }
}
