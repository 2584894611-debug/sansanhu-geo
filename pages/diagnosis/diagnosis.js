// geo-insight/pages/diagnosis/diagnosis.js
// 品牌健康诊断页面

Page({
  data: {
    brandName: '',
    industry: '',
    keywords: '',
    selectedPlatforms: ['doubao', 'qianwen', 'deepseek', 'yuanbao'],
    platforms: [
      { id: 'doubao', name: '字节豆包', checked: true },
      { id: 'qianwen', name: '阿里千问', checked: true },
      { id: 'deepseek', name: 'DeepSeek', checked: true },
      { id: 'yuanbao', name: '腾讯元宝', checked: true }
    ],
    diagnosing: false,
    result: null,
    healthScore: null
  },

  onBrandInput(e) {
    this.setData({ brandName: e.detail.value });
  },

  onIndustryInput(e) {
    this.setData({ industry: e.detail.value });
  },

  onKeywordsInput(e) {
    this.setData({ keywords: e.detail.value });
  },

  onPlatformChange(e) {
    const values = e.detail.value;
    const platforms = this.data.platforms.map(p => ({
      ...p,
      checked: values.includes(p.id)
    }));
    this.setData({ platforms, selectedPlatforms: values });
  },

  async startDiagnosis() {
    const { brandName, industry, keywords, selectedPlatforms } = this.data;
    
    if (!brandName) {
      wx.showToast({ title: '请输入品牌名称', icon: 'none' });
      return;
    }

    this.setData({ diagnosing: true, result: null });

    try {
      const keywordList = keywords 
        ? keywords.split(/[,，\n]/).filter(Boolean)
        : [];

      const res = await wx.cloud.callFunction({
        name: 'brandDiagnosis',
        data: {
          brandName,
          industry: industry || '通用',
          keywords: keywordList,
          platforms: selectedPlatforms
        }
      });

      if (res.result.success) {
        this.setData({ 
          result: res.result,
          healthScore: res.result.healthScore,
          diagnosing: false 
        });
        wx.showToast({ title: '诊断完成', icon: 'success' });
      } else {
        throw new Error(res.result.error);
      }
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '诊断失败', icon: 'none' });
      this.setData({ diagnosing: false });
    }
  },

  getScoreLevel(score) {
    if (score >= 90) return 'S';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    return 'D';
  },

  getScoreColor(level) {
    const colors = {
      'S': '#FFD700',
      'A': '#52c41a',
      'B': '#1890ff',
      'C': '#fa8c16',
      'D': '#ff4d4f'
    };
    return colors[level] || '#999';
  }
});
