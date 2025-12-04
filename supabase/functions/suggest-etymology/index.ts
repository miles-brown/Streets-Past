// AI Etymology Suggestion Edge Function
// Uses pattern matching and linguistic rules to suggest etymologies

Deno.serve(async (req) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Max-Age': '86400',
  };

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const { streetName } = await req.json();

    if (!streetName) {
      throw new Error('Street name is required');
    }

    // Etymology patterns database - common UK street name elements
    const etymologyPatterns: Record<string, { origin: string; meaning: string; period: string }> = {
      // Old English/Anglo-Saxon elements
      'gate': { origin: 'Old Norse', meaning: 'road, way, or street (from "gata")', period: 'Viking Age (793-1066)' },
      'street': { origin: 'Latin via Old English', meaning: 'paved road (from "strata via" - layered way)', period: 'Roman/Early Medieval' },
      'lane': { origin: 'Old English', meaning: 'narrow path or passage (from "lanu")', period: 'Anglo-Saxon' },
      'way': { origin: 'Old English', meaning: 'path or route (from "weg")', period: 'Anglo-Saxon' },
      'road': { origin: 'Old English', meaning: 'mounted journey (from "rad" - riding)', period: 'Medieval' },
      'close': { origin: 'Old French', meaning: 'enclosed space (from "clos")', period: 'Norman' },
      'court': { origin: 'Old French', meaning: 'enclosed yard or courtyard', period: 'Norman' },
      'place': { origin: 'Old French', meaning: 'open square or space', period: 'Medieval' },
      'row': { origin: 'Old English', meaning: 'line or series of houses', period: 'Medieval' },
      'hill': { origin: 'Old English', meaning: 'elevated ground (from "hyll")', period: 'Anglo-Saxon' },
      'green': { origin: 'Old English', meaning: 'grassy common area (from "grene")', period: 'Anglo-Saxon' },
      'field': { origin: 'Old English', meaning: 'open land (from "feld")', period: 'Anglo-Saxon' },
      'bury': { origin: 'Old English', meaning: 'fortified place (from "burh")', period: 'Anglo-Saxon' },
      'ford': { origin: 'Old English', meaning: 'river crossing place', period: 'Anglo-Saxon' },
      'bridge': { origin: 'Old English', meaning: 'structure over water (from "brycg")', period: 'Anglo-Saxon' },
      'mill': { origin: 'Old English', meaning: 'grain grinding place (from "mylen")', period: 'Medieval' },
      'market': { origin: 'Old English', meaning: 'trading place (from "market")', period: 'Medieval' },
      'church': { origin: 'Old English', meaning: 'Christian place of worship (from "cirice")', period: 'Anglo-Saxon' },
      'kirk': { origin: 'Old Norse', meaning: 'church (Scottish/Northern)', period: 'Viking Age' },
      'cheap': { origin: 'Old English', meaning: 'market or trading (from "ceap")', period: 'Anglo-Saxon' },
      'shambles': { origin: 'Old English', meaning: 'meat market or stalls (from "scamel" - bench)', period: 'Medieval' },
      'castle': { origin: 'Norman French', meaning: 'fortified residence', period: 'Norman (post-1066)' },
      'abbey': { origin: 'Latin via Old French', meaning: 'monastic building', period: 'Medieval' },
      'priory': { origin: 'Latin via Old French', meaning: 'religious house', period: 'Medieval' },
      'grove': { origin: 'Old English', meaning: 'small wood (from "graf")', period: 'Anglo-Saxon' },
      'wood': { origin: 'Old English', meaning: 'forested area (from "wudu")', period: 'Anglo-Saxon' },
      'heath': { origin: 'Old English', meaning: 'open uncultivated land (from "haeth")', period: 'Anglo-Saxon' },
      'moor': { origin: 'Old English', meaning: 'wasteland or marsh (from "mor")', period: 'Anglo-Saxon' },
      'meadow': { origin: 'Old English', meaning: 'grassland (from "maed")', period: 'Anglo-Saxon' },
      'croft': { origin: 'Old English', meaning: 'enclosed field (from "croft")', period: 'Anglo-Saxon' },
      'toft': { origin: 'Old Norse', meaning: 'homestead site', period: 'Viking Age' },
      'thorpe': { origin: 'Old Norse', meaning: 'outlying farmstead or village', period: 'Viking Age' },
      'by': { origin: 'Old Norse', meaning: 'farmstead or village (as suffix)', period: 'Viking Age' },
      'beck': { origin: 'Old Norse', meaning: 'stream or brook', period: 'Viking Age' },
      'thwaite': { origin: 'Old Norse', meaning: 'clearing in forest', period: 'Viking Age' },
      'wick': { origin: 'Old English', meaning: 'dwelling or trading place (from "wic")', period: 'Anglo-Saxon' },
      'ton': { origin: 'Old English', meaning: 'settlement or estate (from "tun")', period: 'Anglo-Saxon' },
      'ham': { origin: 'Old English', meaning: 'homestead or village', period: 'Anglo-Saxon' },
      'stead': { origin: 'Old English', meaning: 'place or site (from "stede")', period: 'Anglo-Saxon' },
      'worth': { origin: 'Old English', meaning: 'enclosure or homestead', period: 'Anglo-Saxon' },
      'parade': { origin: 'French', meaning: 'promenade or procession route', period: '18th-19th century' },
      'terrace': { origin: 'French', meaning: 'raised level platform or row of houses', period: '18th-19th century' },
      'crescent': { origin: 'Latin via French', meaning: 'curved street (from "crescere" - to grow)', period: '18th-19th century' },
      'square': { origin: 'Old French', meaning: 'open rectangular space', period: '17th-18th century' },
      'circus': { origin: 'Latin', meaning: 'circular open space', period: '18th-19th century' },
      'avenue': { origin: 'French', meaning: 'tree-lined approach road', period: '17th-19th century' },
      'boulevard': { origin: 'French', meaning: 'broad tree-lined street', period: '19th century' },
      'mews': { origin: 'Old French', meaning: 'falcon cages, later converted stables', period: '18th-19th century' },
      'yard': { origin: 'Old English', meaning: 'enclosed area (from "geard")', period: 'Anglo-Saxon' },
      'alley': { origin: 'Old French', meaning: 'narrow passage (from "alee")', period: 'Medieval' },
      'passage': { origin: 'Old French', meaning: 'narrow way or corridor', period: 'Medieval' },
      'walk': { origin: 'Old English', meaning: 'path for walking', period: 'Medieval' },
      'drive': { origin: 'Old English', meaning: 'private road to a house', period: '19th-20th century' },
      'gardens': { origin: 'Old North French', meaning: 'ornamental grounds', period: '19th century' },
      'park': { origin: 'Old French', meaning: 'enclosed game reserve, later public ground', period: 'Medieval/19th century' },
    };

    // Common descriptive prefixes
    const prefixPatterns: Record<string, { meaning: string; origin: string }> = {
      'high': { meaning: 'principal or main', origin: 'Old English "heah"' },
      'low': { meaning: 'lower in elevation or status', origin: 'Old Norse "lagr"' },
      'old': { meaning: 'original or historic', origin: 'Old English "eald"' },
      'new': { meaning: 'recently created', origin: 'Old English "neowe"' },
      'great': { meaning: 'large or important', origin: 'Old English "great"' },
      'little': { meaning: 'small or lesser', origin: 'Old English "lytel"' },
      'long': { meaning: 'extended in length', origin: 'Old English "lang"' },
      'broad': { meaning: 'wide', origin: 'Old English "brad"' },
      'north': { meaning: 'northern direction', origin: 'Old English "north"' },
      'south': { meaning: 'southern direction', origin: 'Old English "suth"' },
      'east': { meaning: 'eastern direction', origin: 'Old English "east"' },
      'west': { meaning: 'western direction', origin: 'Old English "west"' },
      'upper': { meaning: 'higher part', origin: 'Old English "uppor"' },
      'lower': { meaning: 'lower part', origin: 'Old English' },
      'white': { meaning: 'white-colored or pure', origin: 'Old English "hwit"' },
      'black': { meaning: 'dark-colored', origin: 'Old English "blaec"' },
      'green': { meaning: 'green-colored or grassy', origin: 'Old English "grene"' },
      'red': { meaning: 'red-colored', origin: 'Old English "read"' },
      'golden': { meaning: 'gold-colored or prosperous', origin: 'Old English "gylden"' },
      'silver': { meaning: 'silver-colored', origin: 'Old English "seolfor"' },
      'royal': { meaning: 'pertaining to royalty', origin: 'Old French "roial"' },
      'king': { meaning: 'pertaining to a king', origin: 'Old English "cyning"' },
      'queen': { meaning: 'pertaining to a queen', origin: 'Old English "cwen"' },
      'prince': { meaning: 'pertaining to a prince', origin: 'Old French "prince"' },
      'duke': { meaning: 'pertaining to a duke', origin: 'Old French "duc"' },
      'lord': { meaning: 'pertaining to a lord', origin: 'Old English "hlaford"' },
      'abbey': { meaning: 'near an abbey', origin: 'Latin "abbatia"' },
      'church': { meaning: 'near a church', origin: 'Old English "cirice"' },
      'mill': { meaning: 'near a mill', origin: 'Old English "mylen"' },
      'cross': { meaning: 'at a crossroads or cross', origin: 'Old English "cros" from Latin' },
      'fleet': { meaning: 'creek or stream', origin: 'Old English "fleot"' },
      'well': { meaning: 'near a spring or well', origin: 'Old English "wella"' },
      'spring': { meaning: 'near a spring', origin: 'Old English "spring"' },
    };

    // Analyze the street name
    const nameLower = streetName.toLowerCase().trim();
    const words = nameLower.split(/\s+/);
    
    const suggestions: string[] = [];
    let foundElements: Array<{ element: string; info: { origin: string; meaning: string; period?: string } }> = [];

    // Check for suffix patterns
    for (const [pattern, info] of Object.entries(etymologyPatterns)) {
      if (nameLower.endsWith(pattern) || words.includes(pattern)) {
        foundElements.push({ element: pattern, info });
      }
    }

    // Check for prefix patterns
    for (const [pattern, info] of Object.entries(prefixPatterns)) {
      if (nameLower.startsWith(pattern) || words.includes(pattern)) {
        foundElements.push({ element: pattern, info: { ...info, period: 'Various' } });
      }
    }

    // Build etymology suggestion
    if (foundElements.length > 0) {
      // Remove duplicates
      foundElements = foundElements.filter((v, i, a) => 
        a.findIndex(t => t.element === v.element) === i
      );

      const mainSuggestion = foundElements.map(el => 
        `"${el.element.charAt(0).toUpperCase() + el.element.slice(1)}" derives from ${el.info.origin}, meaning "${el.info.meaning}"${el.info.period ? ` (${el.info.period})` : ''}.`
      ).join(' ');

      suggestions.push(mainSuggestion);

      // Add historical context
      const periods = foundElements.map(el => el.info.period).filter(Boolean);
      if (periods.length > 0) {
        const uniquePeriods = [...new Set(periods)];
        suggestions.push(`This street name contains elements from: ${uniquePeriods.join(', ')}.`);
      }
    } else {
      // Generic suggestion for unrecognized names
      suggestions.push(`"${streetName}" may be named after a person, local landmark, or historical event. Common patterns include: landowner surnames, nearby geographic features, or commemorative naming after notable figures.`);
      suggestions.push('Further research in local historical records, such as tithe maps, census records, or local history archives, may reveal the specific origin of this name.');
    }

    // Add research suggestions
    suggestions.push('For definitive etymology, consult: local county archives, Ordnance Survey historical maps, and publications by the English Place-Name Society or relevant regional societies.');

    const etymologySuggestion = suggestions.join('\n\n');

    return new Response(JSON.stringify({
      data: {
        streetName,
        etymology: etymologySuggestion,
        elements: foundElements,
        confidence: foundElements.length > 0 ? 'medium' : 'low',
        sources: [
          'English Place-Name Society publications',
          'Oxford Dictionary of English Place-Names',
          'Institute of Name-Studies, University of Nottingham'
        ]
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Etymology suggestion error:', error);

    return new Response(JSON.stringify({
      error: {
        code: 'ETYMOLOGY_ERROR',
        message: error.message
      }
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
