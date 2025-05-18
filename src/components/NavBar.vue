<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getApiUrl, API_PATHS, CookieUtil, axiosInstance } from '../api/config';
import { useUserStore } from '../stores/user';

// 导入图标
import userIcon from '../assets/用户.png';
import vipIcon from '../assets/vip.png';
import historyIcon from '../assets/历史记录.png';
import messageIcon from '../assets/消息.png';
import favoriteIcon from '../assets/收藏.png';

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

// 鼠标是否在搜索框上的标志
const isMouseOverSearchInput = ref(false);

// 检查用户是否是VIP
const isUserVip = computed(() => {
  // 假设用户数据中有is_vip字段，1表示是VIP
  const userData = localStorage.getItem('userData');
  if (userData) {
    try {
      const userObj = JSON.parse(userData);
      return userObj.is_vip === 1;
    } catch (e) {
      console.error('解析用户数据失败:', e);
      return false;
    }
  }
  return false;
});

// 添加fetchUserData函数
const fetchUserData = async () => {
  if (!userStore.isLoggedIn || !userStore.userId) return;
  
  try {
    const token = CookieUtil.getCookie('token');
    if (!token) return;
    
    console.log('获取用户资料数据');
    const response = await axiosInstance.get(getApiUrl('/api/user/profile'), {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (response.data.status === 'success' && response.data.data) {
      console.log('用户资料数据:', response.data.data);
      // 保存用户数据到本地存储
      localStorage.setItem('userData', JSON.stringify(response.data.data));
      // 强制重新计算isUserVip
      isUserVip.value = response.data.data.is_vip === 1;
    }
  } catch (err) {
    console.error('获取用户资料失败:', err);
  }
};

// 初始化示例数据
const initExampleData = () => {
  // 初始化示例搜索历史
  const exampleHistory = [
    { id: 1, search_query: '你好-李焕英', search_time: new Date().toISOString() },
    { id: 2, search_query: '你的婚礼', search_time: new Date().toISOString() },
    { id: 3, search_query: '刺杀小说家', search_time: new Date().toISOString() }
  ];
  localStorage.setItem('searchHistory', JSON.stringify(exampleHistory));
  
  // 初始化示例电影排行榜
  const exampleRankings = [
    { rank: 1, movie_id: 1, movie: { title: '我不是药神', poster_url: '' } },
    { rank: 2, movie_id: 2, movie: { title: '孤注一掷', poster_url: '' } },
    { rank: 3, movie_id: 3, movie: { title: '哪吒之魔童降世', poster_url: '' } },
    { rank: 4, movie_id: 4, movie: { title: '唐人街探案3', poster_url: '' } },
    { rank: 5, movie_id: 5, movie: { title: '奇迹-笨小孩', poster_url: '' } }
  ];
  localStorage.setItem('movieRankings', JSON.stringify(exampleRankings));
  
  console.log('已初始化示例数据');
};

// NavBar组件挂载时的操作
onMounted(async () => {
  console.log('NavBar组件挂载 - 当前登录状态:', { 
    isLoggedIn: userStore.isLoggedIn, 
    userId: userStore.userId 
  });
  
  // 从Cookie读取rememberMe状态
  rememberMe.value = CookieUtil.getCookie('rememberMe') === 'true';
  
  console.log('记住我初始状态:', rememberMe.value);
  
  // 清除本地存储中的数据，确保使用后端数据
  localStorage.removeItem('searchHistory');
  localStorage.removeItem('movieRankings');
  
  // 获取用户数据
  if (userStore.isLoggedIn) {
    await fetchUserData();
  }
  
  // 预加载搜索数据
  await Promise.all([
    fetchSearchHistory(),
    fetchMovieRankings()
  ]);
  
  console.log('预加载数据完成', {
    searchHistory: searchHistory.value.length,
    movieRankings: movieRankings.value.length,
    isVip: isUserVip.value
  });
});

// 获取搜索历史
const fetchSearchHistory = async () => {
  try {
    // 打印调试信息
    console.log('获取搜索历史');
    
    // 尝试从API获取
    if (isLoggedIn.value && userId.value) {
      const token = CookieUtil.getCookie('token');
      try {
        const response = await axiosInstance.get(getApiUrl(API_PATHS.SEARCH.HISTORY), {
          headers: { Authorization: `Bearer ${token}` },
          params: { user_id: userId.value }
        });
        
        console.log('搜索历史响应:', response.data);
        
        if (response.data && response.data.status === 'success') {
          searchHistory.value = response.data.data || [];
          console.log('API搜索历史数据:', searchHistory.value);
          return;
        }
      } catch (error) {
        console.error('API获取搜索历史失败:', error);
      }
    }
    
    // 只在未登录或API请求失败时才使用空数组
    console.log('使用空搜索历史数据');
    searchHistory.value = [];
  } catch (error) {
    console.error('获取搜索历史总体失败:', error);
    searchHistory.value = [];
  }
};

// 获取电影排行榜
const fetchMovieRankings = async () => {
  try {
    // 打印调试信息
    console.log('获取电影排行榜');
    
    // 从API获取
    try {
      // 先清除本地缓存，确保每次都获取最新数据
      localStorage.removeItem('movieRankings');
      
      const response = await axiosInstance.get(getApiUrl(API_PATHS.SEARCH.RANKINGS));
      console.log('电影排行榜原始响应:', response.data);
      
      if (response.data && response.data.status === 'success' && response.data.data?.length > 0) {
        // 处理数据，确保每个项目有必要的字段
        movieRankings.value = response.data.data.map(item => {
          // 只在movie对象完全不存在时才创建新对象
          if (!item.movie) {
            console.log(`排名${item.rank}没有movie对象，创建默认对象`);
            item.movie = { 
              id: item.movie_id, 
              title: `电影${item.rank}` 
            };
          } else if (!item.movie.title) {
            // 只在title不存在时才添加默认title
            console.log(`排名${item.rank}的movie对象没有title，添加默认title`);
            item.movie.title = `电影${item.rank}`;
          } else {
            // 打印已有的title
            console.log(`排名${item.rank}的电影标题: ${item.movie.title}`);
          }
          return item;
        });
        
        console.log('处理后的电影排行榜数据:', movieRankings.value);
        return;
      }
    } catch (error) {
      console.error('API获取电影排行榜失败:', error);
    }
    
    // API请求失败时使用空数组
    console.log('无法获取排行榜数据，使用空数组');
    movieRankings.value = [];
  } catch (error) {
    console.error('获取电影排行榜总体失败:', error);
    movieRankings.value = [];
  }
};

// 添加搜索历史
const addSearchHistory = async (query) => {
  try {
    console.log('添加搜索历史:', query);
    
    // 创建新的搜索历史项
    const newHistoryItem = {
      id: Date.now(), // 生成唯一ID
      search_query: query,
      search_time: new Date().toISOString()
    };
    
    // 检查是否已存在相同查询
    const existingIndex = searchHistory.value.findIndex(item => item.search_query === query);
    if (existingIndex !== -1) {
      // 如果存在，则更新时间并移到顶部
      searchHistory.value.splice(existingIndex, 1);
    }
    
    // 添加到数组开头
    searchHistory.value.unshift(newHistoryItem);
    
    // 限制历史记录数量（最多保留10条）
    if (searchHistory.value.length > 10) {
      searchHistory.value = searchHistory.value.slice(0, 10);
    }
    
    // 如果用户已登录，同步到服务器
    if (isLoggedIn.value && userId.value) {
      try {
        const token = CookieUtil.getCookie('token');
        await axiosInstance.post(getApiUrl(API_PATHS.SEARCH.HISTORY), {
          user_id: userId.value,
          search_query: query
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        console.log('搜索历史已同步到服务器');
      } catch (err) {
        console.log('保存到服务器失败:', err);
      }
    }
  } catch (error) {
    console.error('添加搜索历史失败:', error);
  }
};

// 删除搜索历史
const deleteSearchHistory = async (historyId) => {
  try {
    console.log('删除搜索历史，ID:', historyId);
    
    // 从内存中删除
    searchHistory.value = searchHistory.value.filter(item => item.id !== historyId);
    console.log('更新后的搜索历史:', searchHistory.value);
    
    // 如果用户已登录，也从服务器删除
    if (isLoggedIn.value) {
      const token = CookieUtil.getCookie('token');
      await axiosInstance.delete(getApiUrl(`${API_PATHS.SEARCH.HISTORY}/${historyId}`), {
        headers: { Authorization: `Bearer ${token}` }
      }).catch(err => {
        console.log('从服务器删除失败:', err);
      });
    }
  } catch (error) {
    console.error('删除搜索历史失败:', error);
  }
};

// 添加鼠标悬停事件处理函数
const handleSearchHover = () => {
  console.log('搜索框鼠标悬停');
  showSearchSuggestions.value = true;
  
  // 立即检查并确保有数据
  if (searchHistory.value.length === 0) {
    fetchSearchHistory();
  }
  
  if (movieRankings.value.length === 0) {
    fetchMovieRankings();
  }
};

// 处理下拉框的鼠标离开事件
const handleSearchSuggestionsLeave = (event) => {
  console.log('下拉框鼠标离开');
  
  // 检查鼠标是否离开下拉框但没有进入搜索框
  // 这里通过检查relatedTarget来判断鼠标去向
  const searchContainer = event.target.closest('.search-container');
  if (!searchContainer.contains(event.relatedTarget)) {
    console.log('鼠标真正离开整个搜索区域，关闭下拉框');
    showSearchSuggestions.value = false;
  } else {
    console.log('鼠标移到搜索框内，保持下拉框显示');
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

// 处理电影点击 - 修改为搜索功能
const handleMovieClick = async (movieId, title) => {
  if (!title) return;
  
  // 添加到搜索历史
  if (isLoggedIn.value) {
    await addSearchHistory(title);
  }
  
  // 更新搜索框的值
  searchQuery.value = title;
  
  // 跳转到搜索结果页
  router.push({
    path: '/search',
    query: { q: title }
  });
  
  showSearchSuggestions.value = false;
};

const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    // 添加到搜索历史
    await addSearchHistory(searchQuery.value.trim());
    
    // 跳转到搜索结果页
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
    
    console.log('开始登录请求', { 
      username: username.value, 
      rememberMe: rememberMe.value 
    });
    
    // 先清除任何可能存在的旧状态
    userStore.logout();
    
    // 添加更多的调试日志
    console.log('发送登录请求到:', getApiUrl(API_PATHS.AUTH.LOGIN));
    
    // 然后进行新的登录
    const result = await userStore.login(username.value, password.value, rememberMe.value);

    console.log('登录结果:', result);

    if (result.success) {
      console.log('登录成功，用户ID:', result.userId);
      
      // 登录成功后立即获取用户资料
      await fetchUserData();
      
      // 关闭登录模态框前确保状态已更新
      setTimeout(() => {
        showLoginModal.value = false;
        username.value = '';
        password.value = '';
        
        // 保持rememberMe的值以便下次使用
        console.log('登录状态已更新，用户ID:', userStore.userId);
      }, 300);
    } else {
      loginError.value = result.message || '登录失败，请稍后重试';
      console.error('登录失败原因:', result.message);
    }
  } catch (error) {
    console.error('登录请求失败:', error);
    if (error.response) {
      console.error('错误响应:', error.response.data);
      console.error('错误状态:', error.response.status);
    }
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
    
    console.log('注册请求URL:', getApiUrl(API_PATHS.AUTH.REGISTER));
    
    const response = await axiosInstance.post(getApiUrl(API_PATHS.AUTH.REGISTER), {
      username: username.value,
      email: email.value,
      password: password.value
    });

    console.log('注册响应:', response.data);

    if (response.data.status === 'success') {
      // 注册成功后自动登录
      console.log('注册成功，开始自动登录');
      
      // 使用store的登录函数
      const result = await userStore.login(username.value, password.value, rememberMe.value);
      console.log('登录结果:', result);
      
      if (result.success) {
        // 更新组件状态
        showRegisterModal.value = false;
        // 清空表单
        username.value = '';
        email.value = '';
        password.value = '';
        confirmPassword.value = '';
      } else {
        registerError.value = '注册成功，但自动登录失败，请手动登录';
        console.error('自动登录失败:', result.message);
      }
    } else {
      registerError.value = response.data.message || '注册失败，请稍后重试';
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
  try {
    console.log('清空所有搜索历史');
    
    // 清空搜索历史
    searchHistory.value = [];
    console.log('已清空搜索历史');
    
    // 如果用户已登录，也清空服务器端
    if (isLoggedIn.value && userId.value) {
      const token = CookieUtil.getCookie('token');
      await axiosInstance.delete(getApiUrl(`${API_PATHS.SEARCH.HISTORY}/clear`), {
        headers: { Authorization: `Bearer ${token}` },
        params: { user_id: userId.value }
      }).catch(err => {
        console.log('清空服务器搜索历史失败:', err);
      });
    }
  } catch (error) {
    console.error('清空搜索历史失败:', error);
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
    
    <div class="search-container" 
        @mouseenter="handleSearchHover">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索电影、演员、导演..." 
        class="search-input"
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch" class="search-button">搜索</button>
      
      <!-- 搜索建议下拉框 -->
      <div v-if="showSearchSuggestions" class="search-suggestions" @mouseleave="handleSearchSuggestionsLeave">
        <!-- 搜索历史 -->
        <div v-if="searchHistory.length > 0" class="suggestion-section">
          <div class="section-header">
            <h4>搜索历史</h4>
            <button class="clear-history" @click="clearAllSearchHistory">清空</button>
          </div>
          <div class="history-items-container">
            <div 
              v-for="history in searchHistory" 
              :key="history.id"
              class="history-item"
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
        </div>
        
        <!-- 电影排行榜 -->
        <div v-if="movieRankings.length > 0" class="suggestion-section">
          <h4 class="section-title">热搜电影</h4>
          <div 
            v-for="ranking in movieRankings" 
            :key="ranking.rank || ranking.movie_id || ranking.id"
            class="suggestion-item clickable"
            @click="handleMovieClick(ranking.movie_id, ranking.movie.title)"
          >
            <span class="rank-number" :class="`rank-${ranking.rank <= 3 ? ranking.rank : 'normal'}`">{{ ranking.rank }}</span>
            <span>{{ ranking.movie.title }}</span>
          </div>
        </div>

        <!-- 无数据提示 -->
        <div v-if="searchHistory.length === 0 && movieRankings.length === 0" class="no-data">
          暂无数据
        </div>
      </div>
    </div>
    
    <div class="user-actions">
      <template v-if="isLoggedIn">
        <div class="user-menu" v-click-outside="() => showUserMenu = false">
          <button @click="toggleUserMenu" class="user-menu-button">
            <div class="user-info-display">
              <img src="../assets/xiaoxin.gif" alt="用户" class="user-avatar" />
              <span :class="['username', {'username-vip': isUserVip}]">{{ userStore.username}}</span>
              <img v-if="isUserVip" src="../assets/会员.png" alt="VIP" class="vip-icon" />
            </div>
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
            <div class="menu-item" @click="handleMenuClick('favorites')">
              <img :src="favoriteIcon" alt="收藏" class="menu-icon" />
              <span>我的收藏</span>
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
            <input type="checkbox" v-model="rememberMe" id="remember-me-checkbox" />
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
  background-color: #0c0e22;
  color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
  background: linear-gradient(to right, #ffffff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  background: #111431;
}

/* 移除悬停时的上移效果 */
.search-container:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}

.search-input {
  flex: 1;
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 25px 0 0 25px;
  font-size: 1rem;
  outline: none;
  background: #111431;
  color: white;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: #777;
}

.search-input:focus {
  background: #13173a;
}

.search-button {
  background: linear-gradient(135deg, #e94560, #c23758);
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
  box-shadow: 0 2px 10px rgba(233, 69, 96, 0.3);
}

/* 移除悬停时的上移效果 */
.search-button:hover {
  background: linear-gradient(135deg, #e94560, #aa2a49);
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
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
  min-width: 120px;
  margin-right: 100px;
  margin-left: -70px;
}

.welcome-text {
  margin-right: 1rem;
}

.login-button, .logout-button {
  background: linear-gradient(135deg, #e94560, #c23758);
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
  background: linear-gradient(135deg, #e94560, #aa2a49);
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
  padding: 5px 10px;
  border-radius: 25px;
  transition: all 0.3s ease;
  outline: none;
}

.user-menu-button:hover {
  transform: none;
}

.user-menu-button:focus {
  outline: none;
  box-shadow: none;
}

.user-info-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 5px;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
}

/* 用户名样式 */
.username {
  font-size: 16px;
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #ffffff; /* 普通用户使用白色 */
}

/* VIP用户使用炫彩渐变效果 */
.username-vip {
  background: linear-gradient(90deg, #e94560, #ff6b9b, #5271ff, #e94560);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientText 8s ease infinite;
}

@keyframes gradientText {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.vip-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  margin-left: -2px;
  transition: transform 0.3s ease;
  align-self: center;
}

.user-menu-button:hover .vip-icon {
  transform: none;
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 5px);
  right: 0;
  background-color: #0c0e22;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  padding: 8px 0;
  min-width: 180px;
  animation: slideDown 0.3s ease;
  backdrop-filter: blur(10px);
  z-index: 200;
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
  transform: translateX(4px);
  color: #e94560;
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
  background: linear-gradient(145deg, #13173a, #0c0e22);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 400px;
  position: relative;
  z-index: 1001;
  color: white;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
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
  color: white;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #aaa;
  padding: 0.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #c4c5e3;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #2a2d50;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #171a31;
  color: white;
}

.form-group input:focus {
  outline: none;
  border-color: #e94560;
  box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2);
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
  color: #b9bad3;
  cursor: pointer;
  user-select: none;
}

.remember-me input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #e94560;
}

.forgot-password {
  color: #e94560;
  text-decoration: none;
}

.error-message {
  color: #e94560;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.modal-actions {
  margin-top: 1.5rem;
}

.confirm-button {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(233, 69, 96, 0.3);
}

.confirm-button:hover {
  background: linear-gradient(135deg, #e94560, #aa2a49);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
}

.register-link,
.login-link {
  margin-top: 1rem;
  text-align: center;
  color: #b9bad3;
}

.register-link a,
.login-link a {
  color: #e94560;
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
  background-color: #0c0e22;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  margin-top: 12px;
  padding: 1rem;
  z-index: 1000;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.05);
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

.section-header h4, .section-title {
  margin: 0;
  font-size: 1rem;
  color: #e94560;
  text-align: left;
}

.clear-history {
  background: none;
  border: none;
  color: #e94560;
  cursor: pointer;
  font-size: 0.875rem;
}

/* 搜索历史横向排列 */
.history-items-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.suggestion-icon {
  width: 16px;
  height: 16px;
}

.suggestion-item {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
  border-radius: 6px;
}

.suggestion-item.clickable {
  cursor: pointer;
}

.suggestion-item.clickable:hover {
  background-color: rgba(233, 69, 96, 0.1);
}

.suggestion-item:not(.clickable) {
  cursor: default;
  opacity: 0.7;
}

/* 排名数字样式 */
.rank-number {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
  border-radius: 50%;
}

.rank-1 {
  background: linear-gradient(135deg, #ff9a00, #ff6a00);
  color: white;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #a9a9a9);
  color: white;
}

.rank-3 {
  background: linear-gradient(135deg, #cd853f, #8b4513);
  color: white;
}

.rank-normal {
  background: rgba(255, 255, 255, 0.1);
  color: #aaa;
}

.delete-history {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 1rem;
  margin-left: 6px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.history-item:hover .delete-history {
  opacity: 1;
}

.delete-history:hover {
  color: #e94560;
}

.no-data {
  text-align: center;
  color: #b9bad3;
  padding: 1rem;
}
</style> 