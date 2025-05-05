const pool = require('../config/db');

async function initializeDatabase() {
  let connection;
  try {
    connection = await pool.getConnection();
    
    // 데이터베이스 생성
    await connection.query('CREATE DATABASE IF NOT EXISTS flyer_system');
    
    // 데이터베이스 선택
    await connection.query('USE flyer_system');
    
    // 스토어(사용자) 테이블 생성
    await connection.query(`
      CREATE TABLE IF NOT EXISTS stores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        store_name VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // 전단지 테이블 생성
    await connection.query(`
      CREATE TABLE IF NOT EXISTS flyers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        event_type VARCHAR(50),
        event_category VARCHAR(50),
        product_type VARCHAR(50),
        search_keywords VARCHAR(200),
        description TEXT,
        image_url VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    console.log('데이터베이스와 테이블이 초기화되었습니다.');
    return true;
  } catch (error) {
    console.error('데이터베이스 초기화 오류:', error);
    return false;
  } finally {
    if (connection) connection.release();
  }
}

module.exports = { initializeDatabase };