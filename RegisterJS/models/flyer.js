const express = require('express');
const router = express.Router();
const upload = require('../../middlewares/upload');
// const { protect } = require('../../middlewares/auth'); // 이 줄을 주석 처리

const {
  createFlyer,
  getAllFlyers,
  getFlyerById,
  updateFlyer,
  deleteFlyer
} = require('../../controllers/flyerController');

// 모든 라우트에서 protect 미들웨어 제거
router.get('/', getAllFlyers);
router.get('/:id', getFlyerById);
router.post('/', upload.single('image'), createFlyer); // protect 제거
router.put('/:id', upload.single('image'), updateFlyer); // protect 제거
router.delete('/:id', deleteFlyer); // protect 제거

module.exports = router;