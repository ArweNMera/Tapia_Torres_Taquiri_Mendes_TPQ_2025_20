import { useState } from 'react';
import { MessageCircle, Heart, Share2, Bookmark, Filter, Search, Plus, Users, Star, TrendingUp } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Avatar } from '../ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { motion } from 'motion/react';

interface Post {
  id: string;
  author: {
    name: string;
    avatar: string;
    role: 'parent' | 'nutritionist' | 'expert';
    verified: boolean;
  };
  title: string;
  content: string;
  image?: string;
  category: string;
  tags: string[];
  timestamp: string;
  likes: number;
  comments: number;
  shares: number;
  isLiked: boolean;
  isBookmarked: boolean;
}

interface Expert {
  id: string;
  name: string;
  avatar: string;
  specialty: string;
  rating: number;
  consultations: number;
  isOnline: boolean;
}

const posts: Post[] = [
  {
    id: '1',
    author: {
      name: 'Dra. Carmen López',
      avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=100',
      role: 'nutritionist',
      verified: true
    },
    title: '5 Tips para que los niños coman más verduras',
    content: 'Como nutricionista pediatra, he visto que la presentación es clave. Aquí comparto mis estrategias más efectivas para hacer las verduras más atractivas...',
    image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
    category: 'Tips Profesionales',
    tags: ['verduras', 'niños', 'alimentación'],
    timestamp: 'hace 2 horas',
    likes: 24,
    comments: 8,
    shares: 5,
    isLiked: false,
    isBookmarked: true
  },
  {
    id: '2',
    author: {
      name: 'María González',
      avatar: 'https://images.unsplash.com/photo-1544725176-7c40e5a71c5e?w=100',
      role: 'parent',
      verified: false
    },
    title: '¿Cómo manejo las alergias alimentarias de mi hijo?',
    content: 'Mi hijo de 3 años es alérgico a los frutos secos y lácteos. ¿Alguna mamá con experiencia similar que pueda compartir recetas y consejos?',
    category: 'Consultas',
    tags: ['alergias', 'lácteos', 'consejos'],
    timestamp: 'hace 4 horas',
    likes: 12,
    comments: 15,
    shares: 2,
    isLiked: true,
    isBookmarked: false
  },
  {
    id: '3',
    author: {
      name: 'Chef Ana Ruiz',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100',
      role: 'expert',
      verified: true
    },
    title: 'Receta: Nuggets de pollo caseros y saludables',
    content: 'Perfectos para los pequeños de la casa. Sin conservantes ni aditivos artificiales. ¡A mis gemelos les encantan!',
    image: 'https://images.unsplash.com/photo-1562967914-608f82629710?w=400',
    category: 'Recetas',
    tags: ['recetas', 'pollo', 'niños', 'saludable'],
    timestamp: 'hace 1 día',
    likes: 45,
    comments: 12,
    shares: 18,
    isLiked: true,
    isBookmarked: true
  }
];

const experts: Expert[] = [
  {
    id: '1',
    name: 'Dra. Carmen López',
    avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=100',
    specialty: 'Nutrición Pediatra',
    rating: 4.9,
    consultations: 150,
    isOnline: true
  },
  {
    id: '2',
    name: 'Dr. Roberto Silva',
    avatar: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=100',
    specialty: 'Gastroenterología Infantil',
    rating: 4.8,
    consultations: 98,
    isOnline: false
  },
  {
    id: '3',
    name: 'Lic. Sofia Mendez',
    avatar: 'https://images.unsplash.com/photo-1594824156275-d6324f34bb9c?w=100',
    specialty: 'Dietista Clínica',
    rating: 4.7,
    consultations: 75,
    isOnline: true
  }
];

const categories = ['Todos', 'Tips Profesionales', 'Recetas', 'Consultas', 'Experiencias', 'Estudios'];
const sortOptions = ['Más recientes', 'Más populares', 'Más comentados'];

export function CommunityScreen() {
  const [activeTab, setActiveTab] = useState<'feed' | 'experts' | 'my-posts'>('feed');
  const [selectedCategory, setSelectedCategory] = useState('Todos');
  const [sortBy, setSortBy] = useState('Más recientes');
  const [searchQuery, setSearchQuery] = useState('');
  const [postsData, setPostsData] = useState(posts);

  const handleLike = (postId: string) => {
    setPostsData(prev => prev.map(post => 
      post.id === postId 
        ? { 
            ...post, 
            isLiked: !post.isLiked, 
            likes: post.isLiked ? post.likes - 1 : post.likes + 1 
          }
        : post
    ));
  };

  const handleBookmark = (postId: string) => {
    setPostsData(prev => prev.map(post => 
      post.id === postId 
        ? { ...post, isBookmarked: !post.isBookmarked }
        : post
    ));
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'nutritionist': return 'bg-primary text-white';
      case 'expert': return 'bg-secondary text-white';
      case 'parent': return 'bg-accent text-accent-foreground';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'nutritionist': return 'Nutricionista';
      case 'expert': return 'Especialista';
      case 'parent': return 'Padre/Madre';
      default: return 'Usuario';
    }
  };

  const renderPost = (post: Post) => (
    <motion.div
      key={post.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6"
    >
      <Card className="p-6 hover:shadow-md transition-shadow">
        {/* Header del post */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Avatar className="w-12 h-12">
              <img src={post.author.avatar} alt={post.author.name} />
            </Avatar>
            <div>
              <div className="flex items-center space-x-2">
                <h4 className="font-semibold">{post.author.name}</h4>
                {post.author.verified && (
                  <div className="w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-2 mt-1">
                <Badge className={`text-xs px-2 py-1 ${getRoleColor(post.author.role)}`}>
                  {getRoleLabel(post.author.role)}
                </Badge>
                <span className="text-sm text-muted-foreground">{post.timestamp}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              {post.category}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleBookmark(post.id)}
              className={post.isBookmarked ? 'text-warning' : 'text-muted-foreground'}
            >
              <Bookmark size={16} fill={post.isBookmarked ? 'currentColor' : 'none'} />
            </Button>
          </div>
        </div>

        {/* Contenido del post */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg mb-2">{post.title}</h3>
          <p className="text-muted-foreground mb-3">{post.content}</p>
          
          {post.image && (
            <div className="rounded-lg overflow-hidden bg-muted h-48 mb-3">
              <img 
                src={post.image} 
                alt="Post content"
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {post.tags.map((tag, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                #{tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Acciones del post */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleLike(post.id)}
              className={`flex items-center space-x-2 ${post.isLiked ? 'text-destructive' : 'text-muted-foreground'}`}
            >
              <Heart size={16} fill={post.isLiked ? 'currentColor' : 'none'} />
              <span>{post.likes}</span>
            </Button>
            
            <Button variant="ghost" size="sm" className="flex items-center space-x-2 text-muted-foreground">
              <MessageCircle size={16} />
              <span>{post.comments}</span>
            </Button>
            
            <Button variant="ghost" size="sm" className="flex items-center space-x-2 text-muted-foreground">
              <Share2 size={16} />
              <span>{post.shares}</span>
            </Button>
          </div>
          
          <Button variant="outline" size="sm">
            Ver completo
          </Button>
        </div>
      </Card>
    </motion.div>
  );

  const renderExperts = () => (
    <div className="space-y-6">
      {/* Header de expertos */}
      <Card className="p-6 bg-gradient-to-r from-primary/5 to-secondary/5">
        <div className="flex items-center space-x-3 mb-4">
          <Users className="text-primary" size={24} />
          <h3 className="text-lg font-semibold">Consulta con Especialistas</h3>
        </div>
        <p className="text-muted-foreground mb-4">
          Conecta con nutricionistas y especialistas en alimentación infantil
        </p>
        <Button className="bg-primary hover:bg-primary-dark">
          <Plus size={16} className="mr-2" />
          Solicitar Consulta
        </Button>
      </Card>

      {/* Lista de expertos */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {experts.map((expert) => (
          <Card key={expert.id} className="p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start space-x-4">
              <div className="relative">
                <Avatar className="w-16 h-16">
                  <img src={expert.avatar} alt={expert.name} />
                </Avatar>
                {expert.isOnline && (
                  <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-success rounded-full border-2 border-white"></div>
                )}
              </div>
              
              <div className="flex-1">
                <h4 className="font-semibold mb-1">{expert.name}</h4>
                <p className="text-sm text-muted-foreground mb-2">{expert.specialty}</p>
                
                <div className="flex items-center space-x-4 mb-3">
                  <div className="flex items-center space-x-1">
                    <Star size={14} className="text-yellow-500" fill="currentColor" />
                    <span className="text-sm font-medium">{expert.rating}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {expert.consultations} consultas
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <Button size="sm" className="flex-1" disabled={!expert.isOnline}>
                    {expert.isOnline ? 'Consultar Ahora' : 'No Disponible'}
                  </Button>
                  <Button variant="outline" size="sm">
                    Ver Perfil
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderMyPosts = () => (
    <div className="space-y-6">
      <Card className="p-6 border-dashed border-2 border-muted-foreground/30">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
            <Plus size={24} className="text-primary" />
          </div>
          <div>
            <h3 className="font-semibold mb-2">Comparte tu Experiencia</h3>
            <p className="text-muted-foreground text-sm">
              Ayuda a otras familias compartiendo tus tips, recetas o dudas
            </p>
          </div>
          <Button className="bg-primary hover:bg-primary-dark">
            Crear Publicación
          </Button>
        </div>
      </Card>

      <div className="text-center py-12">
        <p className="text-muted-foreground">No tienes publicaciones aún</p>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Comunidad NutriFamily</h1>
        <p className="text-muted-foreground mt-1">
          Conecta, aprende y comparte con otras familias
        </p>
      </div>

      {/* Tabs de navegación */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="feed" className="flex items-center space-x-2">
            <TrendingUp size={16} />
            <span>Feed</span>
          </TabsTrigger>
          <TabsTrigger value="experts" className="flex items-center space-x-2">
            <Users size={16} />
            <span>Especialistas</span>
          </TabsTrigger>
          <TabsTrigger value="my-posts" className="flex items-center space-x-2">
            <MessageCircle size={16} />
            <span>Mis Posts</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="feed">
          {/* Filtros y búsqueda */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar en la comunidad..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex space-x-2">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sortOptions.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Posts */}
          <div>
            {postsData
              .filter(post => selectedCategory === 'Todos' || post.category === selectedCategory)
              .filter(post => 
                searchQuery === '' || 
                post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                post.content.toLowerCase().includes(searchQuery.toLowerCase())
              )
              .map(renderPost)}
          </div>
        </TabsContent>

        <TabsContent value="experts">
          {renderExperts()}
        </TabsContent>

        <TabsContent value="my-posts">
          {renderMyPosts()}
        </TabsContent>
      </Tabs>
    </div>
  );
}