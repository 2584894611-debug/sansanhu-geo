// geo-insight/pages/aiSearch/aiSearch.js
// AI搜索推荐分析页面

Page({
  data: {
    query: '',
    category: '',
    competitors: '',
    selectedPlatforms: ['doubao', 'qianwen', 'deepseek', 'yuanbao'],
    platforms: [
      { id: 'doubao', name: '字节豆包', checked: true },
      { id: 'qianwen', name: '阿里千问', checked: true },
      { id: 'deepseek', name: 'DeepSeek', checked: true },
      { id: 'yuanbao', name: '腾讯元宝', checked: true }
    ],
    analyzing: false,
    result: null
  },

  onQueryInput(e) {
    this.setData({ query: e.detail.value });
  },

  onCategoryInput(e) {
    this.setData({ category: e.detail.value });
  },

  onCompetitorsInput(e) {
    this.setData({ competitors: e.detail.value });
  },

  onPlatformChange(e) {
    const values = e.detail.value;
    const platforms = this.data.platforms.map(p => ({
      ...p,
      checked: values.includes(p.id)
    }));
    this.setData({ platforms, selectedPlatforms: values });
  },

  async startAnalysis() {
    const { query, category, competitors, selectedPlatforms } = this.data;

    if (!query) {
      wx.showToast({ title: '请输入搜索词', icon: 'none' });
      return;
    }

    if (selectedPlatforms.length === 0) {
      wx.showToast({ title: '请选择至少一个平台', icon: 'none' });
      return;
    }

    this.setData({ analyzing: true, result: null });

    try {
      const competitorList = competitors
        ? competitors.split(/[,，\n]/).filter(Boolean)
        : [];

      const res = await wx.cloud.callFunction({
        name: 'aiSearchAnalysis',
        data: {
          query,
          category: category || '',
          competitors: competitorList,
          platforms: selectedPlatforms
        }
      });

      if (res.result.success) {
        this.setData({
          result: res.result,
          analyzing: false
        });
        wx.showToast({ title: '分析完成', icon: 'success' });
      } else {
        throw new Error(res.result.error);
      }
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '分析失败', icon: 'none' });
      this.setData({ analyzing: false });
    }
  }
});
