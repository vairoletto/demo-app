const express = require('express');
const bodyParser = require('body-parser');
const mq = require('./rabbitmq'); // Adjust the path as needed
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3003;

app.use(bodyParser.json());
app.use(cors());

app.post('/queue', (req, res) => {
  console.log(`Received Message`);
  const payload = req.body;
  const exchange = 'nerd'; // Adjust the exchange name as needed
  const routingKey = 'nerd-queue'; // Adjust the routing key as needed

  mq.publish(exchange, routingKey, JSON.stringify(payload), (publishError) => {
    if (publishError) {
      console.error('Error sending payload to RabbitMQ:', publishError);
      res.status(500).json({
        status: 500,
        message: 'Internal Server Error',
        payload: payload
      });
    } else {
      res.status(200).json({
        status: 200,
        message: 'Payload sent to RabbitMQ',
        payload: payload
      });
    }
  });
});


app.listen(PORT, () => {
  console.log(`RabbitMQ Producer Service running on port ${PORT}`);
});

