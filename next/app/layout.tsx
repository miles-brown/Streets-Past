import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Streets Past (Next)',
  description: 'Supabase + Next.js SSR sample',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
