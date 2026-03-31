import {
  SignIn,
  SignUp,
  useAuth,
} from '@clerk/react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import ChatPage from './pages/ChatPage.jsx';

function AuthPage({ mode }) {
  const isSignIn = mode === 'sign-in';

  return (
    <main className="auth-page">
      <section className="auth-card auth-card-standalone">
        {isSignIn ? (
          <SignIn signUpUrl="/sign-up" fallbackRedirectUrl="/" />
        ) : (
          <SignUp signInUrl="/sign-in" fallbackRedirectUrl="/" />
        )}
      </section>
    </main>
  );
}

function ProtectedHome() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return <p className="app-loading">Chargement...</p>;
  }

  if (!isSignedIn) {
    return <Navigate to="/sign-in" replace />;
  }

  return <ChatPage />;
}

function GuestOnly({ children }) {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return <p className="app-loading">Chargement...</p>;
  }

  if (isSignedIn) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ProtectedHome />} />
        <Route
          path="/sign-in"
          element={
            <GuestOnly>
              <AuthPage mode="sign-in" />
            </GuestOnly>
          }
        />
        <Route
          path="/sign-up"
          element={
            <GuestOnly>
              <AuthPage mode="sign-up" />
            </GuestOnly>
          }
        />
        <Route path="/profile" element={<ProtectedHome />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
