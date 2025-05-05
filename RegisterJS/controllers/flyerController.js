// 전단지 등록 함수
const createFlyer = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const {
        product_name,
        price,
        event_type,
        event_category,
        product_type,
        search_keywords,
        description
      } = req.body;
      
      // 이미지 URL 생성
      let image_url = null;
      if (req.file) {
        const host = req.get('host');
        const protocol = req.protocol;
        image_url = `${protocol}://${host}/uploads/${req.file.filename}`;
      }
      
      // 데이터베이스에 저장
      const flyerData = {
        product_name,
        price,
        event_type,
        event_category,
        product_type,
        search_keywords,
        description,
        image_url
      };
      
      const flyer = await Flyer.create(flyerData);
      
      res.status(201).json({
        success: true,
        message: '전단지가 성공적으로 등록되었습니다.',
        flyer
      });
    } catch (error) {
      console.error('Error:', error);
      res.status(500).json({
        success: false,
        message: '서버 오류가 발생했습니다.'
      });
    }
  };
  
  // 전단지 조회 함수 - 스토어별 필터링 추가
  const getAllFlyers = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const flyers = await Flyer.findAll();
      
      res.status(200).json({
        success: true,
        count: flyers.length,
        data: flyers
      });
    } catch (error) {
      console.error('Error:', error);
      res.status(500).json({
        success: false,
        message: '서버 오류가 발생했습니다.'
      });
    }
  };
  
  // 특정 ID의 전단지 조회
  const getFlyerById = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const id = req.params.id;
      const flyer = await Flyer.findById(id);
      
      if (!flyer) {
        return res.status(404).json({
          success: false,
          message: '해당 ID의 전단지를 찾을 수 없습니다.'
        });
      }
      
      res.status(200).json({
        success: true,
        data: flyer
      });
    } catch (error) {
      console.error('Error:', error);
      res.status(500).json({
        success: false,
        message: '서버 오류가 발생했습니다.'
      });
    }
  };
  
  // 전단지 수정
  const updateFlyer = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const id = req.params.id;
      
      // 기존 전단지 정보 조회
      const existingFlyer = await Flyer.findById(id);
      
      if (!existingFlyer) {
        return res.status(404).json({
          success: false,
          message: '해당 ID의 전단지를 찾을 수 없습니다.'
        });
      }
      
      // 요청에서 새 데이터 추출
      const {
        product_name,
        price,
        event_type,
        event_category,
        product_type,
        search_keywords,
        description
      } = req.body;
      
      // 이미지 업로드 처리
      let image_url = existingFlyer.image_url; // 기본값으로 기존 이미지 URL 사용
      
      if (req.file) {
        const host = req.get('host');
        const protocol = req.protocol;
        image_url = `${protocol}://${host}/uploads/${req.file.filename}`;
      }
      
      // 데이터베이스에 업데이트
      const flyerData = {
        id,
        product_name: product_name || existingFlyer.product_name,
        price: price || existingFlyer.price,
        event_type: event_type || existingFlyer.event_type,
        event_category: event_category || existingFlyer.event_category,
        product_type: product_type || existingFlyer.product_type,
        search_keywords: search_keywords || existingFlyer.search_keywords,
        description: description || existingFlyer.description,
        image_url
      };
      
      const updatedFlyer = await Flyer.update(flyerData);
      
      res.status(200).json({
        success: true,
        message: '전단지가 성공적으로 수정되었습니다.',
        data: updatedFlyer
      });
    } catch (error) {
      console.error('Error:', error);
      res.status(500).json({
        success: false,
        message: '서버 오류가 발생했습니다.'
      });
    }
  };
  
  // 전단지 삭제
  const deleteFlyer = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const id = req.params.id;
      
      // 기존 전단지 정보 조회
      const existingFlyer = await Flyer.findById(id);
      
      if (!existingFlyer) {
        return res.status(404).json({
          success: false,
          message: '해당 ID의 전단지를 찾을 수 없습니다.'
        });
      }
      
      // 데이터베이스에서 삭제
      await Flyer.delete(id);
      
      res.status(200).json({
        success: true,
        message: '전단지가 성공적으로 삭제되었습니다.'
      });
    } catch (error) {
      console.error('Error:', error);
      res.status(500).json({
        success: false,
        message: '서버 오류가 발생했습니다.'
      });
    }
  };
  
  // 내 전단지 조회 (로그인한 스토어만)
  const getMyFlyers = async (req, res) => {
    try {
      const isInitialized = await initializeDatabase();
      if (!isInitialized) {
        return res.status(500).json({
          success: false,
          message: '데이터베이스 초기화에 실패했습니다.'
        });
      }
      
      const store_id = req.store.id;
      const flyers = await Flyer.findAll(store_id);
      
      res.status(200).json({
        success: true,
        count: flyers.length,
        data: flyers
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
    createFlyer,
    getAllFlyers,
    getFlyerById,
    updateFlyer,
    deleteFlyer,
    getMyFlyers
  };