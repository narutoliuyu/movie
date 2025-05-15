<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { getApiUrl, API_PATHS } from '../api/config';

const watchHistory = ref([]);
const loading = ref(true);
const error = ref('');

const fetchWatchHistory = async () => {
  try {
    loading.value = true;
    const response = await axios.get(getApiUrl('/api/user/watch-history'));
    if (response.data.status === 'success') {
      watchHistory.value = response.data.data;
    }
  } catch (err) {
    error.value = '获取观看历史失败';
    console.error('获取观看历史失败:', err);
  } finally {
    loading.value = false;
  }
};

const clearHistory = async () => {
  if (!confirm('确定要清空观看历史吗？')) {
    return;
  }
  
  try {
    loading.value = true;
    const response = await axios.delete(getApiUrl('/api/user/watch-history'));
    if (response.data.status === 'success') {
      watchHistory.value = [];
    }
  } catch (err) {
    error.value = '清空观看历史失败';
    console.error('清空观看历史失败:', err);
  } finally {
    loading.value = false;
  }
};

const removeFromHistory = async (movieId) => {
  try {
    const response = await axios.delete(getApiUrl(`/api/user/watch-history/${movieId}`));
    if (response.data.status === 'success') {
      watchHistory.value = watchHistory.value.filter(item => item.movie_id !== movieId);
    }
  } catch (err) {
    error.value = '删除记录失败';
    console.error('删除记录失败:', err);
  }
};

onMounted(() => {
  fetchWatchHistory();
});
</script>

<template>
  <div class="history">
    <div class="header">
      <h2>观看历史</h2>
      <button 
        v-if="watchHistory.length > 0"
        class="clear-button"
        @click="clearHistory"
      >
        清空历史
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="watchHistory.length === 0" class="empty">
      暂无观看历史
    </div>
    
    <div v-else class="history-list">
      <div 
        v-for="item in watchHistory" 
        :key="item.id"
        class="history-item"
      >
        <div class="movie-info">
          <img 
            :src="item.movie.poster_url" 
            :alt="item.movie.title"
            class="poster"
          />
          <div class="details">
            <h3>{{ item.movie.title }}</h3>
            <p class="watch-time">观看时间：{{ item.watch_time }}</p>
            <p class="progress">观看进度：{{ item.progress }}%</p>
          </div>
        </div>
        
        <div class="actions">
          <button 
            class="continue-button"
            @click="$router.push(`/movie/${item.movie.id}`)"
          >
            继续观看
          </button>
          <button 
            class="remove-button"
            @click="removeFromHistory(item.movie.id)"
          >
            删除记录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.clear-button {
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #dc3545;
  color: #dc3545;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-button:hover {
  background: #dc3545;
  color: white;
}

.loading, .error, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.movie-info {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.poster {
  width: 100px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.details {
  flex: 1;
}

.details h3 {
  margin: 0 0 0.5rem;
  color: #333;
}

.watch-time, .progress {
  margin: 0.25rem 0;
  color: #666;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 1rem;
}

.continue-button, .remove-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.continue-button {
  background: #4a90e2;
  color: white;
}

.continue-button:hover {
  background: #357abd;
}

.remove-button {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
}

.remove-button:hover {
  background: #e9ecef;
}
</style> 