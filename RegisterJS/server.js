
require('dotenv').config();
const app = require('./app');
const PORT = process.env.PORT || 3001; // 데이터베이스 비밀번호, 포트 설정 분리 관리 목적 

app.listen(PORT, () => {
  console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
}); // 포트가 listen이 되어야지만 앱이 실행 가능 

// port = 세부적으로 들어 올 수 있는 입구 