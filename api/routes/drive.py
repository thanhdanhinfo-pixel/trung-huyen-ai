from fastapi import APIRouter

router = APIRouter(prefix="/drive", tags=["drive"])

# APP-DECOMPOSITION-V2 / Phase 1
# Existing drive endpoints will be migrated here incrementally.
# No production routes are moved in this commit.
