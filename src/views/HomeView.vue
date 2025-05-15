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
  background-color: #0f1129;
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
  background-color: #171a31;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
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
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
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
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #e94560;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: #e94560;
}

.retry-button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #e94560;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #d03651;
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
}

.movie-card {
  width: 200px;
  margin: 0 12px 24px;
  background-color: #171a31;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.poster-container {
  position: relative;
  overflow: hidden;
  height: 300px;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.movie-card:hover .movie-poster {
  transform: scale(1.05);
}

.movie-rating {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #e94560;
  color: white;
  padding: 3px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 3px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.movie-info {
  padding: 12px;
  background-color: #171a31;
}

.movie-title {
  font-size: 1rem;
  margin: 0 0 6px;
  color: white;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-director {
  font-size: 0.8rem;
  margin: 0;
  color: #b9bad3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.debug-info {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: white;
}

.debug-info p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
