/*
    This file is part of the EverLeaf MapleStory server.

    Evan is backported into the v83 client/server from the immediately
    following data set. Fresh Evans begin as the Evan beginner (job 2001)
    in Utah's House so the original dragon-master tutorial/quest chain can
    advance them naturally instead of skipping directly to first growth.
*/
package client.creator.novice;

import client.Client;
import client.Job;
import client.creator.CharacterFactory;
import client.creator.CharacterFactoryRecipe;

public class EvanCreator extends CharacterFactory {
    private static final int EVAN_START_MAP = 100030100; // Utah's House - Small Attic

    private static CharacterFactoryRecipe createRecipe(int top, int bottom, int shoes, int weapon) {
        return new CharacterFactoryRecipe(Job.EVAN, 1, EVAN_START_MAP, top, bottom, shoes, weapon);
    }

    public static int createCharacter(Client c, String name, int face, int hair, int skin,
                                      int top, int bottom, int shoes, int weapon, int gender) {
        return createNewCharacter(c, name, face, hair, skin, gender,
                createRecipe(top, bottom, shoes, weapon));
    }
}
