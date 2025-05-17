<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';
import NavBar from '../components/NavBar.vue';
import backIcon from '../assets/返回.png';

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
  const token = CookieUtil.getCookie('token');
  if (token) {
    try {
      const response = await axios.get(getApiUrl('/api/user/profile'), {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.status === 'success') {
        isLoggedIn.value = true;
        userId.value = response.data.data.id || CookieUtil.getCookie('userId');
      }
    } catch (error) {
      CookieUtil.deleteCookie('token');
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
    const token = CookieUtil.getCookie('token');
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
    const token = CookieUtil.getCookie('token');
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
    const token = CookieUtil.getCookie('token');
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

// 清空搜索历史
const clearAllHistory = async () => {
  if (!isLoggedIn.value || !userId.value) return;
  
  try {
    const token = CookieUtil.getCookie('token');
    await axios.delete(getApiUrl(`${API_PATHS.SEARCH.HISTORY}/clear`), {
      headers: { Authorization: `Bearer ${token}` },
      params: { user_id: userId.value }
    }).catch(() => {
      // 如果后端API不存在，单独删除每条记录
      const deletePromises = searchHistory.value.map(history => 
        deleteSearchHistory(history.id)
      );
      return Promise.all(deletePromises);
    });
    
    searchHistory.value = [];
  } catch (error) {
    console.error('清空搜索历史失败:', error);
  }
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
                <button class="clear-history" @click="clearAllHistory">清空</button>
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
        <h2>搜索结果: <span>{{ searchQuery }}</span></h2>
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
        <div class="no-results-icon">🔍</div>
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
  background: #0f1129;
  color: white;
}

.search-content {
  padding-top: 90px;
  min-height: calc(100vh - 90px);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 2rem;
}

.search-header {
  width: 100%;
  max-width: 1200px;
  margin-bottom: 2rem;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 2rem;
  background: #13173a;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
  white-space: nowrap;
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
  background: linear-gradient(135deg, #e94560, #a92e48);
}

.back-icon {
  width: 20px;
  height: 20px;
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
  padding: 0.85rem 1.2rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-input:focus {
  outline: none;
  border-color: #e94560;
  box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2), inset 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.08);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-button {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.85rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.search-button:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.search-info {
  width: 100%;
  max-width: 1200px;
  margin-bottom: 2rem;
  text-align: center;
  padding: 0 2rem;
}

.search-info h2 {
  margin: 0;
  font-size: 1.8rem;
  background: linear-gradient(135deg, #ffffff, #b9bad3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.search-info h2 span {
  color: #e94560;
  background: linear-gradient(135deg, #e94560, #ff6b9b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

.result-count {
  margin: 0.5rem 0 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.95rem;
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
  width: 50px;
  height: 50px;
  border: 4px solid rgba(233, 69, 96, 0.3);
  border-top: 4px solid #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error, .no-results {
  text-align: center;
  padding: 4rem 0;
  color: #b9bad3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

.no-results-icon {
  font-size: 5rem;
  opacity: 0.6;
  margin-bottom: 1rem;
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
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 2rem;
  padding: 1rem 0;
  width: 100%;
  max-width: 1200px;
  padding: 0 2rem;
}

.movie-card {
  background: linear-gradient(145deg, #13173a, #171c49);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
  position: relative;
  height: 100%;
}

.movie-card:hover {
  transform: translateY(-10px) scale(1.02);
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
  transition: transform 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
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
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
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

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #13173a;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  margin-top: 12px;
  padding: 1rem;
  z-index: 100;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.suggestion-section {
  margin-bottom: 1.2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.section-header h4 {
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.clear-history {
  background: none;
  border: none;
  color: #e94560;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.clear-history:hover {
  background: rgba(233, 69, 96, 0.1);
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.8rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
  margin-bottom: 4px;
}

.suggestion-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.history-icon {
  width: 16px;
  height: 16px;
  margin-right: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.delete-history {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 2px 8px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border-radius: 50%;
  font-size: 0.8rem;
  margin-right: 10px;
  font-weight: 600;
}

.no-data {
  padding: 1.5rem 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .search-content {
    padding: 80px 1rem 2rem 1rem;
  }

  .search-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 1.2rem;
  }

  .search-container {
    flex-direction: column;
  }
  
  .search-button {
    margin-top: 0.5rem;
  }

  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1.2rem;
    padding: 0 0.5rem;
  }
  
  .back-button {
    align-self: flex-start;
  }
  
  .search-info h2 {
    font-size: 1.4rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .search-content {
    padding: 90px 1.5rem 2rem 1.5rem;
  }
  
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
</style>
