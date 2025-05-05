const jwt = require('jsonwebtoken');
// Store 모델 불러오기 부분 제거하고 임시 함수로 대체

// JWT 시크릿 키 (실제로는 환경 변수로 관리)
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_key';

// 임시 사용자 정보 찾기 함수
const findUserById = (id) => {
  return Promise.resolve({ id, username: 'temp_user' });
};

// 인증 확인 미들웨어
const protect = async (req, res, next) => {
  let token;
  
  // Authorization 헤더에서 토큰 확인
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    try {
      // Bearer 토큰에서 실제 토큰 추출
      token = req.headers.authorization.split(' ')[1];
      
      // 토큰 검증
      const decoded = jwt.verify(token, JWT_SECRET);
      
      // 사용자 정보 가져오기
      req.store = await findUserById(decoded.id);
      
      next();
    } catch (error) {
      console.error('인증 오류:', error);
      res.status(401).json({
        success: false,
        message: '인증되지 않았습니다. 유효하지 않은 토큰입니다.'
      });
    }
  }
  
  if (!token) {
    res.status(401).json({
      success: false,
      message: '인증되지 않았습니다. 토큰이 없습니다.'
    });
  }
};

module.exports = { protect };