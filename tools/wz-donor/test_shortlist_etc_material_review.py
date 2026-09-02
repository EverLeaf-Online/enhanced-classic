#!/usr/bin/env python3

from shortlist_etc_material_review import build_shortlist, is_review_candidate


def base_profile(content_id: str, **overrides):
    profile = {
        "contentId": content_id,
        "family": "Etc",
        "manifestRisk": "low",
        "name": "Ordinary Material",
        "description": "",
        "sourcePath": "Etc.wz/Etc/0400.img.xml",
        "infoProperties": ["icon", "iconraw", "price"],
        "specProperties": [],
        "duplicateOf": None,
        "approved": False,
    }
    profile.update(overrides)
    return profile


def main() -> None:
    accepted = base_profile("4001000")
    accepted_slotmax = base_profile("4001001", infoProperties=["icon", "iconraw", "price", "slotmax"])
    rejected_quest = base_profile("4001002", infoProperties=["icon", "iconraw", "price", "quest"])
    rejected_trade = base_profile("4001003", infoProperties=["icon", "iconraw", "price", "tradeblock"])
    rejected_spec = base_profile("4001004", specProperties=["foo"])
    rejected_duplicate = base_profile("4001005", duplicateOf="4000000")
    rejected_other_prefix = base_profile("4031000")
    rejected_high = base_profile("4001006", manifestRisk="high")
    rejected_approved = base_profile("4001007", approved=True)
    rejected_missing_iconraw = base_profile("4001008", infoProperties=["icon", "price"])
    rejected_no_name = base_profile("4001009", name=None)
    rejected_consume = base_profile("4001010", family="Consume")

    assert is_review_candidate(accepted)
    assert is_review_candidate(accepted_slotmax)
    for profile in [
        rejected_quest,
        rejected_trade,
        rejected_spec,
        rejected_duplicate,
        rejected_other_prefix,
        rejected_high,
        rejected_approved,
        rejected_missing_iconraw,
        rejected_no_name,
        rejected_consume,
    ]:
        assert not is_review_candidate(profile), profile

    report = {
        "donorId": "fixture",
        "profiles": [
            rejected_quest,
            accepted_slotmax,
            accepted,
            rejected_duplicate,
        ],
    }
    result = build_shortlist(report)
    assert result["kind"] == "review-only-etc-material-shortlist"
    assert result["candidateCount"] == 2
    assert [c["contentId"] for c in result["candidates"]] == ["4001000", "4001001"]
    assert all(c["approved"] is False for c in result["candidates"])
    assert all(c["importAllowed"] is False for c in result["candidates"])
    assert result["approved"] is False
    assert result["automaticImport"] is False

    print("shortlist_etc_material_review tests passed")


if __name__ == "__main__":
    main()
