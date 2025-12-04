# UK Counties and Local Authorities Data Import: Acquisition, Transformation, Validation, and Supabase Delivery Blueprint

## Executive Summary

This blueprint sets out a definitive, compliant pathway to acquire, transform, validate, and deliver United Kingdom administrative geography datasets into Supabase—specifically the counties and local_authority_areas tables. The work draws exclusively on official Office for National Statistics (ONS) Names & Codes products, accessed through the Open Geography Portal, and culminates in production-ready import files aligned to the project’s database schema and operating procedures.

The acquisition plan prioritizes the following authoritative sources: the County and Unitary Authority (December 2024) Names and Codes in the UK, and the Local Authority Districts (April 2025) Names and Codes in the UK (V2). These are the definitive lists of names, nine-character Government Statistical Service (GSS) codes, and Welsh-language names (where present) for UK administrative geographies[^1][^2]. The transformation approach emphasizes minimal handling to preserve fidelity, clear derivation rules for country and authority_type, and explicit handling of Welsh names. Validation ensures schema conformity, uniqueness and referential integrity (via GSS codes), country coverage across England, Wales, Scotland, and Northern Ireland, and correct authority typing.

The licensing foundation is the Open Government Licence (OGL) v3.0, with attribution statements captured in metadata and propagated to product outputs as required. Refresh governance will follow ONS release cycles: Counties & Unitary Authorities typically update in December; Local Authority Districts in April. The pipeline will be versioned, idempotent, and designed to handle schema drift and boundary changes with reference to ONS’s Code History Database (CHD) for reclassifications and code continuity[^5][^6].

## Objectives, Scope, and Success Criteria

The objective is to integrate authoritative administrative geography data into Supabase for use in lookup, analytics, and address-related joins. The scope includes two authoritative ONS Names & Codes datasets:
- Counties and Unitary Authorities (December 2024)
- Local Authority Districts (April 2025, V2)

Both datasets cover the UK, provide current names and GSS codes, and include Welsh names where applicable[^1][^2]. Deliverables comprise two import CSV files (counties and local_authority_areas), provenance and attribution metadata persisted in tables, and QA evidence packs.

Success criteria:
- Schema conformity and alignment to the project’s counties and local_authority_areas tables.
- Uniqueness and validity of GSS codes; clean handling of Welsh names (null when absent).
- Country coverage across the UK.
- Authority types correctly derived from code families.
- OGL v3.0 attribution retained and visible in metadata outputs.

## Authoritative Source Inventory and Acquisition Traceability

ONS maintains Names & Codes for administrative geographies via the Open Geography Portal. The two datasets selected are published with clear as-at dates and provide the necessary fields for integration[^1][^2][^3][^4].

To illustrate the acquisition footprint, Table 1 summarises the datasets.

Table 1. Source summary
| Dataset | As-at date | Coverage | Key fields | Download reference | Licence |
|---|---|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes in the UK | 31 December 2024 | UK | CTYUA24CD, CTYUA24NM, CTYUA24NMW | See References [^1] | OGL v3.0 |
| Local Authority Districts (Apr 2025) Names and Codes in the UK (V2) | 1 April 2025 | UK | LAD25CD, LAD25NM, LAD25NMW | See References [^2] | OGL v3.0 |

### Download and Integrity Checks

The acquisition process records dataset titles, as-at dates, retrieval dates, and file sizes, and optionally computes SHA-256 checksums for reproducibility. The OGL v3.0 requires attribution statements to be preserved and exposed in downstream outputs; these are logged alongside each dataset to ensure compliance[^6].

Table 2. Download provenance log
| Dataset | As-at date | Source reference | Retrieved date | File size (bytes) | SHA-256 (optional) |
|---|---|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes | 31 Dec 2024 | See References [^1] | [YYYY-MM-DD] | [number] | [hash] |
| Local Authority Districts (Apr 2025) Names and Codes (V2) | 1 Apr 2025 | See References [^2] | [YYYY-MM-DD] | [number] | [hash] |

## Schema Alignment and Field Mapping

ONS Names & Codes files provide three principal fields per dataset: a nine-character GSS code, an English name, and a Welsh name where applicable. The target tables—counties and local_authority_areas—map directly to these fields, with derived fields for country and authority_type to support analytics and reporting. The mapping is designed to minimize transformations, preserve naming fidelity, and ensure code stability[^1][^2][^3].

Table 3. Field mapping — counties
| Source dataset | Source column | Target column | Data type | Transform / notes |
|---|---|---|---|---|
| CTYUA (Dec 2024) | CTYUA24CD | gss_county_code | text | Direct map; canonical identifier[^1] |
| CTYUA (Dec 2024) | CTYUA24NM | county_name | text | Direct map; preserve casing[^1] |
| CTYUA (Dec 2024) | CTYUA24NMW | county_name_welsh | text | Null if empty; do not inject empty strings[^1] |
| — | — | country | text | Derive from GSS prefix: E/W/S/N[^3] |
| — | — | authority_type | text | Derive: E10→County; E06/W06/S12/N09→Unitary Authority; resolve E10 exceptions via authoritative listings[^1][^3] |
| — | — | source_reference | text | “County and Unitary Authority (Dec 2024) Names and Codes; as at 31 Dec 2024” |

Table 4. Field mapping — local_authority_areas
| Source dataset | Source column | Target column | Data type | Transform / notes |
|---|---|---|---|---|
| LAD (Apr 2025) | LAD25CD | gss_la_code | text | Direct map; canonical identifier[^2] |
| LAD (Apr 2025) | LAD25NM | la_name | text | Direct map; preserve casing[^2] |
| LAD (Apr 2025) | LAD25NMW | la_name_welsh | text | Null if empty; no empty strings[^2] |
| — | — | country | text | Derive from GSS prefix: E/W/S/N[^3] |
| — | — | authority_type | text | Derive: E07→District; E08→Metropolitan District; E09→London Borough; E06/W06/S12/N09→Unitary Authority[^2] |
| — | — | source_reference | text | “Local Authority Districts (Apr 2025) Names and Codes (V2); as at 1 Apr 2025” |

### Authority Type Derivation Rules

Authority types are inferred from the GSS code family and dataset provenance. These rules enable consistent classification while acknowledging special cases and historical reclassifications.

Table 5. Authority type decision table
| Dataset | GSS code pattern | Inferred type | Notes |
|---|---|---|---|
| Counties & UA | E10xxxxxx | County | England counties (e.g., Cambridgeshire E10000003) |
| Counties & UA | E06xxxxxx | Unitary Authority | England unitary authorities |
| Counties & UA | W06xxxxxx | Unitary Authority | Wales unitary authorities |
| Counties & UA | S12xxxxxx | Council Area | Scotland council areas (unitary behavior) |
| Counties & UA | N09xxxxxx | Unitary Authority | Northern Ireland local government districts |
| LADs | E07xxxxxx | District | England districts |
| LADs | E08xxxxxx | Metropolitan District | England metropolitan districts |
| LADs | E09xxxxxx | London Borough | England London boroughs |
| LADs | E06xxxxxx | Unitary Authority | England unitary authorities |
| LADs | W06xxxxxx | Unitary Authority | Wales unitary authorities |
| LADs | S12xxxxxx | Unitary Authority | Scotland council areas/unitary authorities |
| LADs | N09xxxxxx | Unitary Authority | Northern Ireland local government districts |

Where exceptions exist (e.g., counties with unitary functions), the authoritative Names & Codes listings and the Code History Database should be consulted to confirm current classification, ensuring consistent analytics over time[^1][^2][^5].

## Transformation Specification

The pipeline applies strict normalization rules to preserve data integrity while enabling derived fields essential for analysis:

- Names: preserve case and diacritics; trim whitespace; do not re-case.
- Codes: uppercase and validate against the nine-character GSS pattern; the first character encodes the country: E (England), W (Wales), S (Scotland), N (Northern Ireland)[^3].
- Welsh names: populate only when present in the source; otherwise, set to null (no empty strings).
- Country: derive consistently from the GSS prefix and cross-check against ONS listings if anomalies appear.
- Authority type: apply the decision rules; log exceptions for review.
- Provenance: write a source_reference containing the dataset name and as-at date.
- CSV hygiene: use UTF-8, RFC 4180 quoting, consistent headers, Unix line endings.

Table 6. Normalization rules checklist
| Rule | Target columns | Implementation |
|---|---|---|
| Trim whitespace | county_name, county_name_welsh, la_name, la_name_welsh | Trim strings; reject if required fields null post-trim |
| Unicode normalization | all name fields | Normalize to NFC |
| Uppercasing | gss_county_code, gss_la_code | Uppercase pre-validation |
| Welsh name handling | county_name_welsh, la_name_welsh | Set null if empty |
| Country derivation | country | From GSS prefix (E/W/S/N) |
| Authority typing | authority_type | From code families; log anomalies |
| Provenance | source_reference | Set to dataset name + as-at date |

### Country Derivation from GSS Prefix

The mapping below is authoritative and applied consistently across both tables[^3].

Table 7. Country derivation mapping
| Prefix | Country |
|---|---|
| E | England |
| W | Wales |
| S | Scotland |
| N | Northern Ireland |

## Validation and Quality Assurance

Quality assurance ensures the import files meet schema and integrity standards and reflect official source data. The checks cover uniqueness and pattern validity for GSS codes, correct assignment of country and authority type, and proper handling of Welsh names.

Table 8. QA checklist
| Check | Target | Rule | Expected outcome |
|---|---|---|---|
| Header conformity | Both files | Headers match mapping | Pass; remediation if mismatch |
| Code uniqueness | counties, local_authority_areas | No duplicate GSS | Pass; duplicates blocked |
| Code pattern | Both files | 9-character GSS: ^[ENWS]\d{8}$ | Pass; report invalid codes |
| Country assignment | Both files | Country derived from prefix | Pass; E/W/S/N represented |
| Authority type | Both files | Type inferred from code family | Pass; exceptions flagged |
| Welsh names | Both files | Null if empty | Clean semantics; no empty strings |
| Nullability | Both files | Required fields populated | Pass; reject if nulls found |
| Provenance | Both files | source_reference present | Full traceability |

Table 9. Country coverage verification
| Dataset | E | W | S | N | Notes |
|---|---|---|---|---|---|
| Counties & UA | [count] | [count] | [count] | [count] | Align to ONS pack totals[^1] |
| LADs | [count] | [count] | [count] | [count] | Align to ONS pack totals[^2] |

### Duplicate and Anomaly Rules

Duplicate GSS codes are prohibited. Name-only matches are not merged unless supported by official listings or CHD entries. Where reclassification events occur (e.g., district to unitary authority), CHD is the authoritative source for continuity; downstream systems can model effective dates if the schema supports versioning[^5].

## Output Packaging and Delivery

Two import CSVs are produced and delivered into the designated directories:
- data/import/counties/counties_import_supabase.csv
- data/import/local_authorities/local_authorities_import_supabase.csv

CSV files adhere to UTF-8 encoding, RFC 4180 quoting, and Unix line endings. Row counts and file sizes are verified post-export and recorded for audit.

Table 10. Import file manifest
| File path | Rows | Columns | Size (bytes) | Hash (optional) |
|---|---|---|---|---|
| data/import/counties/counties_import_supabase.csv | [number] | 7 | [number] | [hash] |
| data/import/local_authorities/local_authorities_import_supabase.csv | [number] | 7 | [number] | [hash] |

## Licensing, Attribution, and Compliance

The datasets are provided under the Open Government Licence v3.0. Attribution to ONS is mandatory, and the “as at” date must be retained alongside each record. The Open Geography Portal is the definitive source for Names & Codes and related boundary resources; all downstream outputs should include the appropriate OGL attribution statement[^6][^4].

Table 11. Attribution manifest
| Dataset | Attribution text | As-at date | Source reference |
|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes | “Contains public sector information licensed under the Open Government Licence v3.0.” | 31 Dec 2024 | See References [^1] |
| Local Authority Districts (Apr 2025) Names and Codes (V2) | “Contains public sector information licensed under the Open Government Licence v3.0.” | 1 Apr 2025 | See References [^2] |

## Refresh and Maintenance Plan

The refresh cadence follows ONS schedules:
- Counties & Unitary Authorities: December releases
- Local Authority Districts: April releases

The pipeline is designed to be idempotent. On each refresh, GSS codes act as stable natural keys; names are reconciled; authority_type is re-derived to reflect reclassifications. If reclassifications occur, CHD is consulted to document code changes and inform whether to update records or version them with effective dates[^3][^5].

Table 12. Refresh schedule
| Dataset | Last as-at | Next expected window | Owner | Status |
|---|---|---|---|---|
| County and Unitary Authority Names & Codes | Dec 2024 | Dec 2025 | Data Ops | Scheduled |
| Local Authority Districts Names & Codes (V2) | Apr 2025 | Apr 2026 | Data Ops | Scheduled |

## Risks and Mitigations

Licensing for Names & Codes is stable under OGL v3.0; the main risks involve schema drift, misalignment across administrative lookups, and completeness of Welsh names. These are mitigated through validation, governance processes, and explicit provenance.

Table 13. Risk register
| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Schema drift | Low | Medium | Contract tests; fail-fast on header changes | Data Ops |
| Welsh names sparsity | Medium | Low | Persist nulls; document coverage | Data Ops |
| County↔LAD alignment | Medium | Medium | Use latest LAD→County/UA lookup for checks[^7] | Data Governance |
| Attribution omission | Low | High | Persist attribution_text; QA checks[^6] | Legal |
| Reclassification events | Medium | Medium | Consult CHD; version where appropriate[^5] | Data Governance |

## Appendices

Appendix A. CSV layouts

Table 14. Counties import CSV layout
| Column | Type | Nullable | Example |
|---|---|---|---|
| county_name | text | No | “Cambridgeshire” |
| county_name_welsh | text | Yes | null |
| gss_county_code | text | No | “E10000003” |
| country | text | No | “England” |
| authority_type | text | No | “County” |
| source_reference | text | No | “County and Unitary Authority (Dec 2024) Names and Codes; as at 31 Dec 2024” |

Table 15. Local authority areas import CSV layout
| Column | Type | Nullable | Example |
|---|---|---|---|
| la_name | text | No | “South Cambridgeshire” |
| la_name_welsh | text | Yes | null |
| gss_la_code | text | No | “E07000012” |
| country | text | No | “England” |
| authority_type | text | No | “District” |
| source_reference | text | No | “Local Authority Districts (Apr 2025) Names and Codes (V2); as at 1 Apr 2025” |

Appendix B. Country derivation mapping

Table 16. Country mapping
| GSS prefix | Country |
|---|---|
| E | England |
| W | Wales |
| S | Scotland |
| N | Northern Ireland |

Appendix C. Authority type decision rules

Table 17. Authority type decision rules (summary)
| Code family | Type | Source of rule |
|---|---|---|
| E10 | County | ONS County & UA pack; official listings[^1][^3] |
| E06/W06/N09 | Unitary Authority | ONS Names & Codes packs[^1][^2] |
| S12 | Council Area (unitary) | ONS Names & Codes packs[^1][^2] |
| E07 | District | LAD pack[^2] |
| E08 | Metropolitan District | LAD pack[^2] |
| E09 | London Borough | LAD pack[^2] |

## Information Gaps and Assumptions

- Supabase target column types for counties and local_authority_areas should be confirmed by the integration owner; the blueprint assumes text for names/codes and metadata.
- Primary key strategy (surrogate UUID versus natural key via GSS code) should be finalized; GSS codes are unique and suitable as natural keys.
- Welsh-language field coverage varies; absence is recorded as null, not empty strings.
- Where Northern Ireland specifics require additional permissions or separate packs, the refresh governance will document any bespoke steps.

## References

[^1]: County and Unitary Authority (December 2024) Names and Codes in the UK — data.gov.uk. https://www.data.gov.uk/dataset/79b1ab91-4fb9-4a66-abc7-ddfba7027c73/county-and-unitary-authority-december-2024-names-and-codes-in-the-uk  
[^2]: Local Authority Districts (April 2025) Names and Codes in the UK (V2) — data.gov.uk. https://www.data.gov.uk/dataset/b2c91962-58e7-40f1-ad56-7aa2473a93fd/local-authority-districts-april-2025-names-and-codes-in-the-uk-v21  
[^3]: Names and codes listings — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/namesandcodeslistings  
[^4]: Open Geography Portal. https://geoportal.statistics.gov.uk/  
[^5]: Code History Database (CHD) — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/codehistorydatabasechd  
[^6]: Open Government Licence v3.0 — The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
[^7]: Local Authority District to County and Unitary Authority (April 2025) Lookup in EW (V2) — data.gov.uk. https://www.data.gov.uk/dataset/a76a9de2-d0f4-4fd7-bcc9-e63bbf28bbb5/local-authority-district-to-county-and-unitary-authority-april-2025-lookup-in-ew-v21