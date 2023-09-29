from fastapi import FastAPI, HTTPException, Request, Depends
import pika
import logging
import json
import os 
app = FastAPI()
local_ip = os.getenv('local_ip', '10.0.0.1')

QUEUE_NAME = 'nerd-queue'

logging.basicConfig(level=logging.INFO)


def send_to_rabbitmq(payload):
    try:
        credentials = pika.PlainCredentials('nerd', '12345678')
        parameters = pika.ConnectionParameters(local_ip, 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(exchange='nerd', routing_key=QUEUE_NAME, body=json.dumps(payload))
        connection.close()
        logging.info(f'Payload sent to RabbitMQ: {payload}')
    except Exception as e:
        logging.error(f'Error sending payload to RabbitMQ: {str(e)}')


@app.post('/queue', response_model=dict)
async def send_to_queue(request: Request):
    try:
        payload = await request.json()

        # Extract traceparent and tracestate headers
        traceparent = request.headers.get('traceparent')
        tracestate = request.headers.get('tracestate')

        # Add traceparent and tracestate to payload headers
        payload['headers'] = {
            'traceparent': traceparent,
            'tracestate': tracestate
        }

        send_to_rabbitmq(payload)
        logging.info(f'Payload received: {payload}')
        return {
            'status': 200,
            'message': 'Payload sent to nerd-queue',
            'payload': payload
        }
    except Exception as e:
        error_msg = f'Error sending payload to RabbitMQ: {str(e)}'
        logging.error(error_msg)
        return {
            'status': 500,
            'message': error_msg,
            'payload': None
        }



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3004)


