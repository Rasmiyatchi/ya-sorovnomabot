from __future__ import annotations

import enum


class Role(str, enum.Enum):
    ROOT = "root"
    ADMIN = "admin"


# Callback data prefixes (kept short and explicit to avoid collisions)
class CB:
    VOTE = "vote"            # vote:<candidate_id>
    CONFIRM = "confirm"      # confirm:<candidate_id>
    CANCEL = "cancel"        # cancel
    RECHECK_SUB = "recheck"  # recheck (subscription)
    TOP = "top"             # show public top

    # Admin
    ADM = "adm"             # adm:<action>
    ADM_CAND_DEL = "acdel"   # acdel:<candidate_id>

    # Root
    ROOT = "root"           # root:<action>
    ROOT_ADMIN_DEL = "radel"  # radel:<telegram_id>


PAGE_SIZE = 10
