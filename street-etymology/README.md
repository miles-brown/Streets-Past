# Streets Past - UK Street Name Etymology

A comprehensive web application for exploring the fascinating origins and histories of UK street names. Discover the linguistic, historical, and cultural meanings behind the streets we walk every day.

## 🌟 Features

### Search & Discovery
- **Fast Search**: Instant autocomplete search across UK street names
- **Geographic Filtering**: Filter by county, city, or postal area
- **Verified Etymologies**: Browse streets with historically verified name origins
- **Interactive Results**: Rich search results with etymology previews

### Interactive Mapping
- **UK Street Map**: Explore street locations with interactive markers
- **Geographic Context**: View streets within their regional context
- **Click-to-Explore**: Click markers to view street details and etymologies
- **Responsive Maps**: Optimized for both desktop and mobile devices

### User Contributions
- **Submit Etymologies**: Help expand the database by contributing your knowledge
- **Community Moderation**: Peer-reviewed contribution system
- **User Profiles**: Track your contributions and contribution history
- **Quality Control**: Approved submissions enhance the public database

### AI-Powered Suggestions
- **Etymology Engine**: AI assistance for generating educated etymology suggestions
- **Linguistic Patterns**: Pattern-based analysis for common UK street name elements
- **Educational Content**: Learn about street name formation and linguistic evolution

## 🏗️ Technical Stack

### Frontend
- **React 18** with TypeScript for type-safe development
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling
- **MapLibre GL JS** for interactive, free map visualization

### Backend & Database
- **Supabase** for PostgreSQL database, authentication, and storage
- **PostGIS** extension for spatial queries and geographic data
- **Row Level Security** for secure data access
- **Real-time subscriptions** for live updates

### Development Tools
- **TypeScript** for enhanced developer experience
- **ESLint** for code quality and consistency
- **PostCSS** for CSS processing
- **pnpm** for efficient package management

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Supabase account and project

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/miles-brown/streets-past.git
cd streets-past
```

2. **Install dependencies**
```bash
pnpm install
```

3. **Environment Setup**
Create a `.env.local` file:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. **Database Setup**
The project includes migration files for:
- Street data schema with PostGIS support
- User authentication and profiles
- Contribution tracking and moderation
- Newsletter subscription management

5. **Development Server**
```bash
pnpm dev
```

6. **Build for Production**
```bash
pnpm build
```

## 📊 Database Schema

### Core Tables
- **streets**: Street names, locations, etymologies, and metadata
- **contributions**: User-submitted etymology suggestions
- **profiles**: User account information and roles
- **newsletter_subscribers**: Email subscription management
- **historical_maps**: Historical map image metadata

### Spatial Data
- PostGIS-enabled tables for geographic queries
- Coordinate data for all UK street locations
- Optimized spatial indexes for fast map rendering

## 🎯 Usage

### For Users
1. **Search Streets**: Use the search bar to find specific street names
2. **Browse by Location**: Filter results by county or city
3. **Explore on Map**: Click map markers to learn about street locations
4. **Contribute Knowledge**: Submit etymology suggestions for streets
5. **Create Account**: Register to track your contributions

### For Contributors
1. **Research**: Use historical sources and linguistic knowledge
2. **Submit**: Add etymology suggestions through the contribution form
3. **Verify**: Community moderation ensures quality contributions
4. **Learn**: Discover fascinating street naming patterns and histories

## 📈 Data Sources

### Primary Sources
- **OS OpenNames**: Official UK street name dataset
- **UK Postcodes**: Geographic and administrative data
- **Historic England**: Listed buildings and heritage records
- **Local Council Data**: Municipal and regional street information

### Community Contributions
- User-submitted etymological research
- Historical documentation and references
- Regional linguistic patterns and dialects
- Cultural and social historical context

## 🔧 Configuration

### Map Configuration
The application uses MapLibre GL JS with OpenStreetMap tiles:
- Free, open-source mapping solution
- No API key required for basic usage
- Optimized for UK geographic focus
- Responsive design for all screen sizes

### Database Configuration
Supabase provides:
- PostgreSQL with PostGIS spatial extensions
- Row Level Security for data protection
- Real-time subscriptions for live updates
- Built-in authentication and user management

## 🤝 Contributing

We welcome contributions from historians, linguists, geographers, and enthusiasts!

### How to Contribute
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our coding standards
4. **Test thoroughly** with the development server
5. **Submit a pull request** with detailed description

### Contribution Areas
- Street etymology research and verification
- Frontend features and improvements
- Database optimization and spatial queries
- Documentation and user guides
- Testing and quality assurance

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ordnance Survey** for the OpenNames dataset
- **OpenStreetMap** contributors for mapping data
- **Supabase** for the backend infrastructure
- **MapLibre GL JS** for open-source mapping
- **UK local historians** who share their knowledge
- **Linguists and etymologists** who preserve language history

## 📞 Support

For questions, suggestions, or issues:
- Create an issue in this repository
- Contact the maintainers through GitHub
- Join our community discussions

---

**Discover the stories behind every street name. Explore the rich tapestry of UK history, one street at a time.**

*Built with ❤️ for history enthusiasts, researchers, and anyone curious about the places they live and visit.*