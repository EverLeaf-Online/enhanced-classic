#!/usr/bin/env python3
"""Wire the safe SoloMapling headless-client bootstrap into EverLeaf.

This slice only initializes the shared socketless BotClient after worlds/channels
exist. It deliberately does not start EnvironmentManager or spawn any bots.
"""
from pathlib import Path

TARGET = Path("src/main/java/net/server/Server.java")
IMPORT = "import soloMapling.ArtificialPlayer.BotClientHandler;\n"
MARKER = "BotClientHandler.initHeadlessBotClient();"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    if IMPORT not in text:
        anchor = "import service.NoteService;\n"
        if anchor not in text:
            raise SystemExit("Could not locate Server import anchor")
        text = text.replace(anchor, anchor + IMPORT, 1)

    if MARKER not in text:
        anchor = """        for (Channel ch : this.getAllChannels()) {
            ch.reloadEventScriptManager();
        }
"""
        if anchor not in text:
            raise SystemExit("Could not locate Server post-channel startup anchor")
        addition = anchor + """
        // SoloMapling QA foundation: initialize the shared headless client only.
        // Automatic environment/bot spawning remains disabled until smoke-tested.
        BotClientHandler.initHeadlessBotClient();
"""
        text = text.replace(anchor, addition, 1)

    TARGET.write_text(text, encoding="utf-8")
    print("SoloMapling bootstrap hook applied (headless client init only; no bot spawn).")


if __name__ == "__main__":
    main()
