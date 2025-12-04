# UK Counties and Local Authorities Supabase Import — Acquisition, Transformation, Validation, and Delivery Plan

## 1. Purpose, Scope, and Outcomes

This implementation and QA plan sets out how to acquire, transform, validate, and deliver United Kingdom counties and local authorities datasets into Supabase for two target tables: counties and local_authority_areas. The scope covers the authoritative Office for National Statistics (ONS) Names & Codes products for administrative geographies, specifically the County and Unitary Authority (December 2024) Names and Codes in the UK and the Local Authority Districts (April 2025) Names and Codes in the UK. These datasets provide the official names, nine-character Government Statistical Service (GSS) codes, and, where applicable, Welsh language names for the UK’s administrative units[^5][^6].

The delivery objective is to produce clean, consistent, and policy-compliant import files—CSVs—aligned to the schema expectations of the counties and local_authority_areas tables. This plan ensures that the resulting data can be used for lookups, analytics, and geocoding joins with confidence. Because the naming and coding products are maintained under the Open Government Licence (OGL) v3.0, the import pipeline will preserve attribution metadata and provenance for every record[^8].

### 1.1 Deliverables and Success Criteria

Deliverables include two import CSVs ready for Supabase ingestion:
- data/import/counties/counties_import_supabase.csv
- data/import/local_authorities/local_authorities_import_supabase.csv

Success will be measured by:
- Schema conformity: field names and types match target tables; required fields are present; naming is consistent.
- Referential integrity: clean GSS codes; no duplicates; country assignments are consistent with code prefixes.
- Provenance: each record carries a clear source_reference; the pipeline documents date-as-at and licence attribution.
- UK coverage completeness: England, Wales, Scotland, and Northern Ireland are represented in line with the source packs.
- Welsh-name handling: where present, preserved; otherwise, set to null without empty-string injection.

## 2. Source Inventory and Acquisition Traceability

ONS maintains current names and GSS nine-character codes for administrative geographies and provides CSV/Excel downloads through the Open Geography Portal. The two source datasets selected for this import are the definitive Names & Codes packs for counties/unitary authorities and local authority districts[^3][^5][^6].

The County and Unitary Authority (December 2024) Names and Codes in the UK provides UK coverage and includes CTYUA24CD/CTYUA24NM/CTYUA24NMW fields. The Local Authority Districts (April 2025) Names and Codes in the UK (V2) provides UK coverage and includes LAD25CD/LAD25NM/LAD25NMW fields[^5][^6]. Both packs are distributed via ArcGIS Hub REST endpoints, with CSV downloads exposed on the Open Geography Portal[^1][^2][^4].

To anchor provenance, the pipeline records dataset titles, as-at dates, and download references. Because the ArcGIS download URLs are persistent links tied to specific items, they serve as stable acquisition points; the dataset pages confirm the as-at coverage and update cadence[^4][^5][^6].

To illustrate coverage and acquisition details, Table 1 summarises the two sources.

Table 1. Source summary
| Dataset | As-at date | Coverage | Key fields | Download reference | Licence |
|---|---|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes in the UK | 31 December 2024 | UK | CTYUA24CD, CTYUA24NM, CTYUA24NMW | See References [^5] | OGL v3.0 |
| Local Authority Districts (Apr 2025) Names and Codes in the UK (V2) | 1 April 2025 | UK | LAD25CD, LAD25NM, LAD25NMW | See References [^6] | OGL v3.0 |

#### 2.1 Download Paths and Checksums

The pipeline records the provenance for each source pack: dataset title, as-at date, source URL, and file size. While exact checksum hashing (e.g., SHA-256) is optional for ONS CSV downloads, the pipeline documents the date of retrieval and checks file size for sanity. If reproducibility at byte-level is required (e.g., for regulated audits), implement hashing pre- and post-transfer and store the hash in metadata. Where CSV integrity is in doubt (e.g., truncation), re-download from the authoritative page[^5][^6][^4].

Table 2. Download provenance log
| Dataset | As-at date | Source reference | Retrieved date | File size (bytes) | SHA-256 (optional) |
|---|---|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes | 31 Dec 2024 | See References [^5] | [YYYY-MM-DD] | [number] | [hash] |
| Local Authority Districts (Apr 2025) Names and Codes (V2) | 1 Apr 2025 | See References [^6] | [YYYY-MM-DD] | [number] | [hash] |

## 3. Target Schema Alignment and Field Mapping

The source fields map directly to the target tables and columns. Names are preserved as provided by ONS; codes are used as the canonical identifiers. Welsh names are only populated where a value exists in the source file; otherwise, fields are set to null. A country field is derived from the GSS code prefix, and an authority_type is inferred from the dataset family and code ranges. The source_reference captures the dataset name and as-at date for full auditability[^5][^6].

Table 3. Field mapping — counties
| Source dataset | Source column | Target column | Data type | Transform / notes |
|---|---|---|---|---|
| CTYUA (Dec 2024) | CTYUA24CD | gss_county_code | text | Direct map; canonical identifier[^5] |
| CTYUA (Dec 2024) | CTYUA24NM | county_name | text | Direct map; preserve casing[^5] |
| CTYUA (Dec 2024) | CTYUA24NMW | county_name_welsh | text | Null if empty; no empty-string[^5] |
| — | — | country | text | Derive from GSS prefix: E/W/S/N[^3] |
| — | — | authority_type | text | Derive: E10→County; E06/W06/S12/N09→Unitary Authority; E10 exceptions via authoritative list[^5] |
| — | — | source_reference | text | “County and Unitary Authority (Dec 2024) Names and Codes; as at 31 Dec 2024” |

Table 4. Field mapping — local_authority_areas
| Source dataset | Source column | Target column | Data type | Transform / notes |
|---|---|---|---|---|
| LAD (Apr 2025) | LAD25CD | gss_la_code | text | Direct map; canonical identifier[^6] |
| LAD (Apr 2025) | LAD25NM | la_name | text | Direct map; preserve casing[^6] |
| LAD (Apr 2025) | LAD25NMW | la_name_welsh | text | Null if empty; no empty-string[^6] |
| — | — | country | text | Derive from GSS prefix: E/W/S/N[^3] |
| — | — | authority_type | text | Derive from dataset family/code: E07→District; E08→Metropolitan District; E09→London Borough; E06/W06/S12/N09→Unitary Authority[^6] |
| — | — | source_reference | text | “Local Authority Districts (Apr 2025) Names and Codes (V2); as at 1 Apr 2025” |

### 3.1 Authority Type derivation rules

Authority types are inferred to support analysis and presentation. For counties and unitary authorities, code ranges and official naming guidance from the ONS packs support a clear set of rules; for local authority districts, the LAD codes embed typology. The general principle is to use the GSS code family to determine the type, cross-checking against official lists where required[^5][^6][^3].

Table 5. Authority type decision table
| Dataset | GSS code pattern | Inferred type | Notes |
|---|---|---|---|
| Counties & UA | E10xxxxxx | County | England counties (e.g., E10000003 = Cambridgeshire) |
| Counties & UA | E06xxxxxx | Unitary Authority | England unitary authorities |
| Counties & UA | W06xxxxxx | Unitary Authority | Wales unitary authorities |
| Counties & UA | S12xxxxxx | Council Area | Scotland council areas (treated as unitary for many analytics) |
| Counties & UA | N09xxxxxx | Unitary Authority | Northern Ireland local government districts |
| LADs | E07xxxxxx | District | England districts |
| LADs | E08xxxxxx | Metropolitan District | England metropolitan districts |
| LADs | E09xxxxxx | London Borough | England London boroughs |
| LADs | E06xxxxxx | Unitary Authority | England unitary authorities |
| LADs | W06xxxxxx | Unitary Authority | Wales unitary authorities |
| LADs | S12xxxxxx | Unitary Authority | Scotland council areas/unitary authorities |
| LADs | N09xxxxxx | Unitary Authority | Northern Ireland local government districts |

Edge cases—such as county exemplars that behave as unitary authorities—should be resolved against authoritative list annotations and, if necessary, the Code History Database to reflect historical reclassifications[^9].

## 4. Transformation Specification

The transformation pipeline is intentionally minimal, ensuring fidelity to ONS names and codes while adding derived metadata needed by the target tables.

- Names: preserve source casing and diacritics; trim leading/trailing whitespace; do not re-case.
- Codes: uppercase and validate against nine-character GSS pattern; the first character identifies the country: E (England), W (Wales), S (Scotland), N (Northern Ireland)[^3].
- Welsh names: retain as provided; if absent or empty, set to null.
- Country: derive from GSS prefix; cross-check against ONS listings if anomalies are detected.
- Authority type: apply decision rules (Table 5) derived from code families and dataset context.
- Provenance: write a single source_reference field per record, including dataset name and “as at” date.
- CSV hygiene: enforce UTF-8 encoding; use RFC 4180 quoting; ensure consistent headers; produce Unix line endings.

Table 6. Normalization rules checklist
| Rule | Target columns | Implementation |
|---|---|---|
| Trim whitespace | county_name, county_name_welsh, la_name, la_name_welsh | Trim all string fields; reject if null after trim |
| Unicode normalization | all name fields | Normalize to NFC; preserve accented characters |
| Uppercasing | gss_county_code, gss_la_code | Uppercase before validation |
| Welsh name handling | county_name_welsh, la_name_welsh | Null if empty; do not insert empty strings |
| Country derivation | country | From GSS prefix; country must be one of England/Wales/Scotland/Northern Ireland |
| Authority typing | authority_type | Apply decision rules; log anomalies |
| Provenance | source_reference | Always set to dataset name plus as-at date |

### 4.1 Country derivation from GSS prefix

Country derivation is deterministic and is used to validate completeness across the UK. The mapping below is applied consistently[^3].

Table 7. Country derivation mapping
| Prefix | Country |
|---|---|
| E | England |
| W | Wales |
| S | Scotland |
| N | Northern Ireland |

## 5. Validation and Quality Assurance

Quality assurance combines schema checks, uniqueness and referential integrity validations, and country coverage confirmations. Because GSS codes are the canonical identifiers, they must be unique within their respective tables and conform to the expected pattern. Welsh-name fields are optional; empty values are set to null rather than empty strings to preserve clean semantics.

The QA plan also includes anomaly detection on authority_type assignments—especially for E10 counties—and quick checks for name changes or reclassifications using authoritative listings and the Code History Database (CHD)[^9]. The CHM/CHD can help confirm whether a code has been retired or recoded over time, which is essential for stable analytics[^10].

Table 8. QA checklist
| Check | Target | Rule | Expected outcome |
|---|---|---|---|
| Header conformity | Both files | Headers match mapping specification | Pass; otherwise, fail and remediate |
| Code uniqueness | counties, local_authority_areas | GSS codes are unique | Pass; duplicates blocked |
| Code pattern | Both files | 9-character GSS: ^[ENWS]\d{8}$ | Pass; invalid codes reported |
| Country coverage | Both files | E/W/S/N present | Coverage balanced with source packs |
| Authority type | Both files | Type inferred matches code family | Pass; exceptions flagged |
| Welsh name handling | Both files | Empty→null | Clean semantics; no empty strings |
| Nullability | Both files | Required fields non-null | Pass; reject if not |
| Provenance | Both files | source_reference present | Traceability preserved |

Table 9. Country coverage verification
| Dataset | E | W | S | N | Notes |
|---|---|---|---|---|---|
| Counties & UA | [count] | [count] | [count] | [count] | Align to ONS pack totals[^5] |
| LADs | [count] | [count] | [count] | [count] | Align to ONS pack totals[^6] |

### 5.1 Duplicate and Anomaly Rules

Duplicates on GSS codes are blocked. Name variants are not merged unless supported by official listings or CHD entries documenting reclassification. Where a single name appears in both packs but with differing codes, records are kept distinct and investigated; if a code change is confirmed via CHD, historical continuity can be modelled using start/end dates in downstream schema if needed[^9].

## 6. Output Packaging and Delivery

The transformation produces two CSVs:
- data/import/counties/counties_import_supabase.csv
- data/import/local_authorities/local_authorities_import_supabase.csv

File conventions include UTF-8 encoding, RFC 4180 quoting, a header row matching the target schema, and Unix line endings. Each row includes a source_reference field with dataset name and as-at date to guarantee traceability. Counts and summaries are validated post-export and documented for the QA sign-off.

Table 10. Import file manifest
| File path | Rows | Columns | Size (bytes) | Hash (optional) |
|---|---|---|---|---|
| data/import/counties/counties_import_supabase.csv | [number] | 7 | [number] | [hash] |
| data/import/local_authorities/local_authorities_import_supabase.csv | [number] | 7 | [number] | [hash] |

## 7. Licensing, Attribution, and Compliance

The datasets are provided under the Open Government Licence v3.0. Attribution to the Office for National Statistics is required, and the “as at” date must be persisted alongside each record. The Open Geography Portal is the definitive access point for Names & Codes and boundary products, and users must include the appropriate OGL attribution text in downstream outputs[^8][^4].

Table 11. Attribution manifest
| Dataset | Attribution text | As-at date | Source reference |
|---|---|---|---|
| County and Unitary Authority (Dec 2024) Names and Codes | “Contains public sector information licensed under the Open Government Licence v3.0.” | 31 Dec 2024 | See References [^5] |
| Local Authority Districts (Apr 2025) Names and Codes (V2) | “Contains public sector information licensed under the Open Government Licence v3.0.” | 1 Apr 2025 | See References [^6] |

## 8. Refresh and Maintenance Plan

The refresh cadence is annual, aligned to ONS release cycles: Counties & Unitary Authorities are typically updated in December; Local Authority Districts in April. The pipeline is designed to be idempotent: on each refresh, codes are the stable key, names are reconciled, and authority_type is re-derived to reflect any reclassifications. Where reclassifications occur, the Code History Database is consulted to document changes and drive a decision on whether to create new records or update existing ones with effective dates[^3][^9][^10].

Table 12. Refresh schedule
| Dataset | Last as-at | Next expected window | Owner | Status |
|---|---|---|---|---|
| County and Unitary Authority Names & Codes | Dec 2024 | Dec 2025 | Data Ops | Scheduled |
| Local Authority Districts Names & Codes (V2) | Apr 2025 | Apr 2026 | Data Ops | Scheduled |

## 9. Risks and Mitigations

Licensing and schema stability are well understood for ONS Names & Codes. The main risks involve schema drift, misalignment between county and LAD references, and missing Welsh names. These are mitigated through validation, targeted lookups, and clear provenance.

Table 13. Risk register
| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Schema drift in source columns | Low | Medium | Monitor ONS listings; implement contract tests on headers; fail-fast | Data Ops |
| Missing Welsh names | Medium | Low | Preserve nulls; do not inject empty strings; document coverage | Data Ops |
| County↔LAD alignment inconsistencies | Medium | Medium | Use latest LAD→County/UA lookup for cross-checking; flag mismatches[^7] | Data Governance |
| OGL attribution omission | Low | High | Persist attribution_text per dataset; compliance checks in QA[^8] | Legal |
| Reclassification events | Medium | Medium | Consult CHD; version records; update authority_type responsibly[^9] | Data Governance |

## 10. Appendices

The appendices provide a compact view of file layouts and decision rules to support audit and future maintenance.

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
| E10 | County | ONS County & UA pack; official listings[^5][^3] |
| E06/W06/N09 | Unitary Authority | ONS Names & Codes packs[^5][^6] |
| S12 | Council Area (unitary) | ONS Names & Codes packs[^5][^6] |
| E07 | District | LAD pack[^6] |
| E08 | Metropolitan District | LAD pack[^6] |
| E09 | London Borough | LAD pack[^6] |

## Information Gaps and Assumptions

- The exact Supabase column types for counties and local_authority_areas should be confirmed by the integration owner. This plan assumes text for names and codes, text for country and authority_type, and text for source_reference.
- The final choice of primary keys (surrogate UUID vs natural key) should be confirmed. This plan assumes natural keys via GSS codes for lookups, with UUIDs added in the database if required by the application layer.
- Whether to persist Welsh names when absent is specified here as null; confirm that empty strings are not acceptable in the target schema.
- If checksum hashing is required for audit reproducibility, implement SHA-256 on downloaded files and store it in metadata.

## References

[^1]: Administrative Names and Codes — Open Geography Portal search. https://geoportal.statistics.gov.uk/datasets?q=Names+and+Codes+for+ONSPD+and+NSPL&sort_by=name  
[^2]: Names and codes for administrative geographies — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/namesandcodeslistings/namesandcodesforadministrativegeography  
[^3]: Names and codes listings — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/namesandcodeslistings  
[^4]: Open Geography Portal. https://geoportal.statistics.gov.uk/  
[^5]: County and Unitary Authority (December 2024) Names and Codes in the UK — data.gov.uk. https://www.data.gov.uk/dataset/79b1ab91-4fb9-4a66-abc7-ddfba7027c73/county-and-unitary-authority-december-2024-names-and-codes-in-the-uk  
[^6]: Local Authority Districts (April 2025) Names and Codes in the UK (V2) — data.gov.uk. https://www.data.gov.uk/dataset/b2c91962-58e7-40f1-ad56-7aa2473a93fd/local-authority-districts-april-2025-names-and-codes-in-the-uk-v21  
[^7]: Local Authority District to County and Unitary Authority (April 2025) Lookup in EW (V2) — data.gov.uk. https://www.data.gov.uk/dataset/a76a9de2-d0f4-4fd7-bcc9-e63bbf28bbb5/local-authority-district-to-county-and-unitary-authority-april-2025-lookup-in-ew-v21  
[^8]: Open Government Licence v3.0 — The National Archives. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/  
[^9]: Code History Database (CHD) — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/codehistorydatabasechd  
[^10]: Register of Geographic Codes (RGC) — Office for National Statistics. https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups/registerofgeographiccodes