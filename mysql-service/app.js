const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;
const localIp = process.env.local_ip || '10.0.0.1';

const connection = mysql.createConnection({
  host: localIp,
  port: '3306',
  user: 'root',
  password: '12345678',
  database: 'nerd',
});

connection.connect((err) => {
  if (err) {
    console.error('Error connecting to database:', err);
    return;
  }
  console.log('Connected to MySQL database');
});

app.use(bodyParser.json());
app.use(cors());

app.post('/save', (req, res) => {
  const payload = req.body;

  const sql = 'INSERT INTO nerd (nombre, email, edad) VALUES (?, ?, ?)';
  const values = [payload.name, payload.email, payload.age];

  connection.query(sql, values, (err, result) => {
    if (err) {
      console.error('Error saving payload:', err);
      res.status(500).json({
        status: 500,
        message: 'Internal Server Error',
        payload: payload
      });
      return;
    }
    console.log('Payload saved successfully');
    res.status(200).json({
      status: 200,
      message: 'Payload saved successfully',
      payload: payload
    });
  });
});

app.listen(PORT, () => {
  console.log(`MySQL Service running on port ${PORT}`);
});

module.exports = connection;
