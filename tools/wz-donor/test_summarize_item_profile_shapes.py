#!/usr/bin/env python3

from summarize_item_profile_shapes import summarize


def main() -> None:
    report = {
        "donorId": "fixture",
        "profiles": [
            {
                "contentId": "4000001",
                "family": "Etc",
                "manifestRisk": "low",
                "classification": "manual-review",
                "name": "Material A",
                "infoProperties": ["icon", "price"],
                "specProperties": [],
                "reasons": ["family-etc-not-first-batch"],
            },
            {
                "contentId": "4000002",
                "family": "Etc",
                "manifestRisk": "low",
                "classification": "manual-review",
                "name": "Material B",
                "infoProperties": ["price", "icon"],
                "specProperties": [],
                "reasons": ["family-etc-not-first-batch"],
            },
            {
                "contentId": "4000003",
                "family": "Etc",
                "manifestRisk": "blocked",
                "classification": "blocked",
                "name": None,
                "infoProperties": ["quest"],
                "specProperties": [],
                "reasons": ["known-missing-dependency"],
            },
            {
                "contentId": "2020000",
                "family": "Consume",
                "manifestRisk": "low",
                "classification": "simple-consume",
                "name": "Potion",
                "infoProperties": [],
                "specProperties": ["hp"],
                "reasons": [],
            },
        ],
    }

    result = summarize(report, "Etc", sample_limit=1)
    assert result["family"] == "Etc"
    assert result["profileCount"] == 3
    assert result["shapeCount"] == 2
    assert result["automaticImport"] is False
    assert result["shapes"][0]["count"] == 2
    assert result["shapes"][0]["manifestRisk"] == "low"
    assert result["shapes"][0]["infoProperties"] == ["icon", "price"]
    assert len(result["shapes"][0]["samples"]) == 1
    assert result["shapes"][1]["count"] == 1
    assert result["shapes"][1]["manifestRisk"] == "blocked"
    assert result["shapes"][1]["hasStringName"] is False

    print("summarize_item_profile_shapes tests passed")


if __name__ == "__main__":
    main()
