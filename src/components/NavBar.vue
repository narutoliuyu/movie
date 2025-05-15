<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getApiUrl, API_PATHS, CookieUtil } from '../api/config';
import { useUserStore } from '../stores/user';

// 导入图标
import userIcon from '../assets/用户.png';
import vipIcon from '../assets/vip.png';
import historyIcon from '../assets/历史记录.png';
import messageIcon from '../assets/消息.png';

// 添加 click-outside 指令
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.addEventListener('click', el._clickOutside);
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside);
  }
};

const router = useRouter();
const userStore = useUserStore();
const searchQuery = ref('');
const showLoginModal = ref(false);
const showRegisterModal = ref(false);
const showSearchSuggestions = ref(false);
const searchHistory = ref([]);
const movieRankings = ref([]);

// 使用计算属性从store获取登录状态
const isLoggedIn = computed(() => userStore.isLoggedIn);
const userId = computed(() => userStore.userId);

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const rememberMe = ref(false);
const loginError = ref('');
const registerError = ref('');
const showUserMenu = ref(false);

// NavBar组件挂载时的操作
onMounted(async () => {
  console.log('NavBar组件挂载 - 当前登录状态:', { 
    isLoggedIn: userStore.isLoggedIn, 
    userId: userStore.userId 
  });
});

// 获取搜索历史
const fetchSearchHistory = async () => {
  if (!isLoggedIn.value || !userId.value) return;
  
  try {
    const token = CookieUtil.getCookie('token');
    // 打印调试信息
    console.log('获取搜索历史，userId:', userId.value);
    
    const response = await axios.get(getApiUrl(API_PATHS.SEARCH.HISTORY), {
      headers: { Authorization: `Bearer ${token}` },
      params: { user_id: userId.value }
    });
    
    console.log('搜索历史响应:', response.data);
    
    if (response.data.status === 'success') {
      searchHistory.value = response.data.data;
      console.log('搜索历史数据:', searchHistory.value);
    }
  } catch (error) {
    console.error('获取搜索历史失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
    }
  }
};

// 获取电影排行榜
const fetchMovieRankings = async () => {
  try {
    // 打印调试信息
    console.log('获取电影排行榜');
    
    const response = await axios.get(getApiUrl(API_PATHS.SEARCH.RANKINGS));
    
    console.log('电影排行榜响应:', response.data);
    
    if (response.data.status === 'success') {
      movieRankings.value = response.data.data;
      console.log('电影排行榜数据:', movieRankings.value);
    }
  } catch (error) {
    console.error('获取电影排行榜失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
    }
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
    await fetchSearchHistory(); // 重新获取搜索历史
  } catch (error) {
    console.error('删除搜索历史失败:', error);
  }
};

// 监听搜索框焦点
const handleSearchFocus = async () => {
  console.log('搜索框获得焦点');
  showSearchSuggestions.value = true;
  if (isLoggedIn.value) {
    await fetchSearchHistory();
  }
  await fetchMovieRankings();
};

// 监听搜索框失焦
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

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    if (isLoggedIn.value && userId.value) {
      await addSearchHistory(searchQuery.value.trim());
    }
    router.push({
      path: '/search',
      query: { q: searchQuery.value.trim() }
    });
    showSearchSuggestions.value = false;
  }
};

const handleLogin = async () => {
  try {
    loginError.value = '';
    if (!username.value || !password.value) {
      loginError.value = '请输入用户名和密码';
      return;
    }
    
    console.log('开始登录请求', { username: username.value });
    const result = await userStore.login(username.value, password.value, rememberMe.value);

    if (result.success) {
      showLoginModal.value = false;
      username.value = '';
      password.value = '';
      
      console.log('登录成功，用户ID:', result.userId);
    } else {
      loginError.value = result.message;
    }
  } catch (error) {
    console.error('登录请求失败:', error);
    loginError.value = '登录过程中出现错误，请稍后重试';
  }
};

const handleLogout = () => {
  userStore.logout();
  showUserMenu.value = false;
  router.push('/');
};

const goToHome = () => {
  router.push({ name: 'home' });
};

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const navigateTo = (route) => {
  showUserMenu.value = false;
  // 这里先使用占位路由
  console.log('导航到:', route);
};

// 表单验证
const validateRegisterForm = () => {
  if (!username.value) {
    registerError.value = '请输入用户名';
    return false;
  }
  if (!email.value) {
    registerError.value = '请输入邮箱';
    return false;
  }
  if (!email.value.includes('@')) {
    registerError.value = '请输入有效的邮箱地址';
    return false;
  }
  if (!password.value) {
    registerError.value = '请输入密码';
    return false;
  }
  if (password.value.length < 6) {
    registerError.value = '密码长度不能少于6位';
    return false;
  }
  if (password.value !== confirmPassword.value) {
    registerError.value = '两次输入的密码不一致';
    return false;
  }
  return true;
};

const handleRegister = async () => {
  try {
    registerError.value = '';
    
    // 验证表单
    if (!validateRegisterForm()) {
      return;
    }
    
    console.log('开始注册，提交数据:', {
      username: username.value,
      email: email.value,
      password: '***' // 不打印实际密码
    });
    
    const response = await axios.post(getApiUrl(API_PATHS.AUTH.REGISTER), {
      username: username.value,
      email: email.value,
      password: password.value
    });

    console.log('注册响应:', response.data);

    if (response.data.status === 'success') {
      // 注册成功后自动登录
      console.log('注册成功，开始自动登录');
      
      // 使用auth.js中的登录函数，确保使用Cookie存储
      const result = await authLogin(username.value, password.value, rememberMe.value);
      
      if (result.success) {
        // 更新组件状态
        isLoggedIn.value = true;
        userId.value = result.userId;
        showRegisterModal.value = false;
        showLoginModal.value = false;
        // 清空表单
        username.value = '';
        email.value = '';
        password.value = '';
        confirmPassword.value = '';
      }
    }
  } catch (error) {
    console.error('注册失败:', error);
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    registerError.value = error.response?.data?.message || '注册失败，请稍后重试';
  }
};

const switchToLogin = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
  // 清空注册表单
  username.value = '';
  email.value = '';
  password.value = '';
  confirmPassword.value = '';
  registerError.value = '';
};

const switchToRegister = () => {
  showLoginModal.value = false;
  showRegisterModal.value = true;
  // 清空登录表单
  username.value = '';
  password.value = '';
  loginError.value = '';
};

const handleMenuClick = (component) => {
  showUserMenu.value = false;
  router.push({
    path: '/center',
    query: { component }
  });
};

// 清空所有搜索历史
const clearAllSearchHistory = async () => {
  if (!isLoggedIn.value || !userId.value) return;
  
  try {
    const token = CookieUtil.getCookie('token');
    // 先尝试调用后端接口清空
    try {
      await axios.delete(getApiUrl(`${API_PATHS.SEARCH.HISTORY}/clear`), {
        headers: { Authorization: `Bearer ${token}` },
        params: { user_id: userId.value }
      });
    } catch (err) {
      console.log('后端可能没有清空接口，将单独删除每条记录');
      // 如果后端没有提供清空接口，则逐个删除
      const deletePromises = searchHistory.value.map(history => 
        deleteSearchHistory(history.id)
      );
      await Promise.all(deletePromises);
    }
    
    // 无论如何都清空前端显示
    searchHistory.value = [];
    console.log('已清空搜索历史');
  } catch (error) {
    console.error('清空搜索历史失败:', error);
    // 至少清空前端显示
    searchHistory.value = [];
  }
};
</script>

<template>
  <header class="navbar">
    <div class="logo-container" @click="goToHome">
      <img src="../assets/logo.png" alt="电影网站" class="logo" />
      <h1 class="site-name">黑盒影视</h1>
    </div>
    
    <div class="search-container">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索电影、演员、导演..." 
        class="search-input"
        @focus="handleSearchFocus"
        @blur="handleSearchBlur"
      />
      <button @click="handleSearch" class="search-button">搜索</button>
      
      <!-- 搜索建议下拉框 -->
      <div v-if="showSearchSuggestions" class="search-suggestions">
        <!-- 搜索历史 -->
        <div v-if="isLoggedIn && searchHistory.length > 0" class="suggestion-section">
          <div class="section-header">
            <h4>搜索历史</h4>
            <button class="clear-history" @click="clearAllSearchHistory">清空</button>
          </div>
          <div 
            v-for="history in searchHistory" 
            :key="history.id"
            class="suggestion-item"
          >
            <div class="suggestion-content" @click="handleSuggestionClick(history.search_query)">
              <img src="../assets/历史记录.png" alt="历史" class="suggestion-icon" />
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
    
    <div class="user-actions">
      <template v-if="isLoggedIn">
        <div class="user-menu" v-click-outside="() => showUserMenu = false">
          <button @click="toggleUserMenu" class="user-menu-button">
            <img :src="userIcon" alt="用户" class="user-icon" />
          </button>
          
          <div v-if="showUserMenu" class="user-dropdown">
            <div class="menu-item" @click="handleMenuClick('profile')">
              <img :src="userIcon" alt="个人中心" class="menu-icon" />
              <span>个人中心</span>
            </div>
            <div class="menu-item" @click="handleMenuClick('vip')">
              <img :src="vipIcon" alt="VIP" class="menu-icon" />
              <span>VIP会员</span>
            </div>
            <div class="menu-item" @click="handleMenuClick('history')">
              <img :src="historyIcon" alt="历史记录" class="menu-icon" />
              <span>观看历史</span>
            </div>
            <div class="menu-item" @click="handleMenuClick('message')">
              <img :src="messageIcon" alt="消息" class="menu-icon" />
              <span>消息中心</span>
            </div>
            <div class="menu-divider"></div>
            <div class="menu-item logout" @click="handleLogout">
              <span>退出登录</span>
            </div>
          </div>
        </div>
      </template>
      <button v-else @click="showLoginModal = true" class="login-button">登录</button>
    </div>

    <!-- 登录弹窗 -->
    <div v-if="showLoginModal" class="login-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>欢迎登录</h3>
          <button class="close-button" @click="showLoginModal = false">&times;</button>
        </div>
        
        <div class="form-group">
          <label for="login-username">用户名</label>
          <input 
            type="text" 
            id="login-username" 
            v-model="username"
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <div class="form-group">
          <label for="login-password">密码</label>
          <input 
            type="password" 
            id="login-password" 
            v-model="password"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span>7天内免登录</span>
          </label>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>

        <div v-if="loginError" class="error-message">
          {{ loginError }}
        </div>

        <div class="modal-actions">
          <button @click="handleLogin" class="confirm-button">登录</button>
        </div>

        <div class="register-link">
          还没有账号？<a href="#" @click="switchToRegister">立即注册</a>
        </div>
      </div>
      <div class="modal-overlay" @click="showLoginModal = false"></div>
    </div>

    <!-- 注册弹窗 -->
    <div v-if="showRegisterModal" class="register-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>注册新账号</h3>
          <button class="close-button" @click="showRegisterModal = false">&times;</button>
        </div>
        
        <div class="form-group">
          <label for="register-username">用户名</label>
          <input 
            type="text" 
            id="register-username" 
            v-model="username"
            placeholder="请输入用户名"
            @keyup.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="register-email">邮箱</label>
          <input 
            type="email" 
            id="register-email" 
            v-model="email"
            placeholder="请输入邮箱"
            @keyup.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="register-password">密码</label>
          <input 
            type="password" 
            id="register-password" 
            v-model="password"
            placeholder="请输入密码（至少6位）"
            @keyup.enter="handleRegister"
          />
        </div>
        
        <div class="form-group">
          <label for="register-confirm-password">确认密码</label>
          <input 
            type="password" 
            id="register-confirm-password" 
            v-model="confirmPassword"
            placeholder="请再次输入密码"
            @keyup.enter="handleRegister"
          />
        </div>

        <div v-if="registerError" class="error-message">
          {{ registerError }}
        </div>

        <div class="modal-actions">
          <button @click="handleRegister" class="confirm-button">注册</button>
        </div>

        <div class="login-link">
          已经有账号？<a href="#" @click="switchToLogin">立即登录</a>
        </div>
      </div>
      <div class="modal-overlay" @click="showRegisterModal = false"></div>
    </div>
  </header>
</template>

<style scoped>
/* 导航栏样式 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #1a1a2e;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  height: 70px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
}

.logo-container {
  display: flex;
  align-items: center;
  min-width: 180px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo-container:hover {
  transform: scale(1.05);
}

.logo {
  height: 40px;
  width: 40px;
  margin-right: 1rem;
}

.site-name {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

/* 搜索框样式 */
.search-container {
  flex: 1;
  max-width: 500px;
  margin: 0 2rem;
  display: flex;
  position: relative;
  border-radius: 25px;
  overflow: visible;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  background: #16213e;
}

.search-container:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.search-input {
  flex: 1;
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 25px 0 0 25px;
  font-size: 1rem;
  outline: none;
  background: #16213e;
  color: white;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: #666;
}

.search-input:focus {
  background: #1a1a2e;
}

.search-button {
  background: #e94560;
  color: white;
  border: none;
  border-radius: 0 25px 25px 0;
  padding: 0.7rem 1.5rem;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-button:hover {
  background: #d03651;
  transform: translateX(2px);
}

@media (max-width: 768px) {
  .search-container {
    margin: 0 1rem;
  }
  
  .search-input {
    padding: 0.5rem 1rem;
  }
  
  .search-button {
    padding: 0.5rem 1rem;
  }
}

/* 用户操作区样式 */
.user-actions {
  display: flex;
  align-items: center;
  min-width: 150px;
  margin-left: 20px;
}

.welcome-text {
  margin-right: 1rem;
}

.login-button, .logout-button {
  background-color: #e94560;
  border: none;
  color: white;
  padding: 0.7rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(233, 69, 96, 0.3);
}

.login-button:hover, .logout-button:hover {
  background-color: #d03651;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
}

/* 用户菜单样式 */
.user-menu {
  position: relative;
}

.user-menu-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.user-menu-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-icon {
  width: 32px;
  height: 32px;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #1a1a2e;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  padding: 8px 0;
  min-width: 180px;
  margin-top: 8px;
  animation: slideDown 0.3s ease;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #fff;
}

.menu-item:hover {
  background-color: rgba(233, 69, 96, 0.1);
}

.menu-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
}

.menu-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.logout {
  color: #e94560;
}

/* 登录和注册弹窗样式 */
.login-modal,
.register-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1001;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

.forgot-password {
  color: #4a90e2;
  text-decoration: none;
}

.error-message {
  color: #dc3545;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.modal-actions {
  margin-top: 1.5rem;
}

.confirm-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.confirm-button:hover {
  background-color: #357abd;
}

.register-link,
.login-link {
  margin-top: 1rem;
  text-align: center;
  color: #666;
}

.register-link a,
.login-link a {
  color: #4a90e2;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover,
.login-link a:hover {
  text-decoration: underline;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 搜索建议下拉框样式 */
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #1a1a2e;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  margin-top: 8px;
  padding: 1rem;
  z-index: 1000;
}

.suggestion-section {
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.section-header h4 {
  margin: 0;
  font-size: 1rem;
  color: #e94560;
}

.clear-history {
  background: none;
  border: none;
  color: #e94560;
  cursor: pointer;
  font-size: 0.875rem;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
  color: white;
}

.suggestion-item:hover {
  background-color: rgba(233, 69, 96, 0.1);
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.suggestion-icon {
  width: 20px;
  height: 20px;
}

.rank-number {
  font-size: 0.875rem;
  font-weight: bold;
  margin-right: 0.5rem;
}

.no-data {
  text-align: center;
  color: #aaa;
  padding: 1rem;
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
</style> 