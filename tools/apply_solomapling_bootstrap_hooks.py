#!/usr/bin/env python3
"""Wire the safe SoloMapling headless-client bootstrap into EverLeaf.

Normal starts initialize only the shared socketless BotClient. The optional
DisposableQaSmokeRunner is also invoked at this point, but it is inert unless
its exact disposable-QA environment gates are present; EnvironmentManager and
automatic bot population remain disabled.
"""
from pathlib import Path

TARGET = Path("src/main/java/net/server/Server.java")
CLIENT_IMPORT = "import soloMapling.ArtificialPlayer.BotClientHandler;\n"
SMOKE_IMPORT = "import soloMapling.ArtificialPlayer.DisposableQaSmokeRunner;\n"
CLIENT_MARKER = "BotClientHandler.initHeadlessBotClient();"
SMOKE_MARKER = "DisposableQaSmokeRunner.startIfRequested();"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    anchor = "import service.NoteService;\n"
    if anchor not in text and (CLIENT_IMPORT not in text or SMOKE_IMPORT not in text):
        raise SystemExit("Could not locate Server import anchor")
    if CLIENT_IMPORT not in text:
        text = text.replace(anchor, anchor + CLIENT_IMPORT, 1)
    if SMOKE_IMPORT not in text:
        import_anchor = CLIENT_IMPORT if CLIENT_IMPORT in text else anchor
        text = text.replace(import_anchor, import_anchor + SMOKE_IMPORT, 1)

    if CLIENT_MARKER not in text:
        startup_anchor = """        for (Channel ch : this.getAllChannels()) {
            ch.reloadEventScriptManager();
        }
"""
        if startup_anchor not in text:
            raise SystemExit("Could not locate Server post-channel startup anchor")
        addition = startup_anchor + """
        // SoloMapling QA foundation: initialize the shared headless client only.
        // Automatic environment/bot spawning remains disabled until smoke-tested.
        BotClientHandler.initHeadlessBotClient();
"""
        text = text.replace(startup_anchor, addition, 1)

    if SMOKE_MARKER not in text:
        text = text.replace(
            "        BotClientHandler.initHeadlessBotClient();\n",
            "        BotClientHandler.initHeadlessBotClient();\n"
            "        DisposableQaSmokeRunner.startIfRequested();\n",
            1,
        )

    TARGET.write_text(text, encoding="utf-8")
    print("SoloMapling bootstrap hook applied (headless client + explicitly gated disposable QA smoke only).")


if __name__ == "__main__":
    main()
