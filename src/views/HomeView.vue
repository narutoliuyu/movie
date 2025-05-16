<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
import CategoryList from '../components/CategoryList.vue';
import MovieCarousel from '../components/MovieCarousel.vue';
import MovieCard from '../components/MovieCard.vue';
import { getApiUrl, API_PATHS, API_CONFIG } from '../api/config';
import { useRouter } from 'vue-router';

const movies = ref([]);
const filteredMovies = ref([]);
const loading = ref(true);
const error = ref(null);
const activeCategory = ref(null);
const sectionTitle = ref('全部电影');
const categories = ref([]);
const isHomePage = ref(true);
const router = useRouter();

// 获取分类数据
const fetchCategories = async () => {
  try {
    const response = await axios.get(getApiUrl(API_PATHS.CATEGORIES), API_CONFIG);
    if (response.data && response.data.status === 'success') {
      categories.value = response.data.data;
      console.log('获取到的分类数据:', categories.value);
    } else {
      throw new Error(response.data.message || '获取分类数据失败');
    }
  } catch (err) {
    console.error('获取分类数据错误:', err);
    error.value = err.message || '获取分类数据失败';
  }
};

// 监听分类变化
watch(activeCategory, (newCategory) => {
  if (newCategory) {
    filterMoviesByCategory(newCategory);
  }
});

// 监听movies变化
watch(movies, (newMovies) => {
  console.log('movies 发生变化:', newMovies);
  console.log('movies 长度:', newMovies.length);
}, { deep: true });

// 监听 loading 变化
watch(loading, (newLoading) => {
  console.log('loading 状态变化:', newLoading);
});

// 监听 error 变化
watch(error, (newError) => {
  console.log('error 状态变化:', newError);
});

// 获取所有电影
const fetchMovies = async () => {
  try {
    loading.value = true;
    error.value = null;
    const response = await axios.get(getApiUrl(API_PATHS.MOVIES.ALL), API_CONFIG);
    if (response.data && Array.isArray(response.data.data)) {
      movies.value = response.data.data;
    } else if (response.data && Array.isArray(response.data.movies)) {
      movies.value = response.data.movies;
    } else if (Array.isArray(response.data)) {
      movies.value = response.data;
    }
    // 初始化筛选后的电影列表
    filteredMovies.value = [...movies.value];
  } catch (err) {
    console.error('获取电影数据错误:', err);
    error.value = err.response?.data?.message || '获取电影数据失败';
  } finally {
    loading.value = false;
  }
};

// 根据分类获取电影
const fetchMoviesByCategory = async (categoryId) => {
  try {
    loading.value = true;
    error.value = null;
    console.log('开始获取分类电影:', categoryId);
    console.log('当前分类列表:', categories.value);
    const selectedCategory = categories.value.find(cat => cat.id === categoryId);
    console.log('选中的分类:', selectedCategory);
    
    const response = await axios.get(getApiUrl(API_PATHS.MOVIES.BY_CATEGORY(categoryId)), API_CONFIG);
    console.log('获取分类电影响应:', response.data);
    
    if (response.data.status === 'success') {
      movies.value = response.data.data;
      console.log('更新电影列表:', movies.value);
      console.log('电影类型统计:', movies.value.reduce((acc, movie) => {
        acc[movie.movie_type] = (acc[movie.movie_type] || 0) + 1;
        return acc;
      }, {}));
    } else {
      throw new Error(response.data.message || '获取电影失败');
    }
  } catch (err) {
    console.error('获取分类电影错误:', err);
    error.value = err.message || '获取电影失败';
  } finally {
    loading.value = false;
  }
};

// 根据分类筛选电影
const filterMoviesByCategory = (categoryId) => {
  if (categoryId === null) {
    // 显示所有电影
    filteredMovies.value = [...movies.value];
  } else {
    // 筛选特定分类的电影
    filteredMovies.value = movies.value.filter(movie => movie.category_id === categoryId);
  }
};

// 处理分类点击事件
const handleCategoryChange = async (categoryId) => {
  console.log('分类切换:', categoryId);
  activeCategory.value = categoryId;
  if (categoryId === null) {
    isHomePage.value = true;
    await fetchMovies();
  } else {
    isHomePage.value = false;
    await fetchMoviesByCategory(categoryId);
  }
};

// 添加跳转方法
const goToMovieDetail = (movieId) => {
  router.push({
    name: 'movie-detail',
    params: { id: movieId }
  });
};

onMounted(() => {
  console.log('HomeView 组件挂载');
  console.log('初始 movies 值:', movies.value);
  console.log('初始 loading 值:', loading.value);
  console.log('初始 error 值:', error.value);
  
  // 先获取分类数据
  fetchCategories();
  
  // 获取所有电影
  fetchMovies();
});
</script>

<template>
  <div class="home-layout">
    <!-- 导航栏 -->
    <NavBar />
    
    <!-- 主要内容区 -->
    <div class="content-area">
      <!-- 左侧分类 -->
      <aside class="sidebar">
        <CategoryList 
          :categories="categories"
          :active-category="activeCategory"
          @category-change="handleCategoryChange" 
        />
      </aside>
      
      <!-- 右侧内容区 -->
      <div class="main-content">
        <!-- 轮播图 - 只在全部电影时显示 -->
        <div v-if="isHomePage" class="carousel-section">
          <MovieCarousel />
        </div>
        
        <!-- 电影列表 -->
        <div class="movies-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="error" class="error-state">
            <p>{{ error }}</p>
            <button class="retry-button" @click="handleCategoryChange(activeCategory)">重试</button>
          </div>
          
          <!-- 空状态 -->
          <div v-else-if="movies.length === 0" class="empty-state">
            <p>暂无电影数据</p>
            <button class="retry-button" @click="handleCategoryChange(activeCategory)">刷新</button>
          </div>
          
          <!-- 电影列表 -->
          <div v-else class="movies-grid">
            <MovieCard
              v-for="movie in movies"
              :key="movie.id"
              :movie="movie"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-layout {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #0c0e22;
  overflow: hidden;
}

.content-area {
  display: flex;
  width: 100%;
  height: calc(100vh - 70px);
  margin-top: 70px;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  height: 100%;
  flex-shrink: 0;
  background-color: #111431;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
  z-index: 10;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  background: linear-gradient(135deg, #0e102a 0%, #0c0e22 100%);
  scrollbar-width: thin;
  scrollbar-color: #e94560 #171a31;
}

.main-content::-webkit-scrollbar {
  width: 6px;
}

.main-content::-webkit-scrollbar-track {
  background: #171a31;
}

.main-content::-webkit-scrollbar-thumb {
  background: #e94560;
  border-radius: 10px;
}

.carousel-section {
  width: 90%;
  height: 800px;
  margin: 0 auto 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movies-section {
  padding: 20px;
  width: 100%;
  position: relative;
}

.movies-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 5%;
  width: 90%;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(233, 69, 96, 0.3), transparent);
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
  padding: 30px 10px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: #e94560;
  animation: spin 1s cubic-bezier(0.17, 0.67, 0.83, 0.67) infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: #e94560;
}

.retry-button {
  margin-top: 15px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
}

.retry-button:hover {
  background: linear-gradient(135deg, #e94560, #aa2a49);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(233, 69, 96, 0.5);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: white;
}

.empty-state p {
  margin-bottom: 15px;
  font-size: 16px;
  color: #b9bad3;
}

/* 移除这些样式，因为它们与 MovieCard 组件中定义的冲突 */
.movie-card,
.movie-card:hover,
.poster-container,
.movie-poster,
.movie-card:hover .movie-poster,
.movie-rating,
.movie-info,
.movie-title,
.movie-director {
  all: unset;
}

.debug-info {
  background: rgba(255, 255, 255, 0.05);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #b9bad3;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

.debug-info p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
