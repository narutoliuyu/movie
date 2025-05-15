<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { getApiUrl, API_PATHS } from '../api/config';

const userInfo = ref({
  username: '',
  email: '',
  created_at: '',
  avatar: ''
});

const loading = ref(true);
const error = ref('');

const fetchUserInfo = async () => {
  try {
    loading.value = true;
    const response = await axios.get(getApiUrl(API_PATHS.AUTH.PROFILE));
    if (response.data.status === 'success') {
      userInfo.value = response.data.data;
    }
  } catch (err) {
    error.value = '获取用户信息失败';
    console.error('获取用户信息失败:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<template>
  <div class="profile">
    <div class="profile-header">
      <h2>个人资料</h2>
    </div>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else class="profile-content">
      <div class="avatar-section">
        <div class="avatar">
          <img :src="userInfo.avatar || '/default-avatar.png'" alt="用户头像" />
        </div>
        <button class="change-avatar">更换头像</button>
      </div>
      
      <div class="info-section">
        <div class="info-item">
          <label>用户名</label>
          <div class="value">{{ userInfo.username }}</div>
        </div>
        
        <div class="info-item">
          <label>邮箱</label>
          <div class="value">{{ userInfo.email }}</div>
        </div>
        
        <div class="info-item">
          <label>注册时间</label>
          <div class="value">{{ userInfo.created_at }}</div>
        </div>
      </div>
      
      <div class="actions">
        <button class="edit-profile">编辑资料</button>
        <button class="change-password">修改密码</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.profile-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
}

.profile-content {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 2rem;
}

.avatar-section {
  text-align: center;
}

.avatar {
  width: 150px;
  height: 150px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #4a90e2;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.change-avatar {
  background: none;
  border: 1px solid #4a90e2;
  color: #4a90e2;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.change-avatar:hover {
  background: #4a90e2;
  color: white;
}

.info-section {
  padding: 1rem;
}

.info-item {
  margin-bottom: 1.5rem;
}

.info-item label {
  display: block;
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-item .value {
  color: #333;
  font-size: 1.1rem;
}

.actions {
  grid-column: 1 / -1;
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.edit-profile {
  background: #4a90e2;
  color: white;
}

.edit-profile:hover {
  background: #357abd;
}

.change-password {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.change-password:hover {
  background: #e9ecef;
}
</style> 