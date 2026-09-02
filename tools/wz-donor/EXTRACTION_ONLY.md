# GMS v95 extraction-only scope

The v95 donor workflow is currently scoped to extraction only.

It attempts every staged v95.4 WZ independently and stores successful XML output privately on Oracle as `gms-v95-extracted.zip`.

No v83 comparison, import manifest, risk scoring, approval, or automatic content import is performed by this workflow.

`Character.wz` is attempted independently with the existing bounded patch/ZLZ fallback so its known parse anomaly cannot block extraction of the other WZ families.
