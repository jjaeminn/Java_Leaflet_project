const express = require('express');
const cors = require('cors');
const path = require('path');
const flyerRoutes = require('./routes/api/flyers');
const authRoutes = require('./routes/api/auth');  // 추가

const app = express();

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));
app.use(express.static('public'));

// 라우트 설정
app.use('/api/flyers', flyerRoutes);
app.use('/api/auth', authRoutes);  // 추가된 인증 라우터

// 기본 라우트
app.get('/api', (req, res) => {
  res.send('전단지 등록 API 서버가 실행 중입니다.');
});

module.exports = app;