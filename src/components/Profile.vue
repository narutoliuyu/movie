<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import axios from 'axios';
import { getApiUrl, CookieUtil } from '../api/config';

const userStore = useUserStore();
const userInfo = ref({
  username: '',
  email: '',
  created_at: '',
  avatar: ''
});

const loading = ref(true);
const error = ref('');
const fileInput = ref(null);
const showPasswordModal = ref(false);
const showUsernameForm = ref(false);
const newUsername = ref('');
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const usernameError = ref('');
const passwordError = ref('');
const emailVerify = ref('');
const emailVerifyError = ref('');
const passwordStep = ref(1); // 1: 邮箱验证, 2: 密码修改

// 从后端获取用户信息
const fetchUserData = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    // 确保在请求前重新初始化用户状态
    await userStore.initializeState();
    
    console.log('获取用户状态后:', {
      isLoggedIn: userStore.isLoggedIn,
      userId: userStore.userId,
      username: userStore.username
    });
    
    // 检查用户登录状态
    if (!userStore.isLoggedIn || !userStore.userId) {
      console.warn('未登录或用户ID不存在，使用模拟数据');
      
      // 在开发环境中使用模拟数据
      if (import.meta.env.DEV) {
        userInfo.value = {
          username: '测试用户',
          email: 'test@example.com',
          created_at: new Date().toLocaleDateString(),
          avatar: localStorage.getItem('userAvatar') || ''
        };
        loading.value = false;
        return;
      }
      
      error.value = '请先登录后查看个人信息';
      loading.value = false;
      return;
    }

    console.log('尝试获取用户数据，用户ID:', userStore.userId);

    // 先从store中获取基本数据
    userInfo.value.username = userStore.username || '';
    
    // 使用axios实例并确保携带token
    const token = CookieUtil.getCookie('token');
    if (!token) {
      console.error('Token不存在，用户可能需要重新登录');
      
      // 在开发环境中使用模拟数据
      if (import.meta.env.DEV) {
        userInfo.value = {
          username: userStore.username || '测试用户',
          email: 'test@example.com',
          created_at: new Date().toLocaleDateString(),
          avatar: localStorage.getItem('userAvatar') || ''
        };
        loading.value = false;
        return;
      }
      
      error.value = '登录已过期，请重新登录';
      loading.value = false;
      return;
    }
    
    // 尝试多种可能的API路径
    let response;
    let success = false;
    
    try {
      // 优先调用用户资料专用API
      response = await axios.get(getApiUrl('/api/user/profile'), {
        headers: { Authorization: `Bearer ${token}` }
      });
      success = true;
      console.log('通过/api/user/profile获取数据成功');
    } catch (err1) {
      console.log('第一种API路径尝试失败，尝试备选路径');
      
      try {
        // 尝试方式2: /api/users/{id}
        response = await axios.get(getApiUrl(`/api/users/${userStore.userId}`), {
          headers: { Authorization: `Bearer ${token}` }
        });
        success = true;
        console.log('通过/api/users/id获取数据成功');
      } catch (err2) {
        console.log('第二种API路径尝试失败，最后一次尝试');
        
        try {
          // 尝试方式3: /api/users带参数
          response = await axios.get(getApiUrl('/api/users'), {
            headers: { Authorization: `Bearer ${token}` },
            params: { user_id: userStore.userId }
          });
          success = true;
          console.log('通过/api/users?user_id=获取数据成功');
        } catch (err3) {
          console.error('所有API路径尝试失败', err3);
          
          // API请求全部失败时，在开发环境中使用模拟数据
          if (import.meta.env.DEV) {
            console.log('在开发环境中使用模拟数据');
            userInfo.value = {
              username: userStore.username || '测试用户',
              email: 'test@example.com',
              created_at: new Date().toLocaleDateString(),
              avatar: localStorage.getItem('userAvatar') || ''
            };
            loading.value = false;
            return;
          }
          
          error.value = '获取用户信息失败，后端API可能不可用';
        }
      }
    }
    
    // 处理成功获取的数据
    if (success && response && response.data) {
      console.log('获取用户数据成功:', response.data);
      
      // 通用数据结构适配 - 兼容多种后端返回格式
      const userData = response.data.data || response.data.user || response.data;
      
      if (!userData) {
        console.error('返回数据格式异常:', response.data);
        error.value = '返回数据格式不正确';
        return;
      }
      
      // 保存从用户表获取的数据
      userInfo.value = {
        ...userInfo.value,
        ...userData,
        // 确保字段存在，避免undefined
        username: userData.username || userStore.username || '',
        email: userData.email || '',
        // 确保日期格式正确
        created_at: userData.created_at ? new Date(userData.created_at).toLocaleDateString() : ''
      };
      
      // 保存头像URL - 优先使用后端数据，再考虑本地存储
      if (userData.avatar) {
        userInfo.value.avatar = userData.avatar;
        // 同时保存到本地存储以便后续使用
        localStorage.setItem('userAvatar', userData.avatar);
      } else if (!userInfo.value.avatar) {
        userInfo.value.avatar = localStorage.getItem('userAvatar') || '';
      }
      
      // 更新store中的用户名，确保保持一致
      if (userData.username && userData.username !== userStore.username) {
        userStore.username = userData.username;
      }
    }
  } catch (err) {
    console.error('获取用户数据失败', err);
    error.value = '获取用户信息失败，请检查网络连接';
  } finally {
    loading.value = false;
  }
};

const retryFetch = () => {
  fetchUserData();
};

// 处理头像上传
const triggerFileUpload = () => {
  fileInput.value.click();
};

const handleFileChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 验证文件类型
  if (!file.type.match('image.*')) {
    alert('请选择图片文件');
    return;
  }
  
  try {
    loading.value = true;
    
    // 创建本地URL预览
    const fileUrl = URL.createObjectURL(file);
    // 先更新UI显示
    userInfo.value.avatar = fileUrl;
    
    // 保存到本地存储，确保页面刷新后仍能显示
    localStorage.setItem('userAvatar', fileUrl);
    
    // 创建 FormData 对象用于文件上传
    const formData = new FormData();
    formData.append('avatar', file);
    formData.append('user_id', userStore.userId);
    
    const token = CookieUtil.getCookie('token');
    try {
      const response = await axios.post(getApiUrl('/api/user/upload-avatar'), formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.status === 'success') {
        // 如果后端返回了URL，则使用后端返回的URL
        if (response.data.avatar_url) {
          userInfo.value.avatar = response.data.avatar_url;
          localStorage.setItem('userAvatar', response.data.avatar_url);
        }
        alert('头像上传成功');
      }
    } catch (err) {
      console.warn('头像上传到服务器失败，但已保存本地预览', err);
      // 此处不显示错误提示，因为已经保存了本地预览
    }
  } catch (err) {
    console.error('处理头像失败', err);
    alert('处理头像失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 显示修改用户名表单
const showEditUsername = () => {
  newUsername.value = userInfo.value.username;
  showUsernameForm.value = true;
};

// 修改用户名
const updateUsername = async () => {
  if (!newUsername.value || newUsername.value.trim() === '') {
    usernameError.value = '用户名不能为空';
    return;
  }
  
  if (newUsername.value === userInfo.value.username) {
    showUsernameForm.value = false;
    return;
  }
  
  try {
    loading.value = true;
    usernameError.value = '';
    
    const token = CookieUtil.getCookie('token');
    const response = await axios.put(getApiUrl('/api/user/update-username'), {
      user_id: userStore.userId,
      username: newUsername.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (response.data.status === 'success') {
      userInfo.value.username = newUsername.value;
      // 更新store
      userStore.username = newUsername.value;
      alert('用户名修改成功');
      showUsernameForm.value = false;
    } else {
      throw new Error(response.data.message || '修改失败');
    }
  } catch (err) {
    console.error('修改用户名失败', err);
    usernameError.value = '修改用户名失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 取消修改用户名
const cancelUsernameEdit = () => {
  showUsernameForm.value = false;
  usernameError.value = '';
};

// 显示修改密码弹窗
const showChangePassword = () => {
  emailVerify.value = '';
  emailVerifyError.value = '';
  currentPassword.value = '';
  newPassword.value = '';
  confirmPassword.value = '';
  passwordError.value = '';
  passwordStep.value = 1;
  showPasswordModal.value = true;
};

// 关闭密码修改弹窗
const closePasswordModal = () => {
  showPasswordModal.value = false;
  passwordError.value = '';
  emailVerifyError.value = '';
  passwordStep.value = 1;
};

// 验证邮箱
const verifyEmail = async () => {
  if (!emailVerify.value) {
    emailVerifyError.value = '请输入您的邮箱';
    return;
  }
  
  try {
    loading.value = true;
    emailVerifyError.value = '';
    
    // 调用后端API验证邮箱
    const token = CookieUtil.getCookie('token');
    const response = await axios.post(getApiUrl('/api/user/verify-email'), {
      email: emailVerify.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (response.data.status === 'success') {
      // 邮箱验证通过，进入密码修改步骤
      passwordStep.value = 2;
    } else {
      throw new Error(response.data.message || '邮箱验证失败');
    }
  } catch (err) {
    console.error('邮箱验证失败', err);
    emailVerifyError.value = '邮箱与账号不匹配';
  } finally {
    loading.value = false;
  }
};

// 修改密码
const updatePassword = async () => {
  if (!currentPassword.value) {
    passwordError.value = '请输入当前密码';
    return;
  }
  
  if (!newPassword.value) {
    passwordError.value = '请输入新密码';
    return;
  }
  
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = '两次输入的密码不一致';
    return;
  }
  
  try {
    loading.value = true;
    passwordError.value = '';
    
    const token = CookieUtil.getCookie('token');
    const response = await axios.put(getApiUrl('/api/user/change-password'), {
      user_id: userStore.userId,
      current_password: currentPassword.value,
      new_password: newPassword.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (response.data.status === 'success') {
      alert('密码修改成功');
      showPasswordModal.value = false;
    } else {
      throw new Error(response.data.message || '修改失败');
    }
  } catch (err) {
    console.error('修改密码失败', err);
    passwordError.value = '修改密码失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // 添加调试信息
  console.log('Profile组件挂载');
  console.log('当前登录状态:', {
    isLoggedIn: userStore.isLoggedIn,
    userId: userStore.userId,
    username: userStore.username,
    token: CookieUtil.getCookie('token')
  });
  
  // 重新初始化用户状态
  userStore.initializeState().then(() => {
    console.log('状态初始化后:', {
      isLoggedIn: userStore.isLoggedIn,
      userId: userStore.userId,
      username: userStore.username,
      token: CookieUtil.getCookie('token')
    });
    
    // 初始化后获取用户数据
    fetchUserData();
  }).catch(err => {
    console.error('初始化用户状态失败:', err);
    error.value = '初始化用户状态失败，请稍后重试';
  });
});
</script>

<template>
  <div class="profile">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="retryFetch" class="retry-btn">重试</button>
    </div>
    
    <div v-else class="profile-content">
      <div class="avatar-section">
        <div class="avatar">
          <img :src="userInfo.avatar || '/default-avatar.png'" alt="用户头像" />
        </div>
        <div class="avatar-actions">
          <button class="change-avatar" @click="triggerFileUpload">
            更换头像
          </button>
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileChange" 
            accept="image/*" 
            class="file-input"
          />
          <button class="change-password" @click="showChangePassword">修改密码</button>
        </div>
      </div>
      
      <div class="info-section">
        <div v-if="!showUsernameForm" class="info-item">
          <label>用户名</label>
          <div class="value-with-action">
            <div class="value">{{ userInfo.username }}</div>
            <button class="edit-icon" @click="showEditUsername">✎</button>
          </div>
        </div>
        
        <div v-else class="info-item edit-form">
          <label>修改用户名</label>
          <input 
            type="text" 
            v-model="newUsername" 
            class="edit-input"
            placeholder="输入新用户名"
          />
          <div v-if="usernameError" class="form-error">{{ usernameError }}</div>
          <div class="form-actions">
            <button class="save-btn" @click="updateUsername">保存</button>
            <button class="cancel-btn" @click="cancelUsernameEdit">取消</button>
          </div>
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
      
      <!-- 修改密码弹窗 -->
      <div v-if="showPasswordModal" class="modal-overlay">
        <div class="password-modal">
          <div class="modal-header">
            <h3>{{ passwordStep === 1 ? '账号验证' : '修改密码' }}</h3>
            <button class="close-modal" @click="closePasswordModal">×</button>
          </div>
          
          <div class="modal-body">
            <!-- 步骤1：邮箱验证 -->
            <div v-if="passwordStep === 1">
              <div class="form-group">
                <label>请输入账号关联的邮箱</label>
                <input 
                  type="email" 
                  v-model="emailVerify" 
                  placeholder="输入邮箱进行验证"
                />
              </div>
              
              <div v-if="emailVerifyError" class="form-error">{{ emailVerifyError }}</div>
              
              <div class="form-actions">
                <button class="save-btn" @click="verifyEmail">验证</button>
                <button class="cancel-btn" @click="closePasswordModal">取消</button>
              </div>
            </div>
            
            <!-- 步骤2：密码修改 -->
            <div v-else>
              <div class="form-group">
                <label>当前密码</label>
                <input 
                  type="password" 
                  v-model="currentPassword" 
                  placeholder="输入当前密码"
                />
              </div>
              
              <div class="form-group">
                <label>新密码</label>
                <input 
                  type="password" 
                  v-model="newPassword" 
                  placeholder="输入新密码"
                />
              </div>
              
              <div class="form-group">
                <label>确认新密码</label>
                <input 
                  type="password" 
                  v-model="confirmPassword" 
                  placeholder="再次输入新密码"
                />
              </div>
              
              <div v-if="passwordError" class="form-error">{{ passwordError }}</div>
              
              <div class="form-actions">
                <button class="save-btn" @click="updatePassword">保存</button>
                <button class="cancel-btn" @click="closePasswordModal">取消</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile {
  width: 100%;
  height: 100%;
  color: white;
  display: flex;
  justify-content: center;
}

.loading, .error-message {
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

.profile-content {
  display: grid;
  grid-template-columns: 180px minmax(300px, 450px);
  gap: 2rem;
  padding: 1rem 0;
  width: 100%;
  max-width: 700px;
}

.avatar-section {
  text-align: center;
}

.avatar {
  width: 150px;
  height: 150px;
  margin: 0 auto 1.5rem;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e94560;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: #13173a;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.change-avatar {
  background: rgba(233, 69, 96, 0.15);
  border: 1px solid rgba(233, 69, 96, 0.3);
  color: #e94560;
  padding: 0.7rem 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  width: 100%;
}

.change-avatar:hover {
  background: rgba(233, 69, 96, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.2);
}

.change-password {
  background: rgba(19, 23, 58, 0.5);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.7rem 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  width: 100%;
}

.change-password:hover {
  background: rgba(23, 28, 73, 0.7);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

.file-input {
  display: none;
}

.info-section {
  padding: 1rem 0;
}

.info-item {
  margin-bottom: 1.5rem;
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.5), rgba(23, 28, 73, 0.5));
  padding: 1rem 1.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-item label {
  display: block;
  color: #b9bad3;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-align: center;
}

.info-item .value {
  color: white;
  font-size: 1.1rem;
  text-align: center;
}

.value-with-action {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.edit-icon {
  background: transparent;
  border: none;
  color: #e94560;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: absolute;
  right: 0;
}

.edit-icon:hover {
  transform: scale(1.2);
  color: #ff78a9;
}

.edit-form {
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.7), rgba(23, 28, 73, 0.7));
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  color: #b9bad3;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.edit-input, .form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.edit-input:focus, .form-group input:focus {
  outline: none;
  border-color: rgba(233, 69, 96, 0.5);
  box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2);
}

.form-error {
  color: #e94560;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.2rem;
}

.save-btn {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.save-btn:hover {
  background: linear-gradient(135deg, #e94560, #a92e48);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(233, 69, 96, 0.4);
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #b9bad3;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.7rem 1.5rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* 模态窗口样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.password-modal {
  background: linear-gradient(145deg, #171c49, #13173a);
  border-radius: 15px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-header {
  padding: 1.2rem 1.5rem;
  background: rgba(233, 69, 96, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-header h3 {
  margin: 0;
  color: white;
  font-size: 1.3rem;
}

.close-modal {
  background: transparent;
  border: none;
  color: #b9bad3;
  font-size: 1.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-modal:hover {
  color: white;
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem;
}

@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
  
  .avatar-section {
    margin-bottom: 2rem;
  }
}
</style> 