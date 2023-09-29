const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3000;
const localIp = process.env.local_ip || '127.0.0.1';

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cors());

app.post('/submit', (req, res) => {
  const { name, email, age, port, path } = req.body;

  const data = JSON.stringify({
    name: name,
    email: email,
    age: age
  });

  const options = {
    hostname: localIp,
    port: port,
    path: path,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  const request = http.request(options, (response) => {
    let responseData = '';

    response.on('data', (chunk) => {
      responseData += chunk;
    });

    response.on('end', () => {
      try {
        console.log('Response data:', responseData);
        responseData = JSON.parse(responseData);

        // Include payload in the response
        const updatedResponse = {
          status: responseData.status,
          message: responseData.message,
          payload: responseData.payload
        };

        res.json(updatedResponse);
      } catch (error) {
        console.error('Error parsing JSON:', error);
        res.status(500).send('Internal Server Error');
      }
    });
  });

  request.on('error', (error) => {
    console.error('Error making request:', error);
    res.status(500).send('Internal Server Error');
  });

  request.write(data);
  request.end();
});

app.listen(PORT, () => {
  console.log(`Frontend Web App running on port ${PORT}`);
});

