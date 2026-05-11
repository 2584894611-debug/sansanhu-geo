// geo-insight/pages/analyze/analyze.js
// 竞品GEO分析页面

Page({
  data: {
    brandName: '',
    competitors: '',
    selectedPlatforms: ['doubao', 'qianwen', 'deepseek', 'yuanbao'],
    platforms: [
      { id: 'doubao', name: '字节豆包', checked: true },
      { id: 'qianwen', name: '阿里千问', checked: true },
      { id: 'deepseek', name: 'DeepSeek', checked: true },
      { id: 'yuanbao', name: '腾讯元宝', checked: true }
    ],
    analyzing: false,
    results: null,
    reportUrl: null
  },

  // 输入品牌名
  onBrandInput(e) {
    this.setData({ brandName: e.detail.value });
  },

  // 输入竞品
  onCompetitorsInput(e) {
    this.setData({ competitors: e.detail.value });
  },

  // 选择平台
  onPlatformChange(e) {
    const values = e.detail.value;
    const platforms = this.data.platforms.map(p => ({
      ...p,
      checked: values.includes(p.id)
    }));
    this.setData({ platforms, selectedPlatforms: values });
  },

  // 开始分析
  async startAnalyze() {
    const { brandName, competitors, selectedPlatforms } = this.data;
    
    if (!brandName) {
      wx.showToast({ title: '请输入品牌名称', icon: 'none' });
      return;
    }

    if (selectedPlatforms.length === 0) {
      wx.showToast({ title: '请选择至少一个平台', icon: 'none' });
      return;
    }

    this.setData({ analyzing: true, results: null });

    try {
      const competitorList = competitors 
        ? competitors.split(/[,，\n]/).filter(Boolean)
        : [];

      const res = await wx.cloud.callFunction({
        name: 'analyzeCompetitor',
        data: {
          brandName,
          competitors: competitorList,
          platforms: selectedPlatforms
        }
      });

      if (res.result.success) {
        this.setData({ 
          results: res.result,
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
  },

  // 生成报告
  async generateReport() {
    if (!this.data.results) return;

    wx.showLoading({ title: '生成报告中...' });

    try {
      const res = await wx.cloud.callFunction({
        name: 'generateReport',
        data: {
          brandName: this.data.brandName,
          results: this.data.results
        }
      });

      wx.hideLoading();
      this.setData({ reportUrl: res.result.fileID });
      wx.showToast({ title: '报告生成成功', icon: 'success' });
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '报告生成失败', icon: 'none' });
    }
  },

  // 下载报告
  downloadReport() {
    const fileId = this.data.reportUrl;
    if (!fileId) return;

    wx.cloud.downloadFile({
      fileID: fileId,
      success: res => {
        wx.openDocument({
          filePath: res.tempFilePath,
          showMenu: true,
          success: () => {
            console.log('报告打开成功');
          }
        });
      }
    });
  },

  // 分享结果
  onShareAppMessage() {
    return {
      title: `${this.data.brandName}的GEO分析报告`,
      path: '/pages/analyze/analyze'
    };
  }
});
