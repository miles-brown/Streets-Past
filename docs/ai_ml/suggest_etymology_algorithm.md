# suggest-etymology Edge Function — Algorithm Documentation

## Overview

The `suggest-etymology` Supabase Edge Function (`supabase/functions/suggest-etymology/index.ts`) provides AI-assisted etymology suggestions for UK street names using a rule-based linguistic pattern matching engine. It runs on the Deno runtime and is invoked via HTTP POST.

## API

**Endpoint**: `POST /functions/v1/suggest-etymology`

**Request**:
```json
{ "streetName": "High Street" }
```

**Response**:
```json
{
  "data": {
    "streetName": "High Street",
    "etymology": "\"High\" derives from Old English \"heah\", meaning \"principal or main\" (Various). \"Street\" derives from Latin via Old English, meaning \"paved road (from 'strata via' - layered way)\" (Roman/Early Medieval).\n\nThis street name contains elements from: Various, Roman/Early Medieval.\n\nFor definitive etymology, consult: local county archives, Ordnance Survey historical maps, and publications by the English Place-Name Society or relevant regional societies.",
    "elements": [
      { "element": "street", "info": { "origin": "Latin via Old English", "meaning": "paved road (from 'strata via' - layered way)", "period": "Roman/Early Medieval" } },
      { "element": "high", "info": { "meaning": "principal or main", "origin": "Old English \"heah\"", "period": "Various" } }
    ],
    "confidence": "medium",
    "sources": [
      "English Place-Name Society publications",
      "Oxford Dictionary of English Place-Names",
      "Institute of Name-Studies, University of Nottingham"
    ]
  }
}
```

**Error Response** (500):
```json
{
  "error": {
    "code": "ETYMOLOGY_ERROR",
    "message": "Street name is required"
  }
}
```

## Algorithm Steps

### 1. Input Validation
Parses JSON body and requires a non-empty `streetName` field.

### 2. Normalization
```
streetName → lowercase → trim → split on whitespace → words[]
```

### 3. Suffix/Word Pattern Matching
Iterates over 57 etymology patterns. For each pattern, checks:
- Does the normalized name **end with** the pattern? (`nameLower.endsWith(pattern)`)
- Is the pattern present as a **whole word**? (`words.includes(pattern)`)

If either matches, the element and its metadata (origin, meaning, historical period) are added to `foundElements[]`.

### 4. Prefix/Word Pattern Matching
Iterates over 34 prefix patterns. For each pattern, checks:
- Does the normalized name **start with** the pattern? (`nameLower.startsWith(pattern)`)
- Is the pattern present as a **whole word**? (`words.includes(pattern)`)

Matched prefixes are added to `foundElements[]` with `period: "Various"`.

### 5. Deduplication
Filters `foundElements[]` to keep only the first occurrence of each element name:
```ts
foundElements = foundElements.filter((v, i, a) =>
  a.findIndex(t => t.element === v.element) === i
);
```

### 6. Suggestion Generation

**If elements were found** (confidence: `"medium"`):
1. Build a sentence for each element: `"<Element>" derives from <origin>, meaning "<meaning>" (<period>).`
2. Collect unique historical periods and add: `This street name contains elements from: <periods>.`
3. Append research recommendation.

**If no elements found** (confidence: `"low"`):
1. Generic suggestion about possible person/landmark/event naming.
2. Suggest consulting local historical records (tithe maps, census, archives).
3. Append research recommendation.

### 7. Response
Returns JSON with CORS headers (`Access-Control-Allow-Origin: *`). OPTIONS requests return 200 for CORS preflight.

## Pattern Database

### Suffix Patterns (57 entries)

| Category | Patterns | Origin |
|----------|----------|--------|
| **Road types** | gate, street, lane, way, road, close, court, place, row, alley, passage, walk, drive | ON, Latin/OE, OE, OF |
| **Geographic features** | hill, green, field, ford, bridge, heath, moor, meadow, grove, wood | OE |
| **Settlement elements** | bury, ton, ham, stead, worth, wick, croft, yard | OE |
| **Old Norse elements** | gate ("gata"), kirk, toft, thorpe, by, beck, thwaite | ON (Viking Age 793-1066) |
| **Religious/Military** | church, castle, abbey, priory | OE, Norman French, Latin/OF |
| **Commerce** | mill, market, cheap ("ceap"), shambles ("scamel") | OE, Medieval |
| **Modern (17th-19th c.)** | parade, terrace, crescent, square, circus, avenue, boulevard, mews, gardens, park | French, Latin |

**Origin key**: OE = Old English, ON = Old Norse, OF = Old French

### Prefix Patterns (34 entries)

| Category | Patterns | Origin |
|----------|----------|--------|
| **Descriptive** | high, low, old, new, great, little, long, broad | OE, ON |
| **Directional** | north, south, east, west, upper, lower | OE |
| **Colors** | white ("hwit"), black ("blaec"), green ("grene"), red ("read"), golden ("gylden"), silver ("seolfor") | OE |
| **Nobility** | royal, king ("cyning"), queen ("cwen"), prince, duke, lord ("hlaford") | OE, OF |
| **Landmarks** | abbey ("abbatia"), church ("cirice"), mill ("mylen"), cross ("cros"), fleet ("fleot"), well ("wella"), spring | OE, Latin |

## Historical Periods Covered

| Period | Date Range | Example Elements |
|--------|-----------|-----------------|
| Roman/Early Medieval | ~43-410 AD | street |
| Anglo-Saxon | ~410-793 AD | lane, way, hill, field, bury, ham, ton |
| Viking Age | 793-1066 AD | gate, kirk, toft, thorpe, by, beck, thwaite |
| Norman | post-1066 | close, court, castle |
| Medieval | ~1066-1500 | road, mill, market, abbey, alley |
| 17th-18th century | 1600-1800 | square, avenue |
| 18th-19th century | 1700-1900 | parade, terrace, crescent, circus, boulevard, mews |
| 19th-20th century | 1800-2000 | drive |

## Limitations

- **No person-name detection**: Cannot identify streets named after individuals (e.g., "Wellington Road")
- **No compound analysis**: Treats multi-word patterns only as prefix + suffix, not internal elements
- **No geographic context**: Same analysis regardless of whether street is in Yorkshire (Norse influence) or Devon (Saxon influence)
- **Static patterns**: No learning or adaptation from user contributions
- **English-centric**: Welsh, Scottish Gaelic, and Cornish elements not covered

## Extending the Pattern Database

To add new patterns, edit the `etymologyPatterns` or `prefixPatterns` objects in `supabase/functions/suggest-etymology/index.ts`:

```ts
// Add to etymologyPatterns for suffix/word matching:
'newpattern': { origin: 'Origin Language', meaning: 'description', period: 'Historical Period' },

// Add to prefixPatterns for prefix/word matching:
'newprefix': { meaning: 'description', origin: 'Origin Language "original word"' },
```

After editing, redeploy the Edge Function via the Supabase CLI:
```bash
supabase functions deploy suggest-etymology
```
