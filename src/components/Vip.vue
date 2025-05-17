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
  width: 100%;
  height: 100%;
  color: white;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h2 {
  font-size: 1.8rem;
  background: linear-gradient(135deg, #e94560, #ff78a9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.3);
  margin: 0;
  letter-spacing: 1px;
}

.subtitle {
  color: #b9bad3;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.plans-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.plan-card {
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.7), rgba(23, 28, 73, 0.7));
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.plan-card.selected {
  border: 2px solid #e94560;
  background: linear-gradient(145deg, rgba(19, 23, 58, 0.8), rgba(23, 28, 73, 0.8));
  box-shadow: 0 8px 25px rgba(233, 69, 96, 0.2);
}

.plan-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.plan-header h3 {
  margin: 0;
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
}

.price {
  margin-top: 0.8rem;
}

.amount {
  font-size: 1.8rem;
  font-weight: bold;
  background: linear-gradient(135deg, #e94560, #ff78a9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.duration {
  color: #b9bad3;
  font-size: 0.9rem;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
  flex-grow: 1;
}

.features li {
  padding: 0.5rem 0;
  color: #b9bad3;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.check-icon {
  color: #e94560;
  margin-right: 0.6rem;
  font-weight: bold;
}

.select-button {
  width: 100%;
  padding: 0.8rem;
  background: rgba(233, 69, 96, 0.1);
  border: 1px solid rgba(233, 69, 96, 0.3);
  color: #e94560;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  margin-top: auto;
  align-self: center;
}

.select-button:hover {
  background: rgba(233, 69, 96, 0.2);
  transform: translateY(-3px);
}

.select-button.selected {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

.error-message {
  color: #e94560;
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.actions {
  text-align: center;
  margin-top: 2rem;
}

.purchase-button {
  background: linear-gradient(135deg, #e94560, #c23758);
  color: white;
  border: none;
  padding: 1rem 3rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
}

.purchase-button:hover {
  background: linear-gradient(135deg, #e94560, #aa2a49);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(233, 69, 96, 0.4);
}

.purchase-button:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

@media (max-width: 768px) {
  .plans-container {
    grid-template-columns: 1fr;
  }
}
</style> 