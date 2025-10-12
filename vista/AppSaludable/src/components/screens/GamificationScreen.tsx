import { useState } from 'react';
import { Trophy, Star, Target, Calendar, Users, Gift, Zap, Award, TrendingUp, CheckCircle } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { motion, AnimatePresence } from 'motion/react';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: 'nutrition' | 'consistency' | 'learning' | 'social';
  progress: number;
  maxProgress: number;
  isCompleted: boolean;
  points: number;
  unlockedAt?: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly';
  icon: string;
  progress: number;
  maxProgress: number;
  points: number;
  timeLeft: string;
  participants?: number;
}

interface Streak {
  current: number;
  best: number;
  type: string;
  description: string;
  icon: string;
}

const achievements: Achievement[] = [
  {
    id: '1',
    title: 'Primera Semana Completa',
    description: 'Completaste tu primera semana de seguimiento nutricional',
    icon: '🎯',
    category: 'consistency',
    progress: 7,
    maxProgress: 7,
    isCompleted: true,
    points: 100,
    unlockedAt: 'hace 2 días',
    rarity: 'common'
  },
  {
    id: '2',
    title: 'Explorador de Vegetales',
    description: 'Probaste 5 vegetales diferentes esta semana',
    icon: '🥬',
    category: 'nutrition',
    progress: 4,
    maxProgress: 5,
    isCompleted: false,
    points: 150,
    rarity: 'rare'
  },
  {
    id: '3',
    title: 'Maestro de Recetas',
    description: 'Cocinaste 10 recetas de NutriFamily',
    icon: '👨‍🍳',
    category: 'learning',
    progress: 7,
    maxProgress: 10,
    isCompleted: false,
    points: 200,
    rarity: 'epic'
  },
  {
    id: '4',
    title: 'Hidratación Perfecta',
    description: 'Mantuviste una hidratación óptima por 30 días',
    icon: '💧',
    category: 'nutrition',
    progress: 15,
    maxProgress: 30,
    isCompleted: false,
    points: 300,
    rarity: 'legendary'
  }
];

const challenges: Challenge[] = [
  {
    id: '1',
    title: 'Cinco al Día',
    description: 'Come 5 porciones de frutas y verduras hoy',
    type: 'daily',
    icon: '🍎',
    progress: 3,
    maxProgress: 5,
    points: 50,
    timeLeft: '8h 23m'
  },
  {
    id: '2',
    title: 'Semana Equilibrada',
    description: 'Mantén un balance nutricional perfecto por 7 días',
    type: 'weekly',
    icon: '⚖️',
    progress: 4,
    maxProgress: 7,
    points: 200,
    timeLeft: '3 días',
    participants: 1247
  },
  {
    id: '3',
    title: 'Explorador Culinario',
    description: 'Prueba 3 recetas nuevas este mes',
    type: 'monthly',
    icon: '🌍',
    progress: 1,
    maxProgress: 3,
    points: 500,
    timeLeft: '18 días',
    participants: 856
  }
];

const streaks: Streak[] = [
  {
    current: 7,
    best: 12,
    type: 'daily_nutrition',
    description: 'Días seguidos registrando comidas',
    icon: '📝'
  },
  {
    current: 3,
    best: 5,
    type: 'weekly_goals',
    description: 'Semanas alcanzando metas nutricionales',
    icon: '🎯'
  },
  {
    current: 14,
    best: 14,
    type: 'healthy_choices',
    description: 'Días eligiendo opciones saludables',
    icon: '✅'
  }
];

const leaderboard = [
  { rank: 1, name: 'Ana García', points: 2850, avatar: 'https://images.unsplash.com/photo-1544725176-7c40e5a71c5e?w=100', isCurrentUser: false },
  { rank: 2, name: 'Tú', points: 2340, avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100', isCurrentUser: true },
  { rank: 3, name: 'Carlos López', points: 2180, avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=100', isCurrentUser: false },
  { rank: 4, name: 'María Silva', points: 1950, avatar: 'https://images.unsplash.com/photo-1494790108755-2616b2179a5a?w=100', isCurrentUser: false },
  { rank: 5, name: 'Luis Mendez', points: 1780, avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100', isCurrentUser: false }
];

export function GamificationScreen() {
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'challenges' | 'leaderboard'>('overview');
  const [showCelebration, setShowCelebration] = useState(false);

  const userLevel = 8;
  const userPoints = 2340;
  const pointsToNextLevel = 2500;
  const levelProgress = (userPoints / pointsToNextLevel) * 100;

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'bg-gray-500 text-white';
      case 'rare': return 'bg-primary text-white';
      case 'epic': return 'bg-secondary text-white';
      case 'legendary': return 'bg-gradient-to-r from-accent-dark to-warning text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getChallengeTypeColor = (type: string) => {
    switch (type) {
      case 'daily': return 'bg-success text-white';
      case 'weekly': return 'bg-primary text-white';
      case 'monthly': return 'bg-secondary text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1: return 'text-yellow-500';
      case 2: return 'text-gray-400';
      case 3: return 'text-amber-600';
      default: return 'text-muted-foreground';
    }
  };

  const claimChallenge = (challengeId: string) => {
    setShowCelebration(true);
    setTimeout(() => setShowCelebration(false), 3000);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Perfil de usuario y nivel */}
      <Card className="p-6 bg-gradient-to-r from-primary/10 to-secondary/10">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-20 h-20 bg-primary rounded-full flex items-center justify-center">
            <span className="text-white text-2xl font-bold">L{userLevel}</span>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">Nivel {userLevel} - Nutricionista Aprendiz</h2>
            <p className="text-muted-foreground">{userPoints.toLocaleString()} puntos totales</p>
            <div className="mt-2">
              <div className="flex justify-between text-sm mb-1">
                <span>Progreso al Nivel {userLevel + 1}</span>
                <span>{pointsToNextLevel - userPoints} puntos restantes</span>
              </div>
              <Progress value={levelProgress} className="h-3" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-white/50 rounded-lg">
            <Trophy size={24} className="mx-auto text-yellow-500 mb-1" />
            <p className="text-lg font-bold">{achievements.filter(a => a.isCompleted).length}</p>
            <p className="text-xs text-muted-foreground">Logros</p>
          </div>
          <div className="text-center p-3 bg-white/50 rounded-lg">
            <Target size={24} className="mx-auto text-primary mb-1" />
            <p className="text-lg font-bold">{challenges.length}</p>
            <p className="text-xs text-muted-foreground">Retos Activos</p>
          </div>
          <div className="text-center p-3 bg-white/50 rounded-lg">
            <Zap size={24} className="mx-auto text-success mb-1" />
            <p className="text-lg font-bold">{Math.max(...streaks.map(s => s.current))}</p>
            <p className="text-xs text-muted-foreground">Mejor Racha</p>
          </div>
          <div className="text-center p-3 bg-white/50 rounded-lg">
            <Users size={24} className="mx-auto text-secondary mb-1" />
            <p className="text-lg font-bold">#2</p>
            <p className="text-xs text-muted-foreground">Ranking</p>
          </div>
        </div>
      </Card>

      {/* Rachas actuales */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Zap className="mr-2 text-warning" size={20} />
          Tus Rachas
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {streaks.map((streak, index) => (
            <motion.div
              key={streak.type}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border rounded-lg text-center"
            >
              <div className="text-3xl mb-2">{streak.icon}</div>
              <div className="text-2xl font-bold text-primary mb-1">{streak.current}</div>
              <div className="text-sm text-muted-foreground mb-2">{streak.description}</div>
              <div className="text-xs text-muted-foreground">
                Mejor: {streak.best} días
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Logros recientes */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Award className="mr-2 text-yellow-500" size={20} />
          Logros Recientes
        </h3>

        <div className="space-y-3">
          {achievements.filter(a => a.isCompleted).slice(0, 3).map((achievement) => (
            <div key={achievement.id} className="flex items-center space-x-4 p-3 bg-muted rounded-lg">
              <div className="text-2xl">{achievement.icon}</div>
              <div className="flex-1">
                <h4 className="font-medium">{achievement.title}</h4>
                <p className="text-sm text-muted-foreground">{achievement.description}</p>
              </div>
              <div className="text-right">
                <Badge className={getRarityColor(achievement.rarity)}>
                  +{achievement.points}
                </Badge>
                {achievement.unlockedAt && (
                  <p className="text-xs text-muted-foreground mt-1">{achievement.unlockedAt}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderAchievements = () => (
    <div className="space-y-6">
      {/* Filtros de logros */}
      <div className="flex flex-wrap gap-2">
        {['Todos', 'Nutrición', 'Consistencia', 'Aprendizaje', 'Social'].map((filter) => (
          <Button key={filter} variant="outline" size="sm">
            {filter}
          </Button>
        ))}
      </div>

      {/* Grid de logros */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {achievements.map((achievement) => (
          <motion.div
            key={achievement.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.02 }}
            className={`p-6 border-2 rounded-lg transition-all ${
              achievement.isCompleted
                ? 'border-success bg-success/5 shadow-md'
                : 'border-muted hover:border-primary/30'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{achievement.icon}</div>
              <div className="flex flex-col items-end space-y-2">
                <Badge className={getRarityColor(achievement.rarity)}>
                  {achievement.rarity}
                </Badge>
                {achievement.isCompleted && (
                  <CheckCircle size={20} className="text-success" />
                )}
              </div>
            </div>

            <h3 className="font-semibold text-lg mb-2">{achievement.title}</h3>
            <p className="text-muted-foreground text-sm mb-4">{achievement.description}</p>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progreso</span>
                <span>{achievement.progress}/{achievement.maxProgress}</span>
              </div>
              <Progress
                value={(achievement.progress / achievement.maxProgress) * 100}
                className="h-2"
              />
            </div>

            <div className="flex justify-between items-center mt-4">
              <span className="text-sm font-medium text-primary">+{achievement.points} puntos</span>
              {achievement.isCompleted && achievement.unlockedAt && (
                <span className="text-xs text-muted-foreground">{achievement.unlockedAt}</span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderChallenges = () => (
    <div className="space-y-6">
      {/* Retos activos */}
      <div className="space-y-4">
        {challenges.map((challenge) => (
          <Card key={challenge.id} className="p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div className="text-3xl">{challenge.icon}</div>
                <div>
                  <h3 className="font-semibold text-lg">{challenge.title}</h3>
                  <p className="text-muted-foreground text-sm">{challenge.description}</p>
                  <div className="flex items-center space-x-3 mt-2">
                    <Badge className={getChallengeTypeColor(challenge.type)}>
                      {challenge.type === 'daily' ? 'Diario' :
                       challenge.type === 'weekly' ? 'Semanal' : 'Mensual'}
                    </Badge>
                    {challenge.participants && (
                      <span className="text-xs text-muted-foreground">
                        {challenge.participants.toLocaleString()} participantes
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="text-lg font-bold text-primary">+{challenge.points}</div>
                <div className="text-xs text-muted-foreground">{challenge.timeLeft} restantes</div>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span>Progreso</span>
                <span>{challenge.progress}/{challenge.maxProgress}</span>
              </div>
              <Progress
                value={(challenge.progress / challenge.maxProgress) * 100}
                className="h-3"
              />
            </div>

            {challenge.progress === challenge.maxProgress ? (
              <Button
                className="w-full bg-success hover:bg-success/90"
                onClick={() => claimChallenge(challenge.id)}
              >
                <Gift size={16} className="mr-2" />
                Reclamar Recompensa
              </Button>
            ) : (
              <Button variant="outline" className="w-full">
                Continuar Reto
              </Button>
            )}
          </Card>
        ))}
      </div>
    </div>
  );

  const renderLeaderboard = () => (
    <div className="space-y-6">
      {/* Periodo selector */}
      <div className="flex space-x-2">
        <Button variant="default" size="sm">Esta Semana</Button>
        <Button variant="outline" size="sm">Este Mes</Button>
        <Button variant="outline" size="sm">Todo el Tiempo</Button>
      </div>

      {/* Podio */}
      <Card className="p-6">
        <div className="flex justify-center items-end space-x-4 mb-6">
          {/* Segundo lugar */}
          <div className="text-center">
            <div className="w-16 h-16 rounded-full overflow-hidden mb-2 mx-auto border-4 border-gray-300">
              <img src={leaderboard[1].avatar} alt={leaderboard[1].name} className="w-full h-full object-cover" />
            </div>
            <div className="bg-gray-300 text-white w-12 h-16 flex items-center justify-center rounded-t-lg mx-auto">
              <span className="font-bold">2</span>
            </div>
            <p className="font-medium text-sm mt-2">{leaderboard[1].name}</p>
            <p className="text-xs text-muted-foreground">{leaderboard[1].points} pts</p>
          </div>

          {/* Primer lugar */}
          <div className="text-center">
            <div className="w-20 h-20 rounded-full overflow-hidden mb-2 mx-auto border-4 border-yellow-400">
              <img src={leaderboard[0].avatar} alt={leaderboard[0].name} className="w-full h-full object-cover" />
            </div>
            <div className="bg-yellow-400 text-white w-14 h-20 flex items-center justify-center rounded-t-lg mx-auto">
              <Trophy size={20} />
            </div>
            <p className="font-medium text-sm mt-2">{leaderboard[0].name}</p>
            <p className="text-xs text-muted-foreground">{leaderboard[0].points} pts</p>
          </div>

          {/* Tercer lugar */}
          <div className="text-center">
            <div className="w-16 h-16 rounded-full overflow-hidden mb-2 mx-auto border-4 border-amber-600">
              <img src={leaderboard[2].avatar} alt={leaderboard[2].name} className="w-full h-full object-cover" />
            </div>
            <div className="bg-amber-600 text-white w-12 h-14 flex items-center justify-center rounded-t-lg mx-auto">
              <span className="font-bold">3</span>
            </div>
            <p className="font-medium text-sm mt-2">{leaderboard[2].name}</p>
            <p className="text-xs text-muted-foreground">{leaderboard[2].points} pts</p>
          </div>
        </div>
      </Card>

      {/* Lista completa */}
      <Card className="p-6">
        <h3 className="font-semibold mb-4">Tabla de Posiciones</h3>
        <div className="space-y-3">
          {leaderboard.map((user) => (
            <div
              key={user.rank}
              className={`flex items-center space-x-4 p-3 rounded-lg ${
                user.isCurrentUser ? 'bg-primary/10 border border-primary/20' : 'bg-muted'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${getRankColor(user.rank)}`}>
                {user.rank}
              </div>

              <div className="w-10 h-10 rounded-full overflow-hidden">
                <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
              </div>

              <div className="flex-1">
                <p className={`font-medium ${user.isCurrentUser ? 'text-primary' : ''}`}>
                  {user.name}
                  {user.isCurrentUser && <span className="ml-2 text-xs">(Tú)</span>}
                </p>
              </div>

              <div className="text-right">
                <p className="font-bold">{user.points.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">puntos</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Gamificación</h1>
        <p className="text-muted-foreground mt-1">
          Alcanza tus metas nutricionales y gana recompensas
        </p>
      </div>

      {/* Tabs de navegación */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <TrendingUp size={16} />
            <span className="hidden sm:inline">Resumen</span>
          </TabsTrigger>
          <TabsTrigger value="achievements" className="flex items-center space-x-2">
            <Award size={16} />
            <span className="hidden sm:inline">Logros</span>
          </TabsTrigger>
          <TabsTrigger value="challenges" className="flex items-center space-x-2">
            <Target size={16} />
            <span className="hidden sm:inline">Retos</span>
          </TabsTrigger>
          <TabsTrigger value="leaderboard" className="flex items-center space-x-2">
            <Trophy size={16} />
            <span className="hidden sm:inline">Ranking</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          {renderOverview()}
        </TabsContent>

        <TabsContent value="achievements">
          {renderAchievements()}
        </TabsContent>

        <TabsContent value="challenges">
          {renderChallenges()}
        </TabsContent>

        <TabsContent value="leaderboard">
          {renderLeaderboard()}
        </TabsContent>
      </Tabs>

      {/* Celebración modal */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ y: -50 }}
              animate={{ y: 0 }}
              className="bg-white rounded-lg p-8 text-center max-w-sm mx-4"
            >
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-bold mb-2">¡Reto Completado!</h3>
              <p className="text-muted-foreground mb-4">Has ganado 200 puntos</p>
              <Button onClick={() => setShowCelebration(false)}>
                ¡Genial!
              </Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
