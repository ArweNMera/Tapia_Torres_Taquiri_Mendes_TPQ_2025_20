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
import { SettingsScreen } from './components/screens/SettingsScreen';
import { AuthProvider, useAuth } from './contexts/AuthContext';

type AppState = 'onboarding' | 'login' | 'register' | 'main';
type ActiveTab = 'home' | 'meal-plan' | 'scan' | 'risk-prediction' | 'progress' | 'community' | 'gamification' | 'profile' | 'settings';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const [appState, setAppState] = useState<AppState>('onboarding');
  const [activeTab, setActiveTab] = useState<ActiveTab>('home');
  const [hasSeenOnboarding, setHasSeenOnboarding] = useState(false);

  // Verificar si el usuario ya vio el onboarding
  useEffect(() => {
    const seenOnboarding = localStorage.getItem('hasSeenOnboarding');
    setHasSeenOnboarding(!!seenOnboarding);
  }, []);

  // Manejar el estado de la aplicación basado en la autenticación
  useEffect(() => {
    if (isLoading) return;

    if (isAuthenticated) {
      setAppState('main');
    } else if (hasSeenOnboarding) {
      setAppState('login');
    } else {
      setAppState('onboarding');
    }
  }, [isAuthenticated, hasSeenOnboarding, isLoading]);

  const handleOnboardingComplete = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    setHasSeenOnboarding(true);
    setAppState('login');
  };

  const handleLogin = () => {
    setAppState('main');
  };

  const handleShowRegister = () => {
    setAppState('register');
  };

  const handleRegister = () => {
    setAppState('main');
  };

  const handleBackToLogin = () => {
    setAppState('login');
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab as ActiveTab);
  };

  const handleRecipeClick = (recipeId: string) => {
    console.log('Recipe clicked:', recipeId);
    // Here you would navigate to recipe details
  };

  // Mostrar loading mientras se verifica la autenticación
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

  // Onboarding Screen
  if (appState === 'onboarding') {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }

  // Login Screen
  if (appState === 'login') {
    return (
      <LoginScreen 
        onLogin={handleLogin}
        onSignUp={handleShowRegister}
      />
    );
  }

  // Register Screen
  if (appState === 'register') {
    return (
      <RegisterScreen 
        onRegister={handleRegister}
        onBackToLogin={handleBackToLogin}
      />
    );
  }

  // Main App with Navigation
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
        {activeTab === 'profile' && (
          <ProfileScreen />
        )}
        {activeTab === 'settings' && (
          <SettingsScreen />
        )}
      </Layout>
      
      {/* ChatBot flotante disponible en todas las pantallas principales */}
      <ChatBot />
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}