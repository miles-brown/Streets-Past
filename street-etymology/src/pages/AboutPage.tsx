import { Link } from 'react-router-dom';
import { NewsletterSignup } from '../components/NewsletterSignup';
import { MapPin, BookOpen, Users, Globe, Database, Github, Mail, ArrowRight, Scroll } from 'lucide-react';

const featureIconWrap = 'flex h-16 w-16 items-center justify-center rounded-2xl bg-accent text-primary mx-auto mb-4';

export function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-accent/40 via-background to-background dark:from-muted/80 dark:via-background dark:to-background">
        <div
          className="pointer-events-none absolute inset-0 bg-[length:28px_28px] bg-grid-fine opacity-[0.35] dark:opacity-25"
          aria-hidden
        />
        <div className="pointer-events-none absolute inset-0 bg-hero-mesh opacity-90 dark:opacity-100" aria-hidden />

        <div className="relative mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 lg:px-8 lg:py-24">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-4 py-2 text-sm text-muted-foreground shadow-paper backdrop-blur-sm dark:bg-card/60 dark:shadow-paper-dark">
            <Scroll className="h-4 w-4 text-primary" />
            <span>About the project</span>
          </div>
          <h1 className="mb-4 font-display text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            About Street Etymology UK
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Uncovering the linguistic heritage embedded in British street names, connecting communities to their
            historical roots through language.
          </p>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="surface-glass rounded-2xl p-8 md:p-12">
            <h2 className="mb-6 font-display text-2xl font-bold text-foreground">Our mission</h2>
            <div className="prose max-w-none">
              <p>
                Street names are living historical documents, encoding centuries of linguistic evolution, cultural
                change, and social history. Every street corner tells a story — from the Old English &apos;gata&apos;
                (road) surviving in northern &apos;gates&apos; to Norman French influences in &apos;close&apos; and
                &apos;court&apos;.
              </p>
              <p>
                Street Etymology UK was founded to make this rich heritage accessible to everyone. Whether you are a
                historian researching local place names, a linguist studying language evolution, or simply curious about
                the street where you live, our database provides comprehensive etymological information.
              </p>
              <p className="mb-0">
                We combine academic research with community knowledge, building the most comprehensive database of UK
                street name origins. Our platform draws on sources ranging from the English Place-Name Society
                publications to local historical societies and community contributions.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-12 text-center font-display text-2xl font-bold text-foreground">What we offer</h2>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="text-center">
              <div className={featureIconWrap}>
                <Database className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Comprehensive database</h3>
              <p className="text-sm text-muted-foreground">
                Thousands of UK street names with verified etymologies, covering major cities and towns across
                England, Scotland, Wales, and Northern Ireland.
              </p>
            </div>

            <div className="text-center">
              <div className={featureIconWrap}>
                <Globe className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Interactive mapping</h3>
              <p className="text-sm text-muted-foreground">
                Explore street etymologies geographically with our interactive map. Discover linguistic patterns across
                regions and trace historical influences.
              </p>
            </div>

            <div className="text-center">
              <div className={featureIconWrap}>
                <Users className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Community contributions</h3>
              <p className="text-sm text-muted-foreground">
                Share your knowledge and help expand our database. Local historians and etymology enthusiasts can
                submit and verify street name origins.
              </p>
            </div>

            <div className="text-center">
              <div className={featureIconWrap}>
                <BookOpen className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Academic sources</h3>
              <p className="text-sm text-muted-foreground">
                All etymologies are backed by academic sources including English Place-Name Society publications,
                Oxford Dictionary of English Place-Names, and more.
              </p>
            </div>

            <div className="text-center">
              <div className={featureIconWrap}>
                <MapPin className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Search &amp; filter</h3>
              <p className="text-sm text-muted-foreground">
                Find streets by name, location, or etymological origin. Filter by county, city, language of origin, or
                historical period.
              </p>
            </div>

            <div className="text-center">
              <div className={featureIconWrap}>
                <Github className="h-8 w-8" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">Open data</h3>
              <p className="text-sm text-muted-foreground">
                Export data for research purposes. We believe in open access to linguistic and historical information
                for the public good.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-8 text-center font-display text-2xl font-bold text-foreground">Our data sources</h2>

          <div className="surface-glass rounded-xl p-8">
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <BookOpen className="mt-1 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <h4 className="font-semibold text-foreground">English Place-Name Society</h4>
                  <p className="text-sm text-muted-foreground">
                    Academic publications on English county place names and etymologies.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <BookOpen className="mt-1 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <h4 className="font-semibold text-foreground">Oxford Dictionary of English Place-Names</h4>
                  <p className="text-sm text-muted-foreground">
                    Authoritative reference work on the etymology of English place names.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <BookOpen className="mt-1 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <h4 className="font-semibold text-foreground">Ordnance Survey Open Data</h4>
                  <p className="text-sm text-muted-foreground">
                    Geographic and street name data from the national mapping agency.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <BookOpen className="mt-1 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <h4 className="font-semibold text-foreground">Local history societies</h4>
                  <p className="text-sm text-muted-foreground">
                    Research and publications from regional historical societies.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <BookOpen className="mt-1 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <h4 className="font-semibold text-foreground">Community contributions</h4>
                  <p className="text-sm text-muted-foreground">
                    Verified submissions from local historians and etymology enthusiasts.
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section className="border-t border-border py-16">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="surface-glass rounded-2xl border border-primary/15 bg-gradient-to-br from-accent/50 to-background p-8 md:p-12 dark:from-accent/20 dark:to-background">
            <div className="mb-8 text-center">
              <h2 className="mb-2 font-display text-2xl font-bold text-foreground">Get involved</h2>
              <p className="text-muted-foreground">Join our community of etymology researchers and local historians.</p>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="surface-glass rounded-xl p-6">
                <Mail className="mb-3 h-8 w-8 text-primary" />
                <h3 className="mb-2 font-semibold text-foreground">Contact us</h3>
                <p className="mb-3 text-sm text-muted-foreground">Have questions or suggestions? We would love to hear from you.</p>
                <a
                  href="mailto:contact@streetetymology.co.uk"
                  className="text-sm font-medium text-primary transition-colors hover:underline"
                >
                  contact@streetetymology.co.uk
                </a>
              </div>

              <div className="surface-glass rounded-xl p-6">
                <Users className="mb-3 h-8 w-8 text-primary" />
                <h3 className="mb-2 font-semibold text-foreground">Contribute</h3>
                <p className="mb-3 text-sm text-muted-foreground">Share your knowledge of local street name histories.</p>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary transition-colors hover:underline"
                >
                  <span>Create an account</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8">
          <NewsletterSignup />
        </div>
      </section>
    </div>
  );
}
