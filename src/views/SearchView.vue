<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { getApiUrl, API_PATHS } from '../api/config';

const route = useRoute();
const router = useRouter();
const movies = ref([]);
const loading = ref(true);
const error = ref('');
const totalResults = ref(0);
const searchQuery = ref(route.query.q || '');
const showSearchSuggestions = ref(false);
const searchHistory = ref([]);
const movieRankings = ref([]);
const isLoggedIn = ref(false);
const userId = ref(null);

// 在组件挂载时检查登录状态
onMounted(async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const response = await axios.get(getApiUrl('/api/user/profile'), {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.status === 'success') {
        isLoggedIn.value = true;
        userId.value = response.data.data.id || localStorage.getItem('userId');
      }
    } catch (error) {
      localStorage.removeItem('token');
    }
  }
});

const fetchMovies = async (query) => {
  try {
    loading.value = true;
    error.value = '';
    const response = await axios.get(getApiUrl('/api/search'), {
      params: { query }
    });
    
    if (response.data.status === 'success') {
      movies.value = response.data.data.movies;
      totalResults.value = response.data.data.total;
    }
  } catch (err) {
    error.value = '搜索失败，请稍后重试';
    console.error('搜索失败:', err);
  } finally {
    loading.value = false;
  }
};

// 获取搜索历史
const fetchSearchHistory = async () => {
  if (!isLoggedIn.value || !userId.value) return;
  
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(getApiUrl(API_PATHS.SEARCH.HISTORY), {
      headers: { Authorization: `Bearer ${token}` },
      params: { user_id: userId.value }
    });
    
    if (response.data.status === 'success') {
      searchHistory.value = response.data.data;
      console.log('搜索历史:', searchHistory.value);
    }
  } catch (error) {
    console.error('获取搜索历史失败:', error);
  }
};

// 获取电影排行榜
const fetchMovieRankings = async () => {
  try {
    const response = await axios.get(getApiUrl(API_PATHS.SEARCH.RANKINGS));
    
    if (response.data.status === 'success') {
      movieRankings.value = response.data.data;
      console.log('电影排行榜:', movieRankings.value);
    }
  } catch (error) {
    console.error('获取电影排行榜失败:', error);
  }
};

// 添加搜索历史
const addSearchHistory = async (query) => {
  if (!isLoggedIn.value || !userId.value) return;
  
  try {
    const token = localStorage.getItem('token');
    await axios.post(getApiUrl(API_PATHS.SEARCH.HISTORY), {
      user_id: userId.value,
      search_query: query
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (error) {
    console.error('添加搜索历史失败:', error);
  }
};

// 删除搜索历史
const deleteSearchHistory = async (historyId) => {
  try {
    const token = localStorage.getItem('token');
    await axios.delete(getApiUrl(`${API_PATHS.SEARCH.HISTORY}/${historyId}`), {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    // 重新获取搜索历史
    await fetchSearchHistory();
  } catch (error) {
    console.error('删除搜索历史失败:', error);
  }
};

// 处理搜索框焦点
const handleSearchFocus = async () => {
  showSearchSuggestions.value = true;
  await Promise.all([
    isLoggedIn.value ? fetchSearchHistory() : Promise.resolve(),
    fetchMovieRankings()
  ]);
};

// 处理搜索框失焦
const handleSearchBlur = () => {
  setTimeout(() => {
    showSearchSuggestions.value = false;
  }, 200);
};

// 处理搜索建议点击
const handleSuggestionClick = (query) => {
  searchQuery.value = query;
  handleSearch();
};

// 处理电影点击
const handleMovieClick = async (movieId, title) => {
  if (isLoggedIn.value) {
    await addSearchHistory(title);
  }
  router.push(`/movie/${movieId}`);
  showSearchSuggestions.value = false;
};

const goToHome = () => {
  router.push('/');
};

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    if (isLoggedIn.value) {
      await addSearchHistory(searchQuery.value.trim());
    }
    router.push({
      path: '/search',
      query: { q: searchQuery.value.trim() }
    });
    showSearchSuggestions.value = false;
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
</script>

<template>
  <div class="search-view">
    <div class="search-header">
      <button class="back-button" @click="goToHome">
        <i class="back-icon">←</i>
        返回首页
      </button>
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索电影、演员、导演..."
          @keyup.enter="handleSearch"
          @focus="handleSearchFocus"
          @blur="handleSearchBlur"
          class="search-input"
        />
        <button @click="handleSearch" class="search-button">
          搜索
        </button>
        
        <!-- 搜索建议下拉框 -->
        <div v-if="showSearchSuggestions" class="search-suggestions">
          <!-- 搜索历史 -->
          <div v-if="isLoggedIn && searchHistory.length > 0" class="suggestion-section">
            <div class="section-header">
              <h4>搜索历史</h4>
              <button class="clear-history" @click="searchHistory = []">清空</button>
            </div>
            <div 
              v-for="history in searchHistory" 
              :key="history.id"
              class="suggestion-item"
            >
              <div class="suggestion-content" @click="handleSuggestionClick(history.search_query)">
                <span class="history-icon">⟲</span>
                <span>{{ history.search_query }}</span>
              </div>
              <button 
                class="delete-history"
                @click.stop="deleteSearchHistory(history.id)"
              >
                ×
              </button>
            </div>
          </div>
          
          <!-- 电影排行榜 -->
          <div v-if="movieRankings.length > 0" class="suggestion-section">
            <h4>热门电影</h4>
            <div 
              v-for="ranking in movieRankings" 
              :key="ranking.id"
              class="suggestion-item"
              @click="handleMovieClick(ranking.movie_id, ranking.movie.title)"
            >
              <span class="rank-number">{{ ranking.rank }}</span>
              <span>{{ ranking.movie.title }}</span>
            </div>
          </div>

          <!-- 无数据提示 -->
          <div v-if="(!isLoggedIn || searchHistory.length === 0) && movieRankings.length === 0" class="no-data">
            暂无数据
          </div>
        </div>
      </div>
    </div>

    <div class="search-info">
      <h2>搜索结果</h2>
      <p v-if="!loading && !error" class="result-count">
        找到 {{ totalResults }} 个相关结果
      </p>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在搜索...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-button" @click="fetchMovies(searchQuery)">
        重试
      </button>
    </div>

    <div v-else-if="movies.length === 0" class="no-results">
      <p>未找到相关电影</p>
      <button class="back-button" @click="goToHome">
        返回首页
      </button>
    </div>

    <div v-else class="movie-grid">
      <div 
        v-for="movie in movies" 
        :key="movie.id"
        class="movie-card"
        @click="$router.push('/movie/' + movie.id)"
      >
        <div class="poster">
          <img :src="movie.poster_url" :alt="movie.title">
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
</template>

<style scoped>
.search-view {
  padding: 2rem;
  min-height: calc(100vh - 70px);
  background: #1a1a2e;
  color: white;
  margin-top: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.search-header {
  width: 100%;
  max-width: 1200px;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 2rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #e94560;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  white-space: nowrap;
}

.back-button:hover {
  background: #d03651;
  transform: translateY(-2px);
}

.back-icon {
  font-size: 1.2rem;
}

.search-container {
  flex: 1;
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
  position: relative;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #16213e;
  border-radius: 4px;
  background: #16213e;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #e94560;
  box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2);
}

.search-input::placeholder {
  color: #666;
}

.search-button {
  background: #e94560;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-button:hover {
  background: #d03651;
  transform: translateY(-2px);
}

.search-info {
  width: 100%;
  max-width: 1200px;
  margin-bottom: 2rem;
  text-align: center;
}

.search-info h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #e94560;
}

.result-count {
  margin: 0.5rem 0 0;
  color: #888;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  width: 100%;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e94560;
  border-top: 4px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error, .no-results {
  text-align: center;
  padding: 4rem 0;
  color: #888;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.retry-button {
  background: #e94560;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background: #d03651;
  transform: translateY(-2px);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
  padding: 1rem 0;
  width: 100%;
  max-width: 1200px;
}

.movie-card {
  background: #16213e;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: relative;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.movie-card:hover .poster img {
  transform: scale(1.05);
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
  transition: transform 0.3s ease;
}

.rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(233, 69, 96, 0.9);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
  backdrop-filter: blur(4px);
}

.info {
  padding: 1rem;
  background: linear-gradient(to top, #16213e, rgba(22, 33, 62, 0.9));
}

.title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.year, .genres {
  margin: 0.25rem 0;
  color: #888;
  font-size: 0.9rem;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #16213e;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  margin-top: 8px;
  padding: 12px;
  z-index: 1000;
}

.suggestion-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.section-header h4 {
  color: #aaa;
  margin: 0;
  font-size: 0.9rem;
}

.clear-history {
  background: none;
  border: none;
  color: #e94560;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.clear-history:hover {
  background: rgba(233, 69, 96, 0.1);
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.suggestion-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.suggestion-item:hover {
  background: rgba(233, 69, 96, 0.1);
}

.history-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  color: #aaa;
}

.delete-history {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 4px 8px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.3s ease;
}

.suggestion-item:hover .delete-history {
  opacity: 1;
}

.delete-history:hover {
  color: #e94560;
  background: rgba(233, 69, 96, 0.1);
}

.rank-number {
  width: 20px;
  height: 20px;
  background: #e94560;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  margin-right: 8px;
}

.no-data {
  padding: 12px;
  text-align: center;
  color: #aaa;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .search-view {
    padding: 1rem;
  }

  .search-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .search-container {
    flex-direction: column;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
}
</style>
