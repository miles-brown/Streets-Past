import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import type { ReactNode } from 'react';

export type ContentBreadcrumb = { label: string; to?: string };

type ContentPageLayoutProps = {
  title: string;
  lastUpdated?: string;
  breadcrumbs: ContentBreadcrumb[];
  children: ReactNode;
};

/**
 * Shared shell for legal / long-form editorial pages: background, max-width, breadcrumb, card, prose.
 */
export function ContentPageLayout({ title, lastUpdated, breadcrumbs, children }: ContentPageLayoutProps) {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <nav className="mb-8" aria-label="Breadcrumb">
          <ol className="flex flex-wrap items-center gap-2 text-sm">
            {breadcrumbs.map((crumb, i) => (
              <li key={`${crumb.label}-${i}`} className="flex items-center gap-2">
                {i > 0 && <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground/60" aria-hidden />}
                {crumb.to ? (
                  <Link to={crumb.to} className="text-muted-foreground transition-colors hover:text-primary">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="font-medium text-foreground">{crumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>

        <div className="surface-glass rounded-2xl p-8 md:p-12">
          <h1 className={`font-display text-3xl font-bold text-foreground ${lastUpdated ? 'mb-2' : 'mb-8'}`}>
            {title}
          </h1>
          {lastUpdated && (
            <p className="mb-8 font-mono text-sm text-muted-foreground">Last updated: {lastUpdated}</p>
          )}

          <div className="prose max-w-none [&>*:first-child]:mt-0">{children}</div>
        </div>
      </div>
    </div>
  );
}
