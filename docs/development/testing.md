# Testing Strategy — Streets Past

## 1. Current State

No test framework is currently installed. The only automated quality checks in the project are:

- **Type checking**: `tsc -b` runs as part of `pnpm build` and `pnpm build:prod`. TypeScript strict mode is off (`strict: false` in `tsconfig.app.json`), so type errors that would be caught in strict mode are not reported.
- **Linting**: `pnpm lint` runs ESLint with the `react-hooks` and `react-refresh` plugins. This catches hook rule violations and fast-refresh compatibility issues, but not logic errors or runtime failures.

There are no unit tests, component tests, integration tests, or end-to-end tests. The build pipeline does not run any test suite before deployment.

This is acceptable for an early-stage project but creates risk as the codebase grows — particularly around the Supabase integration, authentication logic, and the search debouncing behaviour, which are not exercised by type checking alone.

---

## 2. Recommended Test Framework

### Vitest

[Vitest](https://vitest.dev/) is the recommended unit and component test framework because it:

- Integrates natively with the existing Vite 6 configuration, reusing the same transform pipeline and path aliases
- Is significantly faster than Jest for Vite projects (no separate Babel/Jest transform step)
- Uses a Jest-compatible API, so documentation and patterns are transferable
- Supports jsdom for browser-like DOM simulation
- Works with `@testing-library/react` without any additional adapters

### Installation

Run from `street-etymology/`:

```bash
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

Add the test script to `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage"
  }
}
```

For coverage reporting, also install:

```bash
pnpm add -D @vitest/coverage-v8
```

---

## 3. Unit Tests

Unit tests cover pure logic — functions and hooks that do not depend on the DOM or external services.

### What to test

**Utility functions and type guards**

Any helper functions extracted into `src/lib/` or `src/utils/` should have full unit coverage. Examples of logic worth extracting and testing:

- Coordinate display formatting (e.g., converting `51.5074` to `"51.5074° N"`)
- Date formatting for `created_at` timestamps from Supabase (using `date-fns`)
- Etymology text truncation logic (truncating long `etymology_suggestion` strings to a display-safe length)
- Street name normalisation for search (lowercasing, trimming, removing special characters)

**Auth context role checks**

The `isAdmin` derived value in `AuthContext.tsx` is currently computed as:

```ts
const isAdmin = profile?.role === 'admin' || profile?.role === 'moderator';
```

Unit tests should verify that `isAdmin` is:
- `true` when `profile.role` is `"admin"`
- `true` when `profile.role` is `"moderator"`
- `false` when `profile.role` is `"user"`
- `false` when `profile` is `null`

**Search debounce behaviour**

The `SearchBar` component fires a Supabase query 300ms after the last keystroke. The debounce timing and cancellation logic can be tested by mocking `setTimeout`/`clearTimeout` with Vitest's fake timers.

**Contribution form validation**

The `ContributionForm` component validates:
- `etymology` field is non-empty before submission
- When the user is not authenticated, `email` field is required

These validation paths can be tested independently of the DOM using unit tests against the validation logic if it is extracted into a helper function.

---

## 4. Component Tests

Component tests use React Testing Library to render components in a jsdom environment and assert on user-visible output and interactions. They sit between unit tests and full end-to-end tests — they exercise component logic, state transitions, and rendering, but with external dependencies (Supabase, react-router) mocked.

### SearchBar

File: `src/components/__tests__/SearchBar.test.tsx`

Tests to write:

- **Renders with default placeholder**: The input element renders with the text `"Search UK street names..."`.
- **Renders with custom placeholder**: When `placeholder="Find a street"` is passed as a prop, the input displays that text.
- **Large variant applies correct CSS class**: When `large={true}`, the input has the larger padding class (`py-5`).
- **Does not query when fewer than 2 characters are typed**: Typing a single character does not trigger the Supabase mock.
- **Shows loading indicator**: After typing 2+ characters and before the debounce timeout resolves, the `Loader2` spinner is visible.
- **Shows results dropdown**: After the debounce fires and the mocked Supabase query returns results, a dropdown list of street names is displayed.
- **Shows verified badge**: When a result has `etymology_verified: true`, a "Verified" badge appears.
- **Shows empty state**: When the query returns no results, the "No streets found" message is displayed.
- **Clears input on X button click**: Clicking the clear button resets the input to empty and hides the dropdown.
- **Calls onSelect when provided**: When a result is clicked and `onSelect` is provided as a prop, it is called with the selected `Street` object.
- **Navigates to street detail when no onSelect**: When a result is clicked without an `onSelect` prop, the router navigates to `/street/:id`.
- **Closes dropdown on outside click**: Clicking outside the component hides the dropdown.

### ContributionForm

File: `src/components/__tests__/ContributionForm.test.tsx`

Tests to write:

- **Renders etymology textarea and submit button**: Basic render check.
- **Shows email field for unauthenticated users**: When `useAuth` returns `{ user: null }`, the email input is rendered.
- **Hides email field for authenticated users**: When `useAuth` returns a user object, the email input is not rendered.
- **Shows validation error when etymology is empty**: Submitting with an empty etymology field calls `toast.error` with the correct message and does not call the Supabase mock.
- **Shows validation error when email is missing for unauthenticated users**: Submitting without an email when unauthenticated triggers the email error.
- **Shows loading state during submission**: After clicking submit with valid data, the button shows "Submitting..." and the `Loader2` spinner.
- **Shows success state after submission**: After the mocked Supabase insert resolves successfully, the `CheckCircle` success view is rendered with the street name in the message.
- **Shows error toast on Supabase failure**: When the mocked insert returns an error, `toast.error` is called with the retry message.
- **Reset form allows another submission**: Clicking "Submit another contribution" from the success state returns to the form.
- **Calls onSuccess callback**: When the submission succeeds and `onSuccess` is provided, it is called.

### Header

File: `src/components/__tests__/Header.test.tsx`

Tests to write:

- **Renders logo and site title**: The "Street Etymology" heading and `MapPin` logo are visible.
- **Shows Sign In and Register links when unauthenticated**: When `useAuth` returns `{ user: null, isAdmin: false }`, the "Sign In" and "Register" links are present.
- **Does not show Profile or Sign Out when unauthenticated**: The "Profile" and "Sign Out" elements are not present.
- **Shows Profile and Sign Out links when authenticated**: When `useAuth` returns a user object, the "Profile" and "Sign Out" links are rendered.
- **Does not show Admin link for regular user**: When `isAdmin` is `false`, no "Admin" link is rendered.
- **Shows Admin link for admin/moderator**: When `isAdmin` is `true`, the "Admin" link with the `Shield` icon is rendered.
- **Sign Out calls signOut function**: Clicking the "Sign Out" button calls the `signOut` mock.
- **Mobile menu opens on hamburger click**: Clicking the mobile menu button renders the mobile navigation.
- **Active route receives active styling**: When the current location is `/search`, the "Search Streets" link has the `bg-amber-100` active class.

### AdminPage

File: `src/pages/__tests__/AdminPage.test.tsx`

Tests to write:

- **Redirects non-admin users to homepage**: When `useAuth` returns `{ isAdmin: false, loading: false }`, `navigate('/')` is called and the toast error is shown.
- **Shows loading state while auth is resolving**: When `useAuth` returns `{ isAdmin: false, loading: true }`, the page does not immediately redirect.
- **Renders moderation dashboard for admin users**: When `useAuth` returns `{ isAdmin: true, loading: false }`, the contributions list area is rendered.
- **Filters contributions by status**: Clicking the "Pending", "Approved", "Rejected", and "All" filter buttons updates the Supabase query filter parameter.
- **Shows empty state when no contributions match filter**: When the Supabase mock returns an empty array, an appropriate empty state message is rendered.

---

## 5. Integration Tests

Integration tests exercise multiple layers together — typically a page component with real routing context but mocked Supabase responses. These tests verify that data fetching, state management, and rendering work together correctly.

### Mocking the Supabase client

Mock the entire `@supabase/supabase-js` module at the test level:

```ts
// src/test/mocks/supabase.ts
import { vi } from 'vitest';

export const mockSupabaseFrom = vi.fn();
export const mockSupabaseAuth = {
  getUser: vi.fn().mockResolvedValue({ data: { user: null }, error: null }),
  onAuthStateChange: vi.fn().mockReturnValue({
    data: { subscription: { unsubscribe: vi.fn() } },
  }),
  signInWithPassword: vi.fn(),
  signUp: vi.fn(),
  signOut: vi.fn(),
};

vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    from: mockSupabaseFrom,
    auth: mockSupabaseAuth,
  })),
}));
```

Each `mockSupabaseFrom` call returns a chainable query builder mock. A helper to construct this:

```ts
export function mockQueryChain(resolvedValue: { data: unknown; error: unknown }) {
  const chain = {
    select: vi.fn().mockReturnThis(),
    ilike: vi.fn().mockReturnThis(),
    eq: vi.fn().mockReturnThis(),
    order: vi.fn().mockReturnThis(),
    limit: vi.fn().mockReturnThis(),
    maybeSingle: vi.fn().mockResolvedValue(resolvedValue),
    insert: vi.fn().mockResolvedValue(resolvedValue),
    update: vi.fn().mockReturnThis(),
  };
  mockSupabaseFrom.mockReturnValue(chain);
  return chain;
}
```

### StreetDetailPage data loading

Tests to write:

- **Loads and displays street data**: When the route parameter is a valid street ID and the Supabase mock returns a street record, the street name, location, and etymology suggestion are rendered.
- **Shows loading spinner during fetch**: Before the mock resolves, a loading indicator is visible.
- **Shows not found state for unknown street**: When the mock returns `{ data: null, error: null }`, a "Street not found" message is rendered.
- **Displays verified badge on verified streets**: When `etymology_verified: true` in the mock data, the verified indicator is shown.
- **Displays contribution form for authenticated users**: When the user is logged in, the `ContributionForm` is rendered in the page.

### Contribution submission and approval workflow

Tests to write:

- **Pending contribution appears in admin queue**: Submit a contribution via `ContributionForm` mock, then verify the admin page query includes `status: 'pending'` in the filter.
- **Approving a contribution updates status**: Clicking approve in `AdminPage` calls the Supabase update mock with `{ status: 'approved' }` for the correct contribution ID.
- **Rejecting a contribution updates status**: Clicking reject calls the Supabase update mock with `{ status: 'rejected' }`.

---

## 6. End-to-End Tests

E2E tests run against the full built application in a real browser. They are slower than unit or component tests and are best reserved for critical user journeys and flows that span multiple pages.

### Playwright

Install the Playwright test runner:

```bash
pnpm add -D @playwright/test
npx playwright install chromium
```

Create `playwright.config.ts` in `street-etymology/`:

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
  },
  webServer: {
    command: 'pnpm dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
});
```

Place E2E test files in `street-etymology/e2e/`.

### Journeys to cover

**Navigation: Homepage to street detail and back**

```
1. Navigate to /
2. Assert the hero section and SearchBar are visible
3. Type "Abbey" into the search bar
4. Wait for the dropdown to appear
5. Click the first result
6. Assert the URL is /street/:id and the street name heading is visible
7. Click the browser back button
8. Assert the URL is / and the homepage is rendered
```

**Auth flow: Register, login, profile, logout**

```
1. Navigate to /register
2. Fill in email, password, and full name
3. Submit the form
4. Assert a success message or redirect (email confirmation flow may intercept)
5. Navigate to /login
6. Fill in credentials and submit
7. Assert the Header shows the Profile and Sign Out links
8. Navigate to /profile
9. Assert the user's email is displayed
10. Click Sign Out
11. Assert the Header reverts to showing Sign In and Register
```

**Map: Loads, shows markers, popup on click**

```
1. Navigate to /map
2. Assert the MapLibre canvas element is present
3. Wait for the map tiles to load (no 404s in network)
4. Assert at least one map marker is visible on the canvas (screenshot or aria check)
5. Click a marker
6. Assert a popup appears with a street name
```

**Contribution: Submit form, appears in admin queue**

```
1. Log in as an admin user (seeded test credentials)
2. Navigate to a street detail page
3. Fill in the ContributionForm with valid etymology text
4. Submit the form
5. Assert the success state is shown
6. Navigate to /admin
7. Assert the contribution appears in the pending queue with the submitted text
```

---

## 7. MapLibre GL JS Testing

MapLibre GL JS requires a WebGL context, which jsdom does not provide. This requires special handling depending on the test type.

### In unit and component tests (Vitest + jsdom)

Mock the entire `maplibre-gl` module to prevent WebGL initialisation errors:

```ts
// src/test/mocks/maplibre-gl.ts
import { vi } from 'vitest';

const mockMap = {
  on: vi.fn().mockReturnThis(),
  off: vi.fn(),
  remove: vi.fn(),
  addSource: vi.fn(),
  addLayer: vi.fn(),
  removeSource: vi.fn(),
  removeLayer: vi.fn(),
  getSource: vi.fn(),
  flyTo: vi.fn(),
  fitBounds: vi.fn(),
  getCanvas: vi.fn().mockReturnValue({ style: {} }),
  loaded: vi.fn().mockReturnValue(true),
};

vi.mock('maplibre-gl', () => ({
  default: {
    Map: vi.fn().mockImplementation(() => mockMap),
    Marker: vi.fn().mockImplementation(() => ({
      setLngLat: vi.fn().mockReturnThis(),
      setPopup: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
    })),
    Popup: vi.fn().mockImplementation(() => ({
      setHTML: vi.fn().mockReturnThis(),
    })),
    NavigationControl: vi.fn(),
  },
}));
```

With this mock in place, `MapView` can be rendered in jsdom and the following can be tested:

- The map container `div` is rendered with the correct class and `ref` target
- `maplibregl.Map` constructor is called with the expected `center`, `zoom`, and `bounds` options
- When `streets` prop changes, `addSource` or `addLayer` is called on the mock map
- When a marker is clicked, the mock popup is created and the `flyTo` mock is called

### Snapshot testing for marker styles

Marker elements are created via DOM string literals in `MapView.tsx`. Extract these into a pure function and snapshot-test the output:

```ts
// Extract from MapView.tsx
export function createMarkerElement(isVerified: boolean): string {
  return `<div class="marker-dot ${isVerified ? 'marker-verified' : ''}" ...></div>`;
}

// Test
it('renders verified marker with correct class', () => {
  expect(createMarkerElement(true)).toMatchSnapshot();
});
```

### In E2E tests (Playwright)

Playwright runs in a real Chromium browser with WebGL support. No mocking is needed. Use `page.locator('canvas')` to assert the map canvas is present, and `page.screenshot()` for visual regression of the initial map state.

---

## 8. CI Integration

Add a GitHub Actions workflow at `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: street-etymology

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v3
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
          cache-dependency-path: street-etymology/pnpm-lock.yaml

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Type check
        run: pnpm exec tsc -b --noEmit

      - name: Unit and component tests
        run: pnpm test:run

      - name: Build
        run: pnpm build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
```

For E2E tests, add a separate job that depends on the build succeeding:

```yaml
  e2e:
    runs-on: ubuntu-latest
    needs: test
    defaults:
      run:
        working-directory: street-etymology
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: pnpm install --frozen-lockfile
      - run: npx playwright install --with-deps chromium
      - name: Run E2E tests
        run: pnpm exec playwright test
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
```

Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` as repository secrets pointing at a dedicated Supabase test project (not the production project).

---

## 9. Vitest Configuration

Create `street-etymology/vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'src/**/__tests__/**/*.{ts,tsx}'],
    exclude: ['e2e/**', 'node_modules/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/components/**', 'src/pages/**', 'src/contexts/**', 'src/lib/**'],
      exclude: ['src/test/**', 'src/vite-env.d.ts'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

Create the global test setup file at `street-etymology/src/test/setup.ts`:

```ts
import '@testing-library/jest-dom';
import { vi, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Clean up the DOM after each test
afterEach(() => {
  cleanup();
});

// Suppress MapLibre GL JS console warnings in test output
vi.spyOn(console, 'warn').mockImplementation((msg) => {
  if (typeof msg === 'string' && msg.includes('maplibre')) return;
  console.warn(msg);
});
```

Note: `globals: true` in the Vitest config means `describe`, `it`, `expect`, `vi`, `beforeEach`, etc. are available globally without explicit imports in test files. If you prefer explicit imports, set `globals: false`.

---

## 10. Test File Conventions

### Location

Two patterns are acceptable. Pick one and be consistent:

**Option A: Co-located test files** (preferred for components)

```
src/
  components/
    SearchBar.tsx
    SearchBar.test.tsx        <- test file next to source
    ContributionForm.tsx
    ContributionForm.test.tsx
  pages/
    AdminPage.tsx
    AdminPage.test.tsx
  contexts/
    AuthContext.tsx
    AuthContext.test.tsx
```

**Option B: Centralised `__tests__` directories**

```
src/
  components/
    SearchBar.tsx
    __tests__/
      SearchBar.test.tsx
  pages/
    AdminPage.tsx
    __tests__/
      AdminPage.test.tsx
```

For this project, **Option A** (co-located) is recommended. It keeps tests easy to discover when editing a component and reduces the chance of test files drifting out of sync with their subject.

### Naming

- Unit and component tests: `*.test.ts` or `*.test.tsx`
- E2E tests: `*.spec.ts` in `street-etymology/e2e/`
- Test utilities and mocks: `src/test/` directory

### Import style

Use the `@/` alias in test files the same way as source files:

```ts
import { SearchBar } from '@/components/SearchBar';
import { mockQueryChain } from '@/test/mocks/supabase';
```

---

## 11. Sample Test File: SearchBar

This is a concrete starting point. Save as `street-etymology/src/components/SearchBar.test.tsx`.

```tsx
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { SearchBar } from './SearchBar';

// --- Supabase mock -----------------------------------------------------------
// The mock must be declared before any module imports that use supabase.
// Vitest hoists vi.mock() calls automatically.

const mockSelect = vi.fn();
const mockIlike = vi.fn();
const mockOrder = vi.fn();
const mockLimit = vi.fn();

vi.mock('../lib/supabase', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: mockSelect.mockReturnThis(),
      ilike: mockIlike.mockReturnThis(),
      order: mockOrder.mockReturnThis(),
      limit: mockLimit,
    })),
  },
}));

// --- react-router-dom mock for useNavigate ----------------------------------
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// --- Helpers -----------------------------------------------------------------

const mockStreets = [
  {
    id: 'uuid-1',
    name: 'Abbey Road',
    city: 'London',
    county: 'Greater London',
    postcode_area: 'NW8',
    etymology_suggestion: 'Named after Westminster Abbey, founded 960 AD.',
    etymology_verified: true,
    latitude: 51.5323,
    longitude: -0.177,
    historical_period: 'medieval',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'uuid-2',
    name: 'Abbey Lane',
    city: 'Sheffield',
    county: 'South Yorkshire',
    postcode_area: 'S11',
    etymology_suggestion: null,
    etymology_verified: false,
    latitude: 53.368,
    longitude: -1.503,
    historical_period: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

function renderSearchBar(props = {}) {
  return render(
    <MemoryRouter>
      <SearchBar {...props} />
    </MemoryRouter>
  );
}

// --- Tests -------------------------------------------------------------------

describe('SearchBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders the input with the default placeholder', () => {
      renderSearchBar();
      expect(
        screen.getByPlaceholderText('Search UK street names...')
      ).toBeInTheDocument();
    });

    it('renders the input with a custom placeholder', () => {
      renderSearchBar({ placeholder: 'Find a street' });
      expect(screen.getByPlaceholderText('Find a street')).toBeInTheDocument();
    });

    it('does not show the clear button when the input is empty', () => {
      renderSearchBar();
      // The X button is only rendered when query is non-empty
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });

  describe('search behaviour', () => {
    it('does not query Supabase when fewer than 2 characters are typed', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'A');
      vi.advanceTimersByTime(400);

      expect(mockLimit).not.toHaveBeenCalled();
    });

    it('queries Supabase after the 300ms debounce when 2+ characters are typed', async () => {
      mockLimit.mockResolvedValue({ data: mockStreets, error: null });

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(mockLimit).toHaveBeenCalledWith(10);
      });
    });

    it('does not fire a query if input is cleared before debounce resolves', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      // Clear before the 300ms timeout fires
      await user.clear(screen.getByRole('textbox'));
      vi.advanceTimersByTime(400);

      expect(mockLimit).not.toHaveBeenCalled();
    });
  });

  describe('results dropdown', () => {
    beforeEach(() => {
      mockLimit.mockResolvedValue({ data: mockStreets, error: null });
    });

    it('shows street names in the dropdown after a successful query', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(screen.getByText('Abbey Road')).toBeInTheDocument();
        expect(screen.getByText('Abbey Lane')).toBeInTheDocument();
      });
    });

    it('shows location text beneath each result', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(screen.getByText('London, Greater London, NW8')).toBeInTheDocument();
      });
    });

    it('shows the Verified badge for streets with etymology_verified true', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(screen.getByText('Verified')).toBeInTheDocument();
      });
    });

    it('shows the result count in the footer of the dropdown', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(screen.getByText('2 results found')).toBeInTheDocument();
      });
    });
  });

  describe('empty state', () => {
    it('shows "No streets found" when query returns no results', async () => {
      mockLimit.mockResolvedValue({ data: [], error: null });

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'xyzzy');
      vi.advanceTimersByTime(300);

      await waitFor(() => {
        expect(screen.getByText('No streets found')).toBeInTheDocument();
      });
    });
  });

  describe('clear button', () => {
    it('shows the clear button when input has text', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'A');

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('clears the input and hides the dropdown on clear button click', async () => {
      mockLimit.mockResolvedValue({ data: mockStreets, error: null });

      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => screen.getByText('Abbey Road'));

      await user.click(screen.getByRole('button'));

      expect(screen.getByRole('textbox')).toHaveValue('');
      expect(screen.queryByText('Abbey Road')).not.toBeInTheDocument();
    });
  });

  describe('selection', () => {
    beforeEach(() => {
      mockLimit.mockResolvedValue({ data: mockStreets, error: null });
    });

    it('calls onSelect with the street object when a result is clicked', async () => {
      const onSelect = vi.fn();
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar({ onSelect });

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => screen.getByText('Abbey Road'));
      await user.click(screen.getByText('Abbey Road'));

      expect(onSelect).toHaveBeenCalledWith(mockStreets[0]);
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('navigates to /street/:id when no onSelect prop is provided', async () => {
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar();

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => screen.getByText('Abbey Road'));
      await user.click(screen.getByText('Abbey Road'));

      expect(mockNavigate).toHaveBeenCalledWith('/street/uuid-1');
    });

    it('clears the input after a selection', async () => {
      const onSelect = vi.fn();
      const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
      renderSearchBar({ onSelect });

      await user.type(screen.getByRole('textbox'), 'Ab');
      vi.advanceTimersByTime(300);

      await waitFor(() => screen.getByText('Abbey Road'));
      await user.click(screen.getByText('Abbey Road'));

      expect(screen.getByRole('textbox')).toHaveValue('');
    });
  });
});
```

---

## Priority Order

Given the project is starting from zero test coverage, implement tests in this order:

1. **Vitest configuration** — `vitest.config.ts` and `src/test/setup.ts` (one-time setup, unlocks everything else)
2. **SearchBar component tests** — highest user-facing risk; debounce logic is not covered by type checking
3. **Header component tests** — auth-conditional rendering is a common source of regressions
4. **ContributionForm component tests** — validation logic and success/error states
5. **AdminPage access control test** — the redirect-on-non-admin check is critical security behaviour
6. **AuthContext unit tests** — the `isAdmin` logic is simple but consequential
7. **StreetDetailPage integration test** — exercises the full data loading flow
8. **E2E Playwright tests** — add after unit/component coverage is stable
