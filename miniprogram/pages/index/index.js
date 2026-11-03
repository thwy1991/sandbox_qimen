// pages/index/index.js
const app = getApp();

// 年份范围
const YEAR_START = 1949;
const YEAR_END = 2099;

// 生成固定列表
const yearList = (() => {
  const list = [];
  for (let y = YEAR_START; y <= YEAR_END; y++) list.push(y + '年');
  return list;
})();

const monthList = (() => {
  const list = [];
  for (let m = 1; m <= 12; m++) list.push(m + '月');
  return list;
})();

const hourList = (() => {
  const list = [];
  for (let h = 0; h <= 23; h++) list.push(String(h).padStart(2, '0') + '时');
  return list;
})();

const minuteList = (() => {
  const list = [];
  for (let m = 0; m <= 59; m++) list.push(String(m).padStart(2, '0') + '分');
  return list;
})();

// 根据年月生成天数列表
function genDayList(year, month) {
  const days = new Date(year, month, 0).getDate();
  const list = [];
  for (let d = 1; d <= days; d++) list.push(d + '日');
  return list;
}

Page({
  data: {
    // 列表数据（固定列表直接初始化）
    yearList: yearList,
    monthList: monthList,
    dayList: [],
    hourList: hourList,
    minuteList: minuteList,
    // 当前选中索引
    yearIndex: 0,
    monthIndex: 0,
    dayIndex: 0,
    hourIndex: 0,
    minuteIndex: 0,
    // 时辰地支
    hourZhi: '',
    currentDate: ''
  },

  onLoad() {
    this.setNowTime();
  },

  setNowTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();
    const hour = now.getHours();
    const minute = now.getMinutes();

    // 生成当前年月的天数列表
    const dayList = genDayList(year, month);

    this.setData({
      yearList: yearList,
      monthList: monthList,
      dayList: dayList,
      hourList: hourList,
      minuteList: minuteList,
      yearIndex: year - YEAR_START,
      monthIndex: month - 1,
      dayIndex: day - 1,
      hourIndex: hour,
      minuteIndex: minute,
      hourZhi: this.getHourZhi(hour),
      currentDate: `${year}年${month}月${day}日 ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
    });
  },

  getHourZhi(hour) {
    if (hour === 23 || hour === 0) return '子';
    const map = [
      [1, 3, '丑'], [3, 5, '寅'], [5, 7, '卯'],
      [7, 9, '辰'], [9, 11, '巳'], [11, 13, '午'],
      [13, 15, '未'], [15, 17, '申'], [17, 19, '酉'],
      [19, 21, '戌'], [21, 23, '亥'],
    ];
    for (const [s, e, zhi] of map) {
      if (hour >= s && hour < e) return zhi;
    }
    return '子';
  },

  onYearChange(e) {
    const yearIndex = parseInt(e.detail.value);
    const year = yearIndex + YEAR_START;
    const month = this.data.monthIndex + 1;
    const dayList = genDayList(year, month);
    // 如果当前日超过新月份天数，调整为最后一天
    let dayIndex = this.data.dayIndex;
    if (dayIndex >= dayList.length) {
      dayIndex = dayList.length - 1;
    }
    this.setData({ yearIndex, dayList, dayIndex });
  },

  onMonthChange(e) {
    const monthIndex = parseInt(e.detail.value);
    const year = this.data.yearIndex + YEAR_START;
    const dayList = genDayList(year, monthIndex + 1);
    let dayIndex = this.data.dayIndex;
    if (dayIndex >= dayList.length) {
      dayIndex = dayList.length - 1;
    }
    this.setData({ monthIndex, dayList, dayIndex });
  },

  onDayChange(e) {
    const dayIndex = parseInt(e.detail.value);
    this.setData({ dayIndex });
  },

  onHourChange(e) {
    const hourIndex = parseInt(e.detail.value);
    this.setData({ hourIndex, hourZhi: this.getHourZhi(hourIndex) });
  },

  onMinuteChange(e) {
    const minuteIndex = parseInt(e.detail.value);
    this.setData({ minuteIndex });
  },

  onNowTap() {
    this.setNowTime();
  },

  onPaipanTap() {
    const year = this.data.yearIndex + YEAR_START;
    const month = this.data.monthIndex + 1;
    const day = this.data.dayIndex + 1;
    const hour = this.data.hourIndex;
    const minute = this.data.minuteIndex;
    wx.navigateTo({
      url: `/pages/chart/chart?year=${year}&month=${month}&day=${day}&hour=${hour}&minute=${minute}`
    });
  },

  onAboutTap() {
    wx.navigateTo({
      url: '/pages/about/about'
    });
  }
});
