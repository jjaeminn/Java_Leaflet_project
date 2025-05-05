import express from 'express'

const app = express()

app.get('/', (req, res) => {
  res.send('Hello World')
})

app.listen(3000)
// get - 주소창 
// post - 주소창이 아닌 body안에 놓어 보냄 
// callback  function -> 함수 끝나고 그 다음 끝날 함수 표시 \
// 비동기 동기
// 로그인을 하면 아이디 부여 - 거기에 상품 등록 하면 자동 정렬로 묶인다. 
// 먼저 스토어 개설 하고 거기에 차곡 차곡 상품 등록 하는 방식으로 접근해자 
// 위치 등록도 주소 입력 -> 좌표 반환 -> 표시 형식으로 코딩 시작 
