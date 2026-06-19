import { useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import styles from './StatsChart.module.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const CHART_COLORS = ['#ef4444', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'];

const fallbackData = [
  {
    location_name: 'Đồi chè Cầu Đất (11.8942, 108.5303)',
    timeline: [
      { time: '03:00', probability: 45.0 },
      { time: '04:00', probability: 70.5 },
      { time: '05:00', probability: 90.0 },
      { time: '06:00', probability: 95.5 },
      { time: '07:00', probability: 85.0 },
      { time: '08:00', probability: 50.0 },
      { time: '09:00', probability: 20.0 },
    ],
  },
  {
    location_name: 'Đỉnh Hòn Bồ (11.9688, 108.4811)',
    timeline: [
      { time: '03:00', probability: 60.0 },
      { time: '04:00', probability: 85.0 },
      { time: '05:00', probability: 88.0 },
      { time: '06:00', probability: 80.0 },
      { time: '07:00', probability: 65.0 },
      { time: '08:00', probability: 35.0 },
      { time: '09:00', probability: 15.0 },
    ],
  },
];

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        font: { family: 'Inter', size: 13, weight: 'bold' },
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => `${context.dataset.label}: ${context.parsed.y}%`,
      },
    },
  },
  scales: {
    x: {
      offset: true, // Giúp các điểm không bị dính sát vào mép 2 bên
      title: {
        display: true,
        text: 'Thời gian trong ngày',
        font: { family: 'Inter', weight: 'bold', size: 14 },
      },
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
    y: {
      title: {
        display: true,
        text: 'Khả năng xuất hiện mây (%)',
        font: { family: 'Inter', weight: 'bold', size: 14 },
      },
      min: 0,
      max: 100,
      grid: { color: 'rgba(0,0,0,0.05)' },
    },
  },
};

export default function StatsChart({ data, timeOffset }) {
  const navigate = useNavigate();
  const location = useLocation();
  const chartData = data && data.length > 0 ? data : []; // Use empty array if no data instead of fallback for production

  const formattedData = useMemo(() => {
    // Nếu có timeOffset, chỉ lấy timeOffset + 1 điểm (ví dụ timeOffset = 0 -> lấy 1 điểm hiện tại)
    const limit = timeOffset !== undefined && timeOffset !== null ? timeOffset + 1 : 24;

    const labels = chartData[0]?.timeline?.slice(0, limit).map((t) => t.time) || [];
    const datasets = chartData.map((loc, index) => ({
      label: loc.location_name.split('(')[0].trim(),
      data: loc.timeline ? loc.timeline.slice(0, limit).map((t) => t.probability) : [],
      borderColor: CHART_COLORS[index % CHART_COLORS.length],
      backgroundColor: CHART_COLORS[index % CHART_COLORS.length] + '33',
      tension: 0.4,
      fill: false,
      borderWidth: 3,
      pointRadius: 6,
      pointHoverRadius: 9,
    }));

    return { labels, datasets };
  }, [chartData, timeOffset]);



  // Tính toán độ rộng của biểu đồ. Nếu có ít điểm thì thu hẹp lại để các điểm tập trung ở giữa
  const pointCount = formattedData.labels.length;
  const wrapperStyle = {
    maxWidth: pointCount <= 2 ? '500px' : pointCount <= 4 ? '800px' : '100%',
    margin: '0 auto',
    width: '100%',
  };

  return (
    <div className={styles.chartContainer}>
      <button className={styles.backBtn} onClick={() => navigate('/results', { state: location.state })}>
        ← Quay lại
      </button>
      <div className={styles.chartHeader}>
        Thống Kê Khả Năng Có Mây Theo Thời Gian
      </div>
      <div className={styles.chartWrapper} style={wrapperStyle}>
        <Line data={formattedData} options={chartOptions} />
      </div>
      
      <div style={{ textAlign: 'center', marginTop: '30px', paddingBottom: '20px', display: 'flex', flexDirection: 'column', gap: '15px', alignItems: 'center' }}>

        
        <button 
          onClick={() => navigate('/booking')}
          style={{ 
            padding: '14px 28px', 
            background: 'linear-gradient(135deg, #f59e0b, #d97706)', 
            color: '#fff', 
            border: 'none', 
            borderRadius: '50px', 
            cursor: 'pointer', 
            fontSize: '1.1rem', 
            fontWeight: 'bold', 
            boxShadow: '0 4px 15px rgba(245, 158, 11, 0.4)',
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 6px 20px rgba(245, 158, 11, 0.6)'; }}
          onMouseOut={(e) => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 4px 15px rgba(245, 158, 11, 0.4)'; }}
        >
          🏕️ Tìm dịch vụ & tiện ích lưu trú gần điểm săn mây
        </button>
      </div>


    </div>
  );
}
