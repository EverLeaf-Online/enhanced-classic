#!/usr/bin/env python3
"""Wire the safe SoloMapling headless-client bootstrap into EverLeaf.

Normal starts initialize only the shared socketless BotClient. The optional
DisposableQaSmokeRunner and DisposableQaSuiteRunner are invoked at this point,
but both are inert unless their exact disposable-QA environment gates are
present; EnvironmentManager and automatic bot population remain disabled.
"""
from pathlib import Path

TARGET = Path("src/main/java/net/server/Server.java")
CLIENT_IMPORT = "import soloMapling.ArtificialPlayer.BotClientHandler;\n"
SMOKE_IMPORT = "import soloMapling.ArtificialPlayer.DisposableQaSmokeRunner;\n"
SUITE_IMPORT = "import soloMapling.ArtificialPlayer.DisposableQaSuiteRunner;\n"
CLIENT_MARKER = "BotClientHandler.initHeadlessBotClient();"
SMOKE_MARKER = "DisposableQaSmokeRunner.startIfRequested();"
SUITE_MARKER = "DisposableQaSuiteRunner.startIfRequested();"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    anchor = "import service.NoteService;\n"
    if anchor not in text and any(x not in text for x in (CLIENT_IMPORT, SMOKE_IMPORT, SUITE_IMPORT)):
        raise SystemExit("Could not locate Server import anchor")
    if CLIENT_IMPORT not in text:
        text = text.replace(anchor, anchor + CLIENT_IMPORT, 1)
    if SMOKE_IMPORT not in text:
        import_anchor = CLIENT_IMPORT if CLIENT_IMPORT in text else anchor
        text = text.replace(import_anchor, import_anchor + SMOKE_IMPORT, 1)
    if SUITE_IMPORT not in text:
        import_anchor = SMOKE_IMPORT if SMOKE_IMPORT in text else CLIENT_IMPORT
        text = text.replace(import_anchor, import_anchor + SUITE_IMPORT, 1)

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

    if SUITE_MARKER not in text:
        insertion = "        DisposableQaSmokeRunner.startIfRequested();\n"
        if insertion not in text:
            raise SystemExit("Could not locate disposable QA smoke bootstrap marker")
        text = text.replace(
            insertion,
            insertion + "        DisposableQaSuiteRunner.startIfRequested();\n",
            1,
        )

    TARGET.write_text(text, encoding="utf-8")
    print("SoloMapling bootstrap hook applied (headless client + gated disposable smoke/suite only).")


if __name__ == "__main__":
    main()
