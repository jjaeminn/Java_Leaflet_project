const Store = require('../models/store');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { initializeDatabase } = require('../utils/database');

// JWT 시크릿 키 (실제로는 환경 변수로 관리)
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_key';

// 회원가입
const register = async (req, res) => {
  try {
    const isInitialized = await initializeDatabase();
    if (!isInitialized) {
      return res.status(500).json({
        success: false,
        message: '데이터베이스 초기화에 실패했습니다.'
      });
    }
    
    const { username, password, store_name, email, phone } = req.body;
    
    // 필수 필드 검증
    if (!username || !password || !store_name) {
      return res.status(400).json({
        success: false,
        message: '사용자명, 비밀번호, 스토어명은 필수 입력 사항입니다.'
      });
    }
    
    // 사용자 이름 중복 확인
    const existingUser = await Store.findByUsername(username);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: '이미 사용 중인 사용자명입니다.'
      });
    }
    
    // 새 스토어 생성
    const storeData = { username, password, store_name, email, phone };
    const newStore = await Store.create(storeData);
    
    res.status(201).json({
      success: true,
      message: '회원가입에 성공했습니다.',
      store: newStore
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      message: '서버 오류가 발생했습니다.'
    });
  }
};

// 로그인
const login = async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // 사용자 찾기
    const store = await Store.findByUsername(username);
    if (!store) {
      return res.status(401).json({
        success: false,
        message: '사용자명 또는 비밀번호가 올바르지 않습니다.'
      });
    }
    
    // 비밀번호 검증
    const isMatch = await bcrypt.compare(password, store.password);
    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: '사용자명 또는 비밀번호가 올바르지 않습니다.'
      });
    }
    
    // JWT 토큰 생성
    const token = jwt.sign(
      { id: store.id, username: store.username },
      JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.status(200).json({
      success: true,
      message: '로그인 성공',
      token,
      store: {
        id: store.id,
        username: store.username,
        store_name: store.store_name
      }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      success: false,
      message: '서버 오류가 발생했습니다.'
    });
  }
};

module.exports = {
  register,
  login
};