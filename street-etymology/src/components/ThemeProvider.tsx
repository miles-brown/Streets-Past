import { ThemeProvider as NextThemesProvider } from 'next-themes';
import type { ReactNode } from 'react';

const storageKey = 'streets-past-theme';

export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="light" enableSystem storageKey={storageKey}>
      {children}
    </NextThemesProvider>
  );
}
