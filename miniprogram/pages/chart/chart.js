// pages/chart/chart.js
const app = getApp();

Page({
  data: {
    loading: true,
    error: false,
    errorMsg: '',
    chartData: null,
    // 九宫格数据：按洛书布局 [4,9,2,3,5,7,8,1,6]
    gridCells: []
  },

  onLoad(options) {
    const { year, month, day, hour, minute } = options;
    this.fetchChart(year, month, day, hour, minute);
  },

  fetchChart(year, month, day, hour, minute) {
    this.setData({ loading: true, error: false });

    const apiBase = app.globalData.apiBase;
    wx.request({
      url: `${apiBase}/qimen/chart`,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: {
        year: parseInt(year),
        month: parseInt(month),
        day: parseInt(day),
        hour: parseInt(hour),
        minute: parseInt(minute)
      },
      success: (res) => {
        if (res.data && res.data.success) {
          this.setData({
            chartData: res.data,
            loading: false
          });
          this.buildGrid(res.data.palaces);
        } else {
          this.setData({
            loading: false,
            error: true,
            errorMsg: (res.data && res.data.error) || '排盘失败，请重试'
          });
        }
      },
      fail: (err) => {
        this.setData({
          loading: false,
          error: true,
          errorMsg: '网络连接失败，请检查网络后重试'
        });
      }
    });
  },

  buildGrid(palaces) {
    // 按洛书布局排列：行0=[4,9,2], 行1=[3,5,7], 行2=[8,1,6]
    const layout = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
    const grid = [];
    for (const row of layout) {
      const rowData = row.map(p => {
        const p_data = palaces.find(p_item => p_item.palace === p);
        if (!p_data) return {};
        return {
          palace: p_data.palace,
          name: p_data.name,
          god: p_data.god,
          hv_star: p_data.hv_star,
          hv_stem: p_data.hv_stem,
          door: p_data.door,
          di_pan_stem: p_data.di_pan_stem,
          earth_god: p_data.earth_god,
          is_center: p_data.is_center,
          is_zhi_fu: p_data.is_zhi_fu,
          is_zhi_shi: p_data.is_zhi_shi,
          is_kong: p_data.is_kong,
          is_ma: p_data.is_ma,
          jigan_stem: p_data.jigan_stem,
          jigan_star: p_data.jigan_star,
          earth_jigan: p_data.earth_jigan
        };
      });
      grid.push(rowData);
    }
    this.setData({ gridCells: grid });
  },

  onRetry() {
    const d = this.data.chartData;
    if (d) {
      this.fetchChart(d.datetime.year, d.datetime.month, d.datetime.day, d.datetime.hour, d.datetime.minute);
    }
  },

  onBack() {
    wx.navigateBack();
  }
});
