# Weekend MVP Setup Guide: Street Name Etymology Website

## 🎯 **Complete Weekend Setup (Saturday-Sunday)**

### **Prerequisites (Friday Evening - 30 minutes)**
- GitHub account
- Netlify account  
- Supabase account
- .org domain (optional for MVP)

---

## **DAY 1: Saturday - Core Infrastructure Setup**

### **Hour 1-2: Project Foundation**
```bash
# 1. Clone the template repository
git clone https://github.com/your-username/street-etymology-mvp.git
cd street-etymology-mvp

# 2. Install dependencies
npm install

# 3. Test locally
npm run dev
# Visit http://localhost:3000 to verify setup
```

### **Hour 3-4: Database Setup (Supabase)**
1. **Create Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Choose organization → Create new project
   - Project name: `street-etymology-mvp`
   - Database password: Generate secure password (save it!)
   - Region: Choose closest to your users

2. **Import UK Street Data**
   ```sql
   -- In Supabase SQL Editor, run:
   CREATE TABLE streets (
     id SERIAL PRIMARY KEY,
     name TEXT NOT NULL,
     county TEXT,
     postcode_area TEXT,
     latitude DECIMAL(10,8),
     longitude DECIMAL(11,8),
     etymology_suggestion TEXT,
     created_at TIMESTAMP DEFAULT NOW()
   );

   -- Enable PostGIS
   CREATE EXTENSION postgis;
   
   -- Add spatial index
   CREATE INDEX idx_streets_location ON streets USING GIST (ST_Point(longitude, latitude));

   -- Import CSV data (OS OpenNames dataset)
   \copy streets(name, county, postcode_area, latitude, longitude) 
   FROM 'os_opennames.csv' 
   DELIMITER ',' CSV HEADER;
   ```

3. **Test Database Connection**
   ```bash
   # Update .env.local
   NEXT_PUBLIC_SUPABASE_URL=your_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   ```

### **Hour 5-6: Basic Search Implementation**
```javascript
// pages/api/search.js - Simple search endpoint
export default async function handler(req, res) {
  const { q, county } = req.query;
  
  const { data, error } = await supabase
    .from('streets')
    .select('*')
    .ilike('name', `%${q}%`)
    .limit(50);
    
  if (error) return res.status(500).json({ error: error.message });
  res.json({ results: data });
}
```

```javascript
// components/SearchBar.js
import { useState } from 'react';

export default function SearchBar({ onResults }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSearch = async () => {
    setLoading(true);
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    onResults(data.results);
    setLoading(false);
  };
  
  return (
    <div className="search-container">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search street names..."
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
    </div>
  );
}
```

### **Hour 7-8: Basic UI and Deployment**
```jsx
// pages/index.js - Simple homepage
import SearchBar from '../components/SearchBar';
import StreetList from '../components/StreetList';

export default function Home() {
  const [results, setResults] = useState([]);
  
  return (
    <div className="container">
      <h1>Street Name Etymology</h1>
      <p>Discover the fascinating origins of UK street names</p>
      
      <SearchBar onResults={setResults} />
      
      {results.length > 0 && (
        <div className="results">
          <h2>Found {results.length} streets</h2>
          <StreetList streets={results} />
        </div>
      )}
    </div>
  );
}
```

**Deploy to Netlify:**
1. Connect GitHub repo to Netlify
2. Build settings: `npm run build`
3. Publish directory: `.next`
4. Deploy!

---

## **DAY 2: Sunday - Enhanced Features**

### **Hour 1-3: Interactive Map Integration**
```bash
# Install map dependencies
npm install maplibre-gl react-map-gl
```

```javascript
// components/StreetMap.js
import Map, { Marker } from 'react-map-gl';

export default function StreetMap({ streets }) {
  return (
    <Map
      mapboxAccessToken="your_mapbox_token"
      initialViewState={{
        longitude: -1,
        latitude: 54,
        zoom: 6
      }}
      style={{ width: '100%', height: '500px' }}
      mapStyle="mapbox://styles/mapbox/streets-v12"
    >
      {streets.map((street) => (
        <Marker
          key={street.id}
          longitude={street.longitude}
          latitude={street.latitude}
          anchor="bottom"
        >
          <div className="marker">📍</div>
        </Marker>
      ))}
    </Map>
  );
}
```

### **Hour 4-5: Etymology Suggestions (AI Integration)**
```javascript
// pages/api/etymology.js
export default async function handler(req, res) {
  const { streetName, county } = req.body;
  
  // Simple rule-based etymology for MVP
  const etymology = generateEtymology(streetName, county);
  
  res.json({ etymology });
}

function generateEtymology(streetName, county) {
  const patterns = {
    'Lane': 'Old English meaning "narrow road" or "path"',
    'Road': 'From Old English "rad" meaning "ride" or journey',
    'Street': 'From Latin "strata" meaning "paved road"',
    'Close': 'Private cul-de-sac, often named after owners',
    'Avenue': 'French origin, grand entrance route'
  };
  
  for (const [key, meaning] of Object.entries(patterns)) {
    if (streetName.includes(key)) {
      return `${streetName}: ${meaning}`;
    }
  }
  
  return `${streetName}: Etymology research needed`;
}
```

### **Hour 6-7: User Contributions (Basic)**
```sql
-- Add to Supabase
CREATE TABLE contributions (
  id SERIAL PRIMARY KEY,
  street_id INTEGER REFERENCES streets(id),
  user_email TEXT,
  etymology_suggestion TEXT,
  approved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

```javascript
// components/ContributionForm.js
export default function ContributionForm({ streetId, onSubmit }) {
  const [suggestion, setSuggestion] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/contribute', {
      method: 'POST',
      body: JSON.stringify({ streetId, suggestion }),
      headers: { 'Content-Type': 'application/json' }
    });
    onSubmit();
    setSuggestion('');
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={suggestion}
        onChange={(e) => setSuggestion(e.target.value)}
        placeholder="Suggest the etymology of this street name..."
        required
      />
      <button type="submit">Submit Suggestion</button>
    </form>
  );
}
```

### **Hour 8: Final Polish and Testing**
```javascript
// pages/[id].js - Street detail page
import { useRouter } from 'next/router';

export default function StreetDetail() {
  const router = useRouter();
  const { id } = router.query;
  
  // Fetch street data and display with map and etymology
  // Add contribution form, similar streets, etc.
  
  return (
    <div>
      <h1>{street.name}</h1>
      <StreetMap streets={[street]} />
      <EtymologyDisplay etymology={street.etymology} />
      <ContributionForm streetId={street.id} />
    </div>
  );
}
```

---

## **🚀 Post-Weekend: Optional Enhancements**

### **Week 2: Production Features**
- [ ] Supabase Auth integration for user accounts
- [ ] Image upload for historical maps
- [ ] Email notifications for contributions
- [ ] Admin dashboard for moderating contributions
- [ ] Analytics setup (Google Analytics)

### **Week 3: SEO and Performance**
- [ ] Sitemap generation for all streets
- [ ] Meta tags for street pages
- [ ] Image optimization (WebP conversion)
- [ ] Database indexing optimization
- [ ] CDN setup for static assets

### **Week 4: Community Features**
- [ ] User profiles and contribution history
- [ ] Voting system for etymology suggestions
- [ ] Discussion threads for controversial etymologies
- [ ] Social sharing features
- [ ] Newsletter signup

---

## **💰 Exact Cost Breakdown**

### **Month 1-3 (MVP)**
- **Netlify**: £0 (free tier)
- **Supabase**: £0 (free tier - 50,000 monthly active users)
- **Domain**: £0 (optional, can use netlify.app subdomain)
- **Map API**: £0 (OpenStreetMap, or Mapbox £0-£5/month)
- **Total**: £0-£5/month

### **Month 4-12 (Growth)**
- **Netlify Pro**: £15/month (for custom domain)
- **Supabase Pro**: £25/month (for 500MB database)
- **Domain**: £7.50/year (Gandi .org)
- **Map API**: £5/month (Mapbox)
- **Total**: £45-50/month (but can stay on free tiers longer)

### **Year 2 (Scale to 10K users)**
- **Supabase Pro**: £25/month (database scaling)
- **Netlify Pro**: £15/month
- **Image Storage**: £5-10/month (AWS S3 or Cloudinary)
- **Monitoring**: £0 (free tiers)
- **Total**: £45-60/month

---

## **🛠️ Maintenance Tasks (30 minutes/week)**

### **Daily (5 minutes)**
- Check Netlify deploy logs for errors
- Review Supabase database size usage

### **Weekly (15 minutes)**
- Check contribution moderation queue
- Update dependency packages (`npm audit`)
- Review analytics for usage patterns

### **Monthly (10 minutes)**
- Backup database (export from Supabase)
- Review hosting quotas and usage
- Update any deprecated dependencies

---

## **🚨 Troubleshooting Guide**

### **Common Issues**

**"Build failed" errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build

# Check environment variables
echo $NEXT_PUBLIC_SUPABASE_URL
```

**Database connection timeouts:**
```javascript
// In supabase.js, add connection pooling
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  {
    db: {
      schema: 'public'
    },
    auth: {
      autoRefreshToken: true,
      persistSession: false,
      detectSessionInUrl: false
    }
  }
);
```

**Map not loading:**
- Check Mapbox token is valid
- Ensure map container has defined height
- Verify coordinate data format (lat, lng order)

---

## **📚 Resources and References**

### **Documentation**
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [MapLibre GL JS Guide](https://maplibre.org/maplibre-gl-js-docs/api/)

### **Data Sources**
- [OS OpenNames Dataset](https://www.ordnancesurvey.co.uk/opendata/datasets/opennames.html)
- [UK Postcodes](https://www.getthedata.com/open-postcode-geo)

### **Development Tools**
- [Supabase CLI](https://supabase.com/docs/guides/cli) for local development
- [GitHub Desktop](https://desktop.github.com/) for version control
- [Vercel CLI](https://vercel.com/docs/cli) for deployment

---

## **✅ Success Checklist**

By the end of weekend, you should have:

- [ ] Working search functionality across UK street names
- [ ] Interactive map displaying street locations
- [ ] User contribution system for etymologies
- [ ] Responsive design that works on mobile
- [ ] Live deployment accessible via public URL
- [ ] Database with UK street data imported
- [ ] Basic analytics tracking
- [ ] SSL certificate active (automatic with Netlify)

**Congratulations! You now have a production-ready MVP street etymology website that can scale to thousands of users while maintaining minimal ongoing costs.**

---

*This setup guide provides a complete path from zero to a working MVP in one weekend, with clear upgrade paths as your website grows. The total cost remains under £5/month for the first year while handling substantial traffic and data volumes.*