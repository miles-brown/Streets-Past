import { Link } from 'react-router-dom';
import { MapPin, Mail, BookOpen, Github, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-border bg-muted/40 dark:bg-muted/25">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="col-span-1 md:col-span-2">
            <div className="mb-4 flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/85 text-primary-foreground shadow-sm">
                <MapPin className="h-6 w-6" />
              </div>
              <div>
                <h2 className="font-display text-lg font-bold text-foreground">Street Etymology UK</h2>
                <p className="text-xs text-muted-foreground">Uncovering the stories behind our streets</p>
              </div>
            </div>
            <p className="mb-4 max-w-md text-sm text-muted-foreground">
              Exploring the rich linguistic heritage embedded in British street names. From Roman roads to
              Victorian terraces, discover the etymology that connects us to our past.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-muted-foreground transition-colors hover:text-primary" aria-label="Twitter">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-muted-foreground transition-colors hover:text-primary" aria-label="GitHub">
                <Github className="h-5 w-5" />
              </a>
            </div>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-foreground">Explore</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/search" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  Search Streets
                </Link>
              </li>
              <li>
                <Link to="/map" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  Interactive Map
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  About the Project
                </Link>
              </li>
              <li>
                <Link to="/contribute" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  Contribute
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-foreground">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm text-muted-foreground transition-colors hover:text-primary">
                  Terms of Service
                </Link>
              </li>
              <li>
                <a
                  href="mailto:contact@streetetymology.co.uk"
                  className="flex items-center space-x-1 text-sm text-muted-foreground transition-colors hover:text-primary"
                >
                  <Mail className="h-4 w-4" />
                  <span>Contact</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-border pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
            <p className="text-xs text-muted-foreground">
              2024 Street Etymology UK. Built with data from Ordnance Survey Open Data.
            </p>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <BookOpen className="h-4 w-4" />
              <span>Open source project for etymological research</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
