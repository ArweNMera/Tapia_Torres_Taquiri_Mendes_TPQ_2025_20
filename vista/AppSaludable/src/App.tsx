import { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { ChatBot } from './components/ChatBot';
import { OnboardingScreen } from './components/screens/OnboardingScreen';
import { LoginScreen } from './components/screens/LoginScreen';
import { RegisterScreen } from './components/screens/RegisterScreen';
import { DashboardScreen } from './components/screens/DashboardScreen';
import { MealPlanScreen } from './components/screens/MealPlanScreen';
import { ScanScreen } from './components/screens/ScanScreen';
import { RiskPredictionScreen } from './components/screens/RiskPredictionScreen';
import { ProgressScreen } from './components/screens/ProgressScreen';
import { CommunityScreen } from './components/screens/CommunityScreen';
import { GamificationScreen } from './components/screens/GamificationScreen';
import { ProfileScreen } from './components/screens/ProfileScreen';
import ProfileManagementScreen from './components/screens/ProfileManagementScreen';
import { SettingsScreen } from './components/screens/SettingsScreen';
import SelfAnthropometry from './components/SelfAnthropometry';
import ProfileHubScreen from './components/screens/ProfileHubScreen';
import { AdminUsersPage } from './pages/AdminUsersPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Toaster } from './components/ui/toaster';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsPage from './pages/TermsPage';
import DeleteDataPage from './pages/DeleteDataPage';

type AppState = 'login' | 'register' | 'onboarding' | 'main';
type ActiveTab = 'home' | 'meal-plan' | 'scan' | 'risk-prediction' | 'progress' | 'community' | 'gamification' | 'profile' | 'clinical' | 'admin';

const STATIC_PAGES: Record<string, React.ReactElement> = {
  '/privacy': <PrivacyPolicyPage />,
  '/terms': <TermsPage />,
  '/delete-data': <DeleteDataPage />,
};

const normalizePath = (path: string) => {
  if (!path) {
    return '/';
  }
  const trimmed = path.replace(/\/+$/, '');
  return trimmed === '' ? '/' : trimmed.toLowerCase();
};

function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [appState, setAppState] = useState<AppState>('login');
  const [activeTab, setActiveTab] = useState<ActiveTab>('home');
  const [hasSeenOnboarding, setHasSeenOnboarding] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user) {
      const seenOnboarding = localStorage.getItem(`hasSeenOnboarding_${user.usr_id}`);
      setHasSeenOnboarding(!!seenOnboarding);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    if (isLoading) return;

    if (isAuthenticated) {
      if (hasSeenOnboarding) {
        setAppState('main');
      } else {
        setAppState('onboarding');
      }
    } else {
      if (appState !== 'register') {
        setAppState('login');
      }
    }
  }, [isAuthenticated, hasSeenOnboarding, isLoading]);

  const handleOnboardingComplete = () => {
    if (user) {
      localStorage.setItem(`hasSeenOnboarding_${user.usr_id}`, 'true');
      setHasSeenOnboarding(true);
      setAppState('main');
    }
  };

  const handleLoginSuccess = () => {
  };

  const handleShowRegister = () => {
    setAppState('register');
  };

  const handleRegisterSuccess = () => {
  };

  const handleBackToLogin = () => {
    setAppState('login');
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab as ActiveTab);
  };

  const handleRecipeClick = (recipeId: string) => {
    console.log('Recipe clicked:', recipeId);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-secondary/10 via-accent/5 to-primary/10 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4 mx-auto">
            <span className="text-white font-bold text-lg">NF</span>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (appState === 'register') {
      return (
        <RegisterScreen
          onRegister={handleRegisterSuccess}
          onBackToLogin={handleBackToLogin}
        />
      );
    }

    return (
      <LoginScreen
        onLogin={handleLoginSuccess}
        onSignUp={handleShowRegister}
      />
    );
  }

  if (appState === 'onboarding') {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }

  return (
    <>
      <Layout activeTab={activeTab} onTabChange={handleTabChange}>
        {activeTab === 'home' && (
          <DashboardScreen onRecipeClick={handleRecipeClick} />
        )}
        {activeTab === 'meal-plan' && (
          <MealPlanScreen onRecipeClick={handleRecipeClick} />
        )}
        {activeTab === 'scan' && (
          <ScanScreen />
        )}
        {activeTab === 'risk-prediction' && (
          <RiskPredictionScreen />
        )}
        {activeTab === 'progress' && (
          <ProgressScreen />
        )}
        {activeTab === 'community' && (
          <CommunityScreen />
        )}
        {activeTab === 'gamification' && (
          <GamificationScreen />
        )}
        {activeTab === 'clinical' && (
          <SelfAnthropometry />
        )}
        {activeTab === 'profile' && (
          <ProfileHubScreen />
        )}
        {activeTab === 'admin' && (
          <AdminUsersPage />
        )}
      </Layout>

      <ChatBot />
    </>
  );
}

export default function App() {
  const pathname =
    typeof window !== 'undefined' ? normalizePath(window.location.pathname) : '/';
  const staticPage = STATIC_PAGES[pathname];

  if (staticPage) {
    return staticPage;
  }

  return (
    <AuthProvider>
      <AppContent />
      <Toaster />
    </AuthProvider>
  );
}
