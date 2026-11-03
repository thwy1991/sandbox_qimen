// app.js
App({
  globalData: {
    apiBase: 'http://localhost:5000/api', // 开发环境用本地地址，上线时替换为实际域名
    userInfo: null
  },

  onLaunch() {
    // 小程序启动时执行
    console.log('奇门遁甲排盘小程序启动');
  }
});
