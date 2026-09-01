# Duey transform idempotency gate

Production applies EverLeaf release transforms before staging and again while building the staged release. `test_duey_transform_idempotency.py` protects that workflow contract by running the Duey ownership and settlement transforms against already-transformed source and requiring the second pass to be byte-identical.

This specifically guards against regressions where one transform strengthens code produced by another transform and the earlier transform later fails because it only recognizes its original exact output shape.
