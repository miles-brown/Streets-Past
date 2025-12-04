import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { Header } from './components/Header';
import { Footer } from './components/Footer';

// Pages
import { HomePage } from './pages/HomePage';
import { SearchPage } from './pages/SearchPage';
import { MapPage } from './pages/MapPage';
import { StreetDetailPage } from './pages/StreetDetailPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminPage } from './pages/AdminPage';
import { AboutPage } from './pages/AboutPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { TermsPage } from './pages/TermsPage';

import './index.css';

// Layout component with header and footer
function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}

// Full-screen layout (no header/footer) for map page
function FullScreenLayout({ children }: { children: React.ReactNode }) {
  return <div className="h-screen">{children}</div>;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#292524',
              color: '#fafaf9',
              borderRadius: '0.75rem',
            },
            success: {
              iconTheme: {
                primary: '#f59e0b',
                secondary: '#fafaf9',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fafaf9',
              },
            },
          }}
        />
        
        <Routes>
          {/* Auth pages (no header/footer) */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Full-screen map page */}
          <Route
            path="/map"
            element={
              <FullScreenLayout>
                <MapPage />
              </FullScreenLayout>
            }
          />
          
          {/* Main pages with header/footer */}
          <Route
            path="/"
            element={
              <MainLayout>
                <HomePage />
              </MainLayout>
            }
          />
          <Route
            path="/search"
            element={
              <MainLayout>
                <SearchPage />
              </MainLayout>
            }
          />
          <Route
            path="/street/:id"
            element={
              <MainLayout>
                <StreetDetailPage />
              </MainLayout>
            }
          />
          <Route
            path="/profile"
            element={
              <MainLayout>
                <ProfilePage />
              </MainLayout>
            }
          />
          <Route
            path="/admin"
            element={
              <MainLayout>
                <AdminPage />
              </MainLayout>
            }
          />
          <Route
            path="/about"
            element={
              <MainLayout>
                <AboutPage />
              </MainLayout>
            }
          />
          <Route
            path="/contribute"
            element={
              <MainLayout>
                <SearchPage />
              </MainLayout>
            }
          />
          <Route
            path="/privacy"
            element={
              <MainLayout>
                <PrivacyPage />
              </MainLayout>
            }
          />
          <Route
            path="/terms"
            element={
              <MainLayout>
                <TermsPage />
              </MainLayout>
            }
          />
          
          {/* Auth callback */}
          <Route
            path="/auth/callback"
            element={
              <MainLayout>
                <HomePage />
              </MainLayout>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
