<template>
  <div class="about-page">
    
    <div class="about-hero">
      <h1 class="about-title">关于三三狐GEO</h1>
      <p class="about-subtitle">让品牌在AI搜索时代被看见</p>
    </div>

    <div class="about-section">
      <h2 class="section-title">🔍 什么是三三狐GEO</h2>
      <p class="section-text">
        三三狐GEO是一款专业的<strong>生成式引擎优化（GEO）</strong>SaaS平台。不同于传统SEO优化搜索引擎排名，三三狐GEO专注于让您的品牌内容被AI搜索引擎（如DeepSeek、豆包、Kimi、ChatGPT等）优先理解、信任和推荐。
      </p>
      <p class="section-text">
        当用户向AI提问时，被AI引用等同于获得"超级大V推荐"——这就是GEO的核心价值。
      </p>
    </div>

    <div class="about-section">
      <h2 class="section-title">⚡ 核心功能</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>AI搜索可见度诊断</h3>
          <p>检测您的品牌在DeepSeek、豆包、Kimi等主流AI搜索中的曝光率和推荐位，精准定位优化空间</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>内容优化建议</h3>
          <p>基于AI引擎的语义理解偏好，提供结构化内容改写方案，让您的内容更容易被AI引用</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🌐</div>
          <h3>知识图谱覆盖分析</h3>
          <p>全面评估百度百科、知乎、小红书等知识平台的品牌存在，构建AI信任的证据链</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3>竞品对比</h3>
          <p>对标竞争对手的GEO表现，发现差异化优势，制定精准的AI搜索竞争策略</p>
        </div>
      </div>
    </div>

    <div class="about-section">
      <h2 class="section-title">🏢 运营主体</h2>
      <div class="company-info">
        <p><strong>武汉爱黑马文化传媒有限公司</strong></p>
        <p>华中地区新媒体整合营销头部机构，10年深耕内容行业</p>
        <p>运营"武汉吃喝玩乐"、"HAO科技"等知名自媒体品牌</p>
      </div>
    </div>

    <div class="about-section">
      <h2 class="section-title">📞 联系我们</h2>
      <div class="contact-info">
        <p>📧 邮箱：contact@xhpj.cloud</p>
        <p>📱 电话：189 8603 4050</p>
        <p>📍 地址：武汉市江汉区</p>
      </div>
    </div>

    <div class="about-footer">
      <p>鄂ICP备2025150688号</p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  color: #2c2c2c;
}

.about-hero {
  text-align: center;
  padding: 3rem 0 2rem;
}

.about-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.about-subtitle {
  font-size: 1.25rem;
  color: #555;
  font-weight: 400;
}

.about-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 16px;
  border: 1px solid #e8e8e8;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #D4AF37;
  margin-bottom: 1rem;
}

.section-text {
  font-size: 1rem;
  line-height: 1.8;
  color: #333;
  margin-bottom: 0.75rem;
}

.section-text strong {
  color: #B8941F;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1rem;
}

.feature-card {
  padding: 1.5rem;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  transition: transform 0.2s, border-color 0.2s;
}

.feature-card:hover {
  transform: translateY(-2px);
  border-color: #D4AF37;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #B8941F;
  margin-bottom: 0.5rem;
}

.feature-card p {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #555;
}

.company-info {
  line-height: 2;
  color: #333;
}

.company-info strong {
  color: #B8941F;
  font-size: 1.1rem;
}

.contact-info {
  line-height: 2.2;
  color: #333;
  font-size: 1rem;
}

.about-footer {
  text-align: center;
  padding: 2rem 0;
  color: #999;
  font-size: 0.85rem;
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .about-title {
    font-size: 1.8rem;
  }
  
  .about-section {
    padding: 1.25rem;
  }
}
</style>
