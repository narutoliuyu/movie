<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { getApiUrl } from '../api/config';

const messages = ref([]);
const loading = ref(true);
const error = ref('');

const fetchMessages = async () => {
  try {
    loading.value = true;
    const response = await axios.get(getApiUrl('/api/user/messages'));
    if (response.data.status === 'success') {
      messages.value = response.data.data;
    }
  } catch (err) {
    error.value = '获取消息失败';
    console.error('获取消息失败:', err);
  } finally {
    loading.value = false;
  }
};

const markAsRead = async (messageId) => {
  try {
    const response = await axios.put(getApiUrl(`/api/user/messages/${messageId}/read`));
    if (response.data.status === 'success') {
      const message = messages.value.find(m => m.id === messageId);
      if (message) {
        message.is_read = true;
      }
    }
  } catch (err) {
    error.value = '标记消息已读失败';
    console.error('标记消息已读失败:', err);
  }
};

const deleteMessage = async (messageId) => {
  if (!confirm('确定要删除这条消息吗？')) {
    return;
  }
  
  try {
    const response = await axios.delete(getApiUrl(`/api/user/messages/${messageId}`));
    if (response.data.status === 'success') {
      messages.value = messages.value.filter(m => m.id !== messageId);
    }
  } catch (err) {
    error.value = '删除消息失败';
    console.error('删除消息失败:', err);
  }
};

onMounted(() => {
  fetchMessages();
});
</script>

<template>
  <div class="message-center">
    <div class="header">
      <h2>消息中心</h2>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="messages.length === 0" class="empty">
      暂无消息
    </div>
    
    <div v-else class="message-list">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message-item"
        :class="{ 'unread': !message.is_read }"
      >
        <div class="message-content">
          <h3>{{ message.title }}</h3>
          <p class="content">{{ message.content }}</p>
          <p class="time">{{ message.created_at }}</p>
        </div>
        
        <div class="actions">
          <button 
            v-if="!message.is_read"
            class="read-button"
            @click="markAsRead(message.id)"
          >
            标记已读
          </button>
          <button 
            class="delete-button"
            @click="deleteMessage(message.id)"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-center {
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.loading, .error, .empty {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.message-item.unread {
  border-left: 4px solid #4a90e2;
}

.message-content {
  flex: 1;
}

.message-content h3 {
  margin: 0 0 0.5rem;
  color: #333;
}

.content {
  margin: 0.5rem 0;
  color: #666;
  line-height: 1.5;
}

.time {
  margin: 0;
  color: #999;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.read-button, .delete-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.read-button {
  background: #4a90e2;
  color: white;
}

.read-button:hover {
  background: #357abd;
}

.delete-button {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
}

.delete-button:hover {
  background: #e9ecef;
}
</style> 