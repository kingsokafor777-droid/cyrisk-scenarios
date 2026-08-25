# ADR 0001: Keep the first corpus sealed, fictional, and non-currency

**Status:** Accepted

The first corpus consists only of committed fictional JSON with `synthetic-index-units`. It does not
accept remote records, runtime collection, or currency labels. This makes the regression harness
reproducible and constrains portfolio claims. Any future external-data integration must be a
separate versioned adapter with its own consent, provenance, privacy, and quality boundaries.
