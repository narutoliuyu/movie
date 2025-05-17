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
const carouselMovies = ref([]);
const gridMovies = ref([]);
const loading = ref(true);
const error = ref(null);
const activeCategory = ref(null);
const sectionTitle = ref('全部电影');
const categories = ref([]);
const isHomePage = ref(true);
const router = useRouter();
const scrollPosition = ref(0); // 记录滚动位置

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
    
    // 分离轮播图电影和网格电影
    splitMovies();
  } catch (err) {
    console.error('获取电影数据错误:', err);
    error.value = err.response?.data?.message || '获取电影数据失败';
  } finally {
    loading.value = false;
  }
};

// 分离轮播图电影和网格电影
const splitMovies = () => {
  if (movies.value.length > 0) {
    // 取前5部电影作为轮播图
    carouselMovies.value = movies.value.slice(0, 5);
    // 剩余电影作为网格展示
    gridMovies.value = movies.value.slice(5);
  } else {
    carouselMovies.value = [];
    gridMovies.value = [];
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
      
      // 分离轮播图电影和网格电影 (分类页面全部以网格展示)
      gridMovies.value = [...movies.value];
      carouselMovies.value = [];
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
  // 保存当前滚动位置到sessionStorage
  sessionStorage.setItem('homeScrollPosition', window.scrollY.toString());
  
  router.push({
    name: 'movie-detail',
    params: { id: movieId }
  });
};

// 根据电影ID查找并滚动到对应位置
const scrollToMovie = (movieId) => {
  if (!movieId) return false;
  
  console.log('尝试定位到电影ID:', movieId);
  
  // 查找电影元素
  const movieElement = document.querySelector(`[data-movie-id="${movieId}"]`);
  console.log('查找结果:', movieElement ? '找到元素' : '未找到元素');
  
  // 调试 - 打印所有电影卡片信息
  const allCards = document.querySelectorAll('.movie-card');
  console.log(`找到 ${allCards.length} 个电影卡片`);
  allCards.forEach((card, index) => {
    console.log(`卡片 ${index}:`, card.getAttribute('data-movie-id'));
  });
  
  if (movieElement) {
    // 使用instant立即滚动无动画
    console.log('开始滚动到目标电影');
    movieElement.scrollIntoView({ 
      behavior: 'instant',
      block: 'center' 
    });
    console.log('滚动完成，定位到电影元素');
    
    // 添加高亮效果
    movieElement.classList.add('highlight-movie');
    console.log('添加高亮效果');
    
    // 3秒后移除高亮
    setTimeout(() => {
      movieElement.classList.remove('highlight-movie');
    }, 3000);
    
    return true;
  }
  
  return false;
};

// 更快的定位尝试，多次尝试但增加延迟间隔
const attemptFastScroll = (movieId, attempts = 0, maxAttempts = 20) => {
  console.log(`尝试定位 (${attempts+1}/${maxAttempts})...`);
  
  if (attempts >= maxAttempts) {
    console.log('达到最大尝试次数，停止定位');
    return;
  }
  
  const success = scrollToMovie(movieId);
  if (!success) {
    // 增加延迟间隔，确保DOM有足够时间渲染
    const delay = Math.min(300 + attempts * 100, 1000); // 延迟从300ms开始，最大不超过1秒
    console.log(`定位失败，${delay}ms后重试`);
    setTimeout(() => attemptFastScroll(movieId, attempts + 1, maxAttempts), delay);
  } else {
    // 成功后清除缓存
    console.log('定位成功，清除缓存');
    sessionStorage.removeItem('lastViewedMovieId');
  }
};

// 监听路由变化
watch(() => router.currentRoute.value.path, (path, oldPath) => {
  console.log(`路由变化: ${oldPath} -> ${path}`);
  
  if (path === '/') {
    // 当进入首页时，立即尝试定位
    const lastViewedMovieId = sessionStorage.getItem('lastViewedMovieId');
    console.log('从sessionStorage读取lastViewedMovieId:', lastViewedMovieId);
    
    if (lastViewedMovieId) {
      console.log('检测到返回首页，准备定位到上次查看的电影:', lastViewedMovieId);
      
      // 由于Vue的响应式渲染，我们需要等待DOM更新后再尝试滚动
      console.log('等待DOM更新后定位');
      setTimeout(() => {
        console.log('DOM应该已更新，开始尝试定位');
        attemptFastScroll(lastViewedMovieId);
      }, 100);
    }
  }
}, { immediate: true });

// 监听电影数据加载完成
watch(gridMovies, (newMovies) => {
  if (newMovies.length > 0) {
    console.log(`电影数据加载完成，共 ${newMovies.length} 部电影`);
    
    // 当电影数据加载完成后，立即尝试定位
    const lastViewedMovieId = sessionStorage.getItem('lastViewedMovieId');
    console.log('gridMovies加载后，从sessionStorage读取lastViewedMovieId:', lastViewedMovieId);
    
    if (lastViewedMovieId) {
      console.log('电影数据加载完成，尝试定位到电影:', lastViewedMovieId);
      setTimeout(() => {
        attemptFastScroll(lastViewedMovieId);
      }, 100);
    }
  }
}, { immediate: true });

onMounted(() => {
  console.log('HomeView 组件挂载');
  console.log('初始 movies 值:', movies.value);
  console.log('初始 loading 值:', loading.value);
  console.log('初始 error 值:', error.value);
  
  // 先获取分类数据
  fetchCategories();
  
  // 获取所有电影
  fetchMovies();
  
  // 检查是否需要定位到特定电影
  const lastViewedMovieId = sessionStorage.getItem('lastViewedMovieId');
  console.log('onMounted: 从sessionStorage读取lastViewedMovieId:', lastViewedMovieId);
  
  // 如果有lastViewedMovieId，但尚未加载电影数据，则保留ID等待数据加载后处理
  if (lastViewedMovieId) {
    console.log('检测到需要定位的电影ID:', lastViewedMovieId);
  }
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
          class="content-visibility-auto"
        />
      </aside>
      
      <!-- 右侧内容区 -->
      <div class="main-content scroll-container">
        <!-- 轮播图 - 只在全部电影时显示 -->
        <div v-if="isHomePage" class="carousel-section content-visibility-auto">
          <MovieCarousel :movies="carouselMovies" class="animation-gpu" />
        </div>
        
        <!-- 电影列表 -->
        <div class="movies-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <div class="skeleton-grid">
              <div class="skeleton-card animation-gpu" v-for="n in 10" :key="n">
                <div class="skeleton-poster"></div>
                <div class="skeleton-info">
                  <div class="skeleton-title"></div>
                  <div class="skeleton-director"></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="error" class="error-state">
            <p>{{ error }}</p>
            <button class="retry-button" @click="handleCategoryChange(activeCategory)">重试</button>
          </div>
          
          <!-- 空状态 -->
          <div v-else-if="gridMovies.length === 0" class="empty-state">
            <p>暂无电影数据</p>
            <button class="retry-button" @click="handleCategoryChange(activeCategory)">刷新</button>
          </div>
          
          <!-- 电影列表 -->
          <div v-else>
            <div class="movies-container">
              <div class="movies-grid">
                <MovieCard
                  v-for="movie in gridMovies"
                  :key="movie.id"
                  :movie="movie"
                  class="animation-gpu"
                />
              </div>
            </div>
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
  background-color: #0c0e22;
  box-shadow: 10px 0 20px -5px rgba(0, 0, 0, 0.3);
  z-index: 10;
  position: relative;
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
  width: 95%;
  max-width: 1200px;
  margin: 20px auto 60px;
  padding: 25px;
  background-color: rgba(15, 17, 41, 0.5);
  border-radius: 16px;
  position: relative;
}

.movies-section::before {
  display: none;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(45deg, #ffffff, #e94560);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  position: relative;
  padding-left: 15px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(to bottom, #e94560, #aa2a49);
  border-radius: 2px;
}

.movies-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 214px);
  gap: 20px;
  padding: 10px 0;
  justify-content: center;
}

/* 响应式布局 */
@media (max-width: 1190px) {
  .movies-grid {
    grid-template-columns: repeat(4, 214px);
  }
}

@media (max-width: 956px) {
  .movies-grid {
    grid-template-columns: repeat(3, 214px);
  }
}

@media (max-width: 722px) {
  .movies-section {
    padding: 20px;
    width: 90%;
  }
  
  .movies-container {
    padding: 0;
  }

  .movies-grid {
    grid-template-columns: repeat(2, 214px);
  }
}

@media (max-width: 500px) {
  .movies-grid {
    grid-template-columns: repeat(1, 214px);
  }
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
  width: 100%;
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

/* 骨架屏效果 */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1400px;
  padding: 30px;
  margin: 0 auto;
}

.skeleton-card {
  width: 100%;
  aspect-ratio: 2/3;
  background: linear-gradient(145deg, #13173a, #0c0e22);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.skeleton-poster {
  flex: 1;
  background: linear-gradient(110deg, #13173a 25%, #1c2150 37%, #13173a 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
}

.skeleton-info {
  height: 80px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.8);
}

.skeleton-title {
  height: 16px;
  margin-bottom: 12px;
  width: 80%;
  background: linear-gradient(110deg, #333755 25%, #444a7a 37%, #333755 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 4px;
}

.skeleton-director {
  height: 12px;
  width: 60%;
  background: linear-gradient(110deg, #333755 25%, #444a7a 37%, #333755 63%);
  background-size: 200% 100%;
  animation: loading-shine 1.5s infinite;
  border-radius: 4px;
}

@keyframes loading-shine {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
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

/* 确保移除所有可能与MovieCard组件样式冲突的样式 */
.movie-card,
.movie-card:hover,
.poster-container,
.movie-poster,
.movie-card:hover .movie-poster,
.movie-rating,
.movie-info,
.movie-title,
.movie-director {
  all: unset !important;
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
