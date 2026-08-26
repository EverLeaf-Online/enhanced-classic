package everleaf.progression;

/** Application boundary for deterministic Rooted forge purchases. */
public final class RootedForgeService {
    private final RootedForgeRepository repository;

    public RootedForgeService(RootedForgeRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public RootedForgeRepository.PurchaseResult purchase(
            int accountId,
            int characterId,
            int characterLevel,
            RootedForgeRecipe recipe,
            String requestKey
    ) {
        if (!RootedZakumPolicy.levelEligible(characterLevel)) {
            return RootedForgeRepository.PurchaseResult.rejected("rooted_milestone_required");
        }
        if (recipe == null) return RootedForgeRepository.PurchaseResult.rejected("unknown_recipe");
        if (requestKey == null || requestKey.isBlank()) {
            return RootedForgeRepository.PurchaseResult.rejected("invalid_request_key");
        }
        RootedForgeOutcomeCatalog.byRecipe(recipe); // Refuse recipes without a safe deterministic outcome.
        return repository.purchase(accountId, characterId, recipe, requestKey);
    }
}
