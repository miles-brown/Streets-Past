import { createClient } from '@/utils/supabase/server';

export default async function Page() {
  const supabase = await createClient();

  const { data: streets, error } = await supabase.from('streets').select('id, name, city').limit(10);

  if (error) {
    return (
      <main style={{ padding: '1.5rem', fontFamily: 'system-ui' }}>
        <h1>Streets (sample)</h1>
        <p style={{ color: 'crimson' }}>Could not load streets: {error.message}</p>
      </main>
    );
  }

  return (
    <main style={{ padding: '1.5rem', fontFamily: 'system-ui' }}>
      <h1>Streets (sample)</h1>
      <p>First rows from <code>streets</code> (Supabase server client + refreshed session).</p>
      <ul>
        {streets?.map((row) => (
          <li key={row.id}>
            {row.name}
            {row.city ? ` — ${row.city}` : ''}
          </li>
        ))}
      </ul>
      {(!streets || streets.length === 0) && <p>No rows returned (empty table or RLS).</p>}
    </main>
  );
}
