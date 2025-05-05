const pool = require('../config/db');
const bcrypt = require('bcrypt');

class Store {
  // 회원가입
  static async create(storeData) {
    const connection = await pool.getConnection();
    try {
      await connection.query('USE flyer_system');
      
      // 비밀번호 해싱
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(storeData.password, salt);
      
      const [result] = await connection.execute(
        `INSERT INTO stores 
         (username, password, store_name, email, phone) 
         VALUES (?, ?, ?, ?, ?)`,
        [
          storeData.username,
          hashedPassword,
          storeData.store_name,
          storeData.email,
          storeData.phone
        ]
      );
      
      return { id: result.insertId, ...storeData, password: undefined };
    } finally {
      connection.release();
    }
  }
  
  // 사용자 이름으로 검색
  static async findByUsername(username) {
    const connection = await pool.getConnection();
    try {
      await connection.query('USE flyer_system');
      
      const [rows] = await connection.execute(
        'SELECT * FROM stores WHERE username = ?',
        [username]
      );
      
      return rows.length ? rows[0] : null;
    } finally {
      connection.release();
    }
  }
  
  // ID로 검색
  static async findById(id) {
    const connection = await pool.getConnection();
    try {
      await connection.query('USE flyer_system');
      
      const [rows] = await connection.execute(
        'SELECT id, username, store_name, email, phone, created_at FROM stores WHERE id = ?',
        [id]
      );
      
      return rows.length ? rows[0] : null;
    } finally {
      connection.release();
    }
  }
}

module.exports = Store;