<script setup>
import { ref, onMounted } from 'vue';

// 模拟消息数据
const messages = ref([
  {
    id: 1,
    title: '欢迎使用黑盒影视',
    content: '感谢您注册黑盒影视，希望您能享受我们提供的服务。',
    created_at: '2023-07-01 10:30:00',
    is_read: false
  },
  {
    id: 2,
    title: '系统更新通知',
    content: '我们的系统将于本周五进行维护更新，可能会造成短暂的服务中断，敬请谅解。',
    created_at: '2023-07-15 15:45:00',
    is_read: false
  },
  {
    id: 3,
    title: '新片推荐',
    content: '根据您的观影喜好，我们为您推荐了一批新上线的电影，快去看看吧！',
    created_at: '2023-07-20 09:15:00',
    is_read: true
  }
]);

const loading = ref(false);
const error = ref('');

const markAsRead = (messageId) => {
  const message = messages.value.find(m => m.id === messageId);
  if (message) {
    message.is_read = true;
  }
};

const deleteMessage = (messageId) => {
  if (!confirm('确定要删除这条消息吗？')) {
    return;
  }
  
  messages.value = messages.value.filter(m => m.id !== messageId);
};

</script>

<template>
  <div class="message-center">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button class="retry-btn">重试</button>
    </div>
    
    <div v-else-if="messages.length === 0" class="empty-messages">
      <div class="empty-icon">📬</div>
      <p>暂无消息</p>
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
  width: 100%;
  height: 100%;
  color: white;
}

.loading, .error-message, .empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #b9bad3;
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

.empty-icon {
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.error-message p {
  color: #e94560;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.retry-btn {
  margin-top: 1rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
  font-weight: 500;
}

.retry-btn:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.5), rgba(23, 28, 73, 0.5));
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.message-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.message-item.unread {
  border-left: 4px solid #e94560;
}

.message-content {
  flex: 1;
}

.message-content h3 {
  margin: 0 0 0.8rem;
  color: white;
  font-weight: 600;
}

.content {
  margin: 0.5rem 0;
  color: #b9bad3;
  line-height: 1.5;
}

.time {
  margin: 0.8rem 0 0;
  color: rgba(185, 186, 211, 0.7);
  font-size: 0.85rem;
}

.actions {
  display: flex;
  gap: 0.8rem;
}

.read-button, .delete-button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.read-button {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.read-button:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.delete-button {
  background: rgba(19, 23, 58, 0.5);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.delete-button:hover {
  background: rgba(23, 28, 73, 0.7);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .message-item {
    flex-direction: column;
  }
  
  .actions {
    margin-top: 1rem;
    align-self: flex-end;
  }
}
</style> 