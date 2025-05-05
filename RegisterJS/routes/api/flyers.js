const express = require('express');
const router = express.Router();
const upload = require('../../middlewares/upload');
const { protect } = require('../../middlewares/auth');
const {
  createFlyer,
  getAllFlyers,
  getFlyerById,
  updateFlyer,
  deleteFlyer,
  getMyFlyers
} = require('../../controllers/flyerController');

// 공개 라우트
router.get('/me/flyers', protect, getMyFlyers);  // 또는 다른 라우트          // 모든/특정 스토어 전단지 조회 (쿼리로 필터링)
router.get('/:id', getFlyerById);          // 특정 ID의 전단지 조회

// 보호된 라우트 (로그인 필요)
router.post('/', protect, upload.single('image'), createFlyer);    // 전단지 등록
router.get('/me/flyers', protect, getMyFlyers);                    // 내 전단지 조회
router.put('/:id', protect, upload.single('image'), updateFlyer);  // 전단지 수정
router.delete('/:id', protect, deleteFlyer);                       // 전단지 삭제

module.exports = router;