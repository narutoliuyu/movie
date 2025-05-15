<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { getApiUrl, API_PATHS } from '../api/config';

const vipPlans = ref([
  {
    id: 1,
    name: '月度会员',
    price: 29.9,
    duration: '30天',
    features: [
      '高清画质',
      '无广告观看',
      '优先客服',
      '新片抢先看'
    ]
  },
  {
    id: 2,
    name: '季度会员',
    price: 79.9,
    duration: '90天',
    features: [
      '高清画质',
      '无广告观看',
      '优先客服',
      '新片抢先看',
      '专属片单'
    ]
  },
  {
    id: 3,
    name: '年度会员',
    price: 299.9,
    duration: '365天',
    features: [
      '4K超清画质',
      '无广告观看',
      '优先客服',
      '新片抢先看',
      '专属片单',
      '离线下载',
      '多设备同步'
    ]
  }
]);

const selectedPlan = ref(null);
const loading = ref(false);
const error = ref('');

const selectPlan = (plan) => {
  selectedPlan.value = plan;
};

const handlePurchase = async () => {
  if (!selectedPlan.value) {
    error.value = '请选择会员套餐';
    return;
  }
  
  try {
    loading.value = true;
    error.value = '';
    
    const response = await axios.post(getApiUrl('/api/vip/purchase'), {
      planId: selectedPlan.value.id
    });
    
    if (response.data.status === 'success') {
      alert('购买成功！');
    }
  } catch (err) {
    error.value = '购买失败，请稍后重试';
    console.error('购买失败:', err);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="vip">
    <div class="header">
      <h2>VIP会员</h2>
      <p class="subtitle">解锁更多精彩内容</p>
    </div>
    
    <div class="plans-container">
      <div 
        v-for="plan in vipPlans" 
        :key="plan.id"
        class="plan-card"
        :class="{ 'selected': selectedPlan?.id === plan.id }"
        @click="selectPlan(plan)"
      >
        <div class="plan-header">
          <h3>{{ plan.name }}</h3>
          <div class="price">
            <span class="amount">¥{{ plan.price }}</span>
            <span class="duration">/{{ plan.duration }}</span>
          </div>
        </div>
        
        <ul class="features">
          <li v-for="feature in plan.features" :key="feature">
            <i class="check-icon">✓</i>
            {{ feature }}
          </li>
        </ul>
        
        <button 
          class="select-button"
          :class="{ 'selected': selectedPlan?.id === plan.id }"
        >
          {{ selectedPlan?.id === plan.id ? '已选择' : '选择套餐' }}
        </button>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div class="actions">
      <button 
        class="purchase-button"
        :disabled="!selectedPlan || loading"
        @click="handlePurchase"
      >
        {{ loading ? '处理中...' : '立即购买' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.vip {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h2 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.subtitle {
  color: #666;
  margin-top: 0.5rem;
}

.plans-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.plan-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.plan-card.selected {
  border-color: #4a90e2;
}

.plan-header {
  text-align: center;
  margin-bottom: 2rem;
}

.plan-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.price {
  margin-top: 1rem;
}

.amount {
  font-size: 2rem;
  font-weight: bold;
  color: #4a90e2;
}

.duration {
  color: #666;
  font-size: 1rem;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem;
}

.features li {
  padding: 0.5rem 0;
  color: #666;
  display: flex;
  align-items: center;
}

.check-icon {
  color: #4a90e2;
  margin-right: 0.5rem;
  font-weight: bold;
}

.select-button {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #4a90e2;
  background: none;
  color: #4a90e2;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.select-button.selected {
  background: #4a90e2;
  color: white;
}

.actions {
  text-align: center;
}

.purchase-button {
  padding: 1rem 3rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.purchase-button:hover:not(:disabled) {
  background: #357abd;
}

.purchase-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  text-align: center;
  color: #dc3545;
  margin-bottom: 1rem;
}
</style> 