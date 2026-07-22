"""
markov_jump_parser.py
---------------------
Parses Markov jump count columns from a BEAST log file and returns the
posterior expected number of jumps for each directed (start, end) location pair.

Supported BEAST naming conventions
-----------------------------------
BEAST 1 (MarkovJumpsTreeLikelihood):
    c_{trait}.{A}to{B}[1]
    e.g. c_region.NigeriatoWestern Europe[1]

BEAST 2 (discrete-state BSSVS with jump logging):
    {trait}.actual_jumps.{A}.{B}
    e.g. region.actual_jumps.Nigeria.Western Europe

The parser validates each candidate (start, end) split against the known
location list to correctly handle location names that contain "to" or ".".
"""

import re
import pandas as pd


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_markov_jump_counts(log_source, location_trait, location_list, burnin=0.0):
    """
    Read Markov jump count columns from a BEAST log file and compute the
    posterior mean count for each directed (start_location, end_location) pair.

    Parameters
    ----------
    log_source : str or file-like
        Path to the BEAST log file, or an already-opened file-like object.
        The file must be tab-separated with a header row.
    location_trait : str
        Name of the discrete location trait (e.g. "region").
    location_list : list[str]
        Ordered list of location names as used in the BEAST XML / log columns.
    burnin : float or int
        If 0 <= burnin < 1  → fraction of rows to discard (e.g. 0.1 = 10 %).
        If burnin >= 1       → absolute number of rows to discard.
        Pass 0 (default) when the log file has already had burn-in removed.

    Returns
    -------
    dict[(str, str), float]
        Mapping from (start_name, end_name) → posterior mean jump count.
        Only pairs with at least one matching column are included.

    Raises
    ------
    ValueError
        If no Markov jump columns are found for the given trait.
    """
    # ------------------------------------------------------------------
    # 1. Load the log file
    # ------------------------------------------------------------------
    if isinstance(log_source, str):
        log_df = pd.read_csv(log_source, sep='\t', comment='#', low_memory=False)
    else:
        log_df = pd.read_csv(log_source, sep='\t', comment='#', low_memory=False)

    # ------------------------------------------------------------------
    # 2. Apply burn-in
    # ------------------------------------------------------------------
    n_rows = len(log_df)
    if burnin < 0 or burnin >= n_rows:
        raise ValueError(
            f"burn-in value {burnin} is out of range for a log with {n_rows} rows."
        )
    if 0 < burnin < 1:
        burn_rows = int(n_rows * burnin)
    else:
        burn_rows = int(burnin)
    log_df = log_df.iloc[burn_rows:].reset_index(drop=True)

    # ------------------------------------------------------------------
    # 3. Build a set of stripped location names for fast membership testing
    # ------------------------------------------------------------------
    loc_set = {str(loc).strip() for loc in location_list}

    # ------------------------------------------------------------------
    # 4. Detect and map Markov jump columns → (start, end)
    # ------------------------------------------------------------------
    jump_col_map = {}  # (start, end) -> column_name

    for col in log_df.columns:
        pair = _try_parse_beast1(col, location_trait, loc_set)
        if pair is None:
            pair = _try_parse_beast2(col, location_trait, loc_set)
        if pair is not None:
            start, end = pair
            # If multiple columns map to the same pair (shouldn't happen),
            # prefer the first one found.
            if (start, end) not in jump_col_map:
                jump_col_map[(start, end)] = col

    if not jump_col_map:
        raise ValueError(
            f"No Markov jump count columns found for trait '{location_trait}'. "
            f"Expected patterns like 'c_{location_trait}.{{A}}to{{B}}[1]' (BEAST 1) "
            f"or '{location_trait}.actual_jumps.{{A}}.{{B}}' (BEAST 2)."
        )

    # ------------------------------------------------------------------
    # 5. Compute posterior means
    # ------------------------------------------------------------------
    jump_weights = {}
    for (start, end), col_name in jump_col_map.items():
        jump_weights[(start, end)] = float(log_df[col_name].mean())

    return jump_weights


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _try_parse_beast1(col, location_trait, loc_set):
    """
    Attempt to parse a BEAST 1 Markov jump column name.

    Pattern:  c_{trait}.{A}to{B}[N]

    Because location names may contain the substring 'to' (e.g. "Togo",
    "Central America"), we try every possible split point and return the
    first one where both halves are valid location names.
    """
    # Quick prefix/suffix screen before doing expensive work
    prefix = f"c_{location_trait}."
    if not col.startswith(prefix):
        return None

    # Strip the trailing bracket annotation, e.g. "[1]"
    body = col[len(prefix):]           # "{A}to{B}[N]"
    body = re.sub(r'\[\d+\]$', '', body)   # "{A}to{B}"

    # Find all occurrences of 'to' in the body and try each as a split point
    for m in re.finditer('to', body):
        candidate_start = body[:m.start()]
        candidate_end = body[m.end():]
        if candidate_start in loc_set and candidate_end in loc_set:
            return (candidate_start, candidate_end)

    return None


def _try_parse_beast2(col, location_trait, loc_set):
    """
    Attempt to parse a BEAST 2 Markov jump column name.

    Pattern:  {trait}.actual_jumps.{A}.{B}

    Because location names may contain '.' (unlikely but possible), we
    try every possible split position in the suffix after 'actual_jumps.'.
    """
    prefix = f"{location_trait}.actual_jumps."
    if not (f".actual_jumps." in col and col.startswith(f"{location_trait}.")):
        return None

    suffix = col[len(prefix):]  # "{A}.{B}"

    # Try every dot as a split point
    parts = suffix.split('.')
    for i in range(1, len(parts)):
        candidate_start = '.'.join(parts[:i])
        candidate_end = '.'.join(parts[i:])
        if candidate_start in loc_set and candidate_end in loc_set:
            return (candidate_start, candidate_end)

    return None
