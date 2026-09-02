package client.inventory;

import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import tools.Pair;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.util.List;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class WzDonorConsumePersistenceTest {
    private static final int CARBONATED_DRINK = 2022711;
    private static final int ACORN = 2022712;

    @Test
    void characterInventoryPersistsBothDonorConsumesAsOrdinaryUseItems() throws Exception {
        verifyCommonPersistenceBindings(ItemFactory.INVENTORY, 31001, false);
    }

    @Test
    void accountStoragePersistsBothDonorConsumesAsOrdinaryUseItems() throws Exception {
        verifyCommonPersistenceBindings(ItemFactory.STORAGE, 41001, true);
    }

    private static void verifyCommonPersistenceBindings(ItemFactory factory, int ownerId, boolean accountScoped) throws Exception {
        Connection connection = mock(Connection.class);
        PreparedStatement deleteStatement = mock(PreparedStatement.class);
        PreparedStatement insertStatement = mock(PreparedStatement.class);

        when(connection.prepareStatement(anyString())).thenReturn(deleteStatement);
        when(connection.prepareStatement(anyString(), eq(Statement.RETURN_GENERATED_KEYS))).thenReturn(insertStatement);

        Item drink = new Item(CARBONATED_DRINK, (short) 3, (short) 7);
        drink.setOwner("");
        drink.setExpiration(-1);
        drink.setGiftFrom("");
        drink.setFlag((short) 0);

        Item acorn = new Item(ACORN, (short) 8, (short) 19);
        acorn.setOwner("EverLeaf");
        acorn.setExpiration(1_900_000_000_000L);
        acorn.setGiftFrom("staging");
        acorn.setFlag((short) 0);

        factory.saveItems(List.of(
                new Pair<>(drink, InventoryType.USE),
                new Pair<>(acorn, InventoryType.USE)), ownerId, connection);

        verify(deleteStatement).setInt(1, factory.getValue());
        verify(deleteStatement).setInt(2, ownerId);
        verify(deleteStatement).executeUpdate();

        InOrder order = inOrder(insertStatement);
        verifyItemBinding(order, insertStatement, factory.getValue(), ownerId, accountScoped,
                CARBONATED_DRINK, 3, 7, "", -1, "");
        verifyItemBinding(order, insertStatement, factory.getValue(), ownerId, accountScoped,
                ACORN, 8, 19, "EverLeaf", 1_900_000_000_000L, "staging");
    }

    private static void verifyItemBinding(
            InOrder order,
            PreparedStatement statement,
            int persistenceType,
            int ownerId,
            boolean accountScoped,
            int itemId,
            int position,
            int quantity,
            String owner,
            long expiration,
            String giftFrom) throws Exception {
        order.verify(statement).setInt(1, persistenceType);
        order.verify(statement).setString(2, accountScoped ? null : String.valueOf(ownerId));
        order.verify(statement).setString(3, accountScoped ? String.valueOf(ownerId) : null);
        order.verify(statement).setInt(4, itemId);
        order.verify(statement).setInt(5, InventoryType.USE.getType());
        order.verify(statement).setInt(6, position);
        order.verify(statement).setInt(7, quantity);
        order.verify(statement).setString(8, owner);
        order.verify(statement).setInt(9, -1);
        order.verify(statement).setInt(10, 0);
        order.verify(statement).setLong(11, expiration);
        order.verify(statement).setString(12, giftFrom);
        order.verify(statement).executeUpdate();
    }
}
