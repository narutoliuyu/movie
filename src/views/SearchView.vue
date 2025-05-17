<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getApiUrl, API_PATHS, CookieUtil, axiosInstance } from '../api/config';
import NavBar from '../components/NavBar.vue';
import backIcon from '../assets/返回.png';

const route = useRoute();
const router = useRouter();
const movies = ref([]);
const loading = ref(false);
const error = ref('');
const totalResults = ref(0);
const searchQuery = ref(route.query.q || '');
const recommendedMovies = ref([]);
const loadingRecommendations = ref(false);

// 先定义fetchMovies函数，解决Cannot access before initialization错误
const fetchMovies = async (query) => {
  try {
    loading.value = true;
    error.value = '';
    console.log('开始搜索电影:', query);
    
    const apiUrl = getApiUrl(API_PATHS.SEARCH.MAIN);
    console.log('API地址:', apiUrl);
    
    const response = await axiosInstance.get(apiUrl, {
      params: { query }
    });
    
    console.log('搜索响应:', response.data);
    
    if (response.data && response.data.status === 'success') {
      movies.value = response.data.data.movies || [];
      totalResults.value = response.data.data.total || 0;
      console.log('获取到电影数据:', movies.value.length);
      
      // 如果搜索结果为空，获取推荐电影
      if (movies.value.length === 0) {
        await fetchRecommendedMovies();
      }
    } else {
      console.error('API响应格式错误:', response.data);
      error.value = '服务器返回数据格式错误';
      movies.value = [];
      await fetchRecommendedMovies();
    }
  } catch (err) {
    error.value = '搜索失败，请稍后重试';
    console.error('搜索失败:', err);
    movies.value = [];
    await fetchRecommendedMovies();
  } finally {
    loading.value = false;
    console.log('搜索完成，loading状态:', loading.value);
  }
};

// 获取推荐电影
const fetchRecommendedMovies = async () => {
  try {
    loadingRecommendations.value = true;
    console.log('获取推荐电影');
    
    // 从API获取推荐电影
    const apiUrl = getApiUrl(API_PATHS.MOVIES.FEATURED);
    console.log('推荐电影API地址:', apiUrl);
    
    const response = await axiosInstance.get(apiUrl, {
      params: { limit: 4, featured: true }
    });
    
    console.log('推荐电影响应:', response.data);
    
    if (response.data && response.data.status === 'success' && response.data.data) {
      recommendedMovies.value = response.data.data || [];
      console.log('获取到推荐电影:', recommendedMovies.value.length);
    } else {
      recommendedMovies.value = [];
      console.log('没有获取到推荐电影');
    }
  } catch (err) {
    console.error('获取推荐电影失败:', err);
    recommendedMovies.value = [];
  } finally {
    loadingRecommendations.value = false;
  }
};

// 监听路由查询参数变化
watch(
  () => route.query.q,
  (newQuery) => {
    if (newQuery) {
      searchQuery.value = newQuery;
      fetchMovies(newQuery);
    }
  },
  { immediate: true }
);

const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <div class="search-view">
    <NavBar />
    
    <div class="search-content">
      <div class="search-header">
        <button class="back-button" @click="goToHome">
          <img :src="backIcon" alt="返回" class="back-icon" />
          <span>返回首页</span>
        </button>
        <h1 class="search-title">搜索结果: <span class="highlight">{{ searchQuery }}</span></h1>
      </div>

      <div class="search-info" v-if="!loading && !error && movies.length > 0">
        <p class="result-count">找到 <span class="highlight-count">{{ totalResults }}</span> 个相关结果</p>
      </div>

      <div v-if="error" class="error">
        <p>{{ error }}</p>
        <button class="retry-button" @click="fetchMovies(searchQuery)">
          重试
        </button>
      </div>

      <div v-else-if="movies.length === 0" class="no-results">
        <div class="no-results-container">
          <div class="no-results-icon">🔍</div>
          <p>未找到 "{{ searchQuery }}" 相关电影</p>
        </div>
        
        <!-- 推荐电影部分 -->
        <div v-if="recommendedMovies.length > 0" class="recommended-section">
          <h2 class="section-title">为您推荐</h2>
          <p class="recommendation-desc">您可能对以下电影感兴趣：</p>
          
          <div class="movie-grid">
            <div 
              v-for="movie in recommendedMovies.slice(0, 4)" 
              :key="movie.id"
              class="movie-card"
              @click="$router.push('/movie/' + movie.id)"
            >
              <div class="poster">
                <img :src="movie.poster_url || 'https://via.placeholder.com/300x450/1a1a2e/ffffff?text=暂无图片'" :alt="movie.title">
                <div class="overlay">
                  <div class="play-button">▶</div>
                </div>
                <div class="rating" v-if="movie.rating">
                  <span class="rating-value">{{ movie.rating }}</span>
                </div>
              </div>
              <div class="info">
                <h3 class="title">{{ movie.title }}</h3>
                <p class="year">{{ movie.release_date }}</p>
                <p class="genres">{{ movie.movie_type }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="movie-grid">
        <div 
          v-for="movie in movies" 
          :key="movie.id"
          class="movie-card"
          @click="$router.push('/movie/' + movie.id)"
        >
          <div class="poster">
            <img :src="movie.poster_url || 'https://via.placeholder.com/300x450/1a1a2e/ffffff?text=暂无图片'" :alt="movie.title">
            <div class="overlay">
              <div class="play-button">▶</div>
            </div>
            <div class="rating" v-if="movie.rating">
              <span class="rating-value">{{ movie.rating }}</span>
            </div>
          </div>
          <div class="info">
            <h3 class="title">{{ movie.title }}</h3>
            <p class="year">{{ movie.release_date }}</p>
            <p class="genres">{{ movie.movie_type }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1129 0%, #13173a 100%);
  color: white;
}

.search-content {
  padding-top: 90px;
  min-height: calc(100vh - 90px);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-bottom: 2rem;
  padding-left: 2rem;
  padding-right: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.search-header {
  width: 100%;
  margin-bottom: 2rem;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.5rem;
}

.search-title {
  font-size: 2.5rem;
  margin: 0;
  text-align: left;
  background: linear-gradient(135deg, #ffffff, #b9bad3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.highlight {
  color: #e94560;
  background: linear-gradient(135deg, #e94560, #ff6b9b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.back-button:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: scale(1.05);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.back-icon {
  width: 20px;
  height: 20px;
}

.search-info {
  width: 100%;
  margin-bottom: 2rem;
  text-align: left;
}

.result-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
  margin-left: 0.5rem;
}

.highlight-count {
  color: #e94560;
  font-weight: 700;
  font-size: 1.3rem;
}

.loading, .error, .no-results {
  text-align: left;
  padding: 2rem 0;
  color: #b9bad3;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.5rem;
  width: 100%;
}

.loading-container, .no-results-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 1rem 0;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(233, 69, 96, 0.2);
  border-top: 4px solid #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-results-icon {
  font-size: 3.5rem;
  opacity: 0.6;
  margin-bottom: 0.5rem;
}

.retry-button {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.retry-button:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: scale(1.05);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(214px, 1fr));
  gap: 25px;
  width: 100%;
  padding: 0;
}

.movie-card {
  background: linear-gradient(145deg, #13173a, #171c49);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.4s ease;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  position: relative;
  height: 100%;
}

.movie-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
}

.poster {
  position: relative;
  padding-top: 150%;
  overflow: hidden;
}

.poster img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.movie-card:hover .poster img {
  transform: scale(1.1);
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0) 60%);
  opacity: 0;
  transition: opacity 0.4s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.movie-card:hover .overlay {
  opacity: 1;
}

.play-button {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #e94560, #c23758);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 1.5rem;
  transform: scale(0.8);
  transition: transform 0.4s ease;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.5);
}

.movie-card:hover .play-button {
  transform: scale(1);
}

.rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  padding: 0.4rem 0.7rem;
  border-radius: 8px;
  font-weight: bold;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(233, 69, 96, 0.5);
  z-index: 2;
}

.info {
  padding: 1.2rem;
  background: linear-gradient(to top, #13173a, rgba(19, 23, 58, 0.9));
}

.title {
  margin: 0 0 0.8rem;
  font-size: 1.1rem;
  color: white;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.year, .genres {
  margin: 0.4rem 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .search-content {
    padding: 80px 1rem 2rem 1rem;
  }

  .search-header {
    padding: 1.5rem 0;
  }
  
  .search-title {
    font-size: 1.8rem;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }

  .section-title {
    font-size: 1.5rem;
  }
  
  .recommendation-desc {
    font-size: 1rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .search-content {
    padding: 90px 1.5rem 2rem 1.5rem;
  }
  
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 20px;
  }
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(233, 69, 96, 0.5);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(233, 69, 96, 0.7);
}

/* 推荐电影样式 */
.recommended-section {
  width: 100%;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 1.5rem;
  margin: 0 0 0.3rem;
  color: #e94560;
  text-align: left;
}

.recommendation-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin-bottom: 1rem;
  text-align: left;
}
</style>
