from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import pika
import logging
import json
import os
import httpx
import newrelic.agent


app = FastAPI()
local_ip = os.getenv('local_ip', '10.0.0.1')

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8888",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


QUEUE_NAME = 'nerd-queue'

logging.basicConfig(level=logging.INFO)



def receive_from_rabbitmq():
    credentials = pika.PlainCredentials('nerd', '12345678')
    parameters = pika.ConnectionParameters(local_ip, 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    method_frame, header_frame, payload = channel.basic_get(queue = QUEUE_NAME)     
    logging.info(f'Method is: {str(method_frame)}')   
    if method_frame is None:
        connection.close()
        return 'EMPTY'
    else:
        #add custom attribute
        newrelic.agent.add_custom_attribute('fromsource', QUEUE_NAME)            
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close() 
        return payload

async def post_to_submit(payload, port, path, traceparent, tracestate):
    try:
        payload['port'] = port
        payload['path'] = path
        
        url = f"http://{local_ip}:3000/submit"
        headers = {
            'Content-Type': 'application/json'
        }

        # Add traceparent and tracestate if available
        if traceparent is not None:
            headers['traceparent'] = traceparent
        if tracestate is not None:
            headers['tracestate'] = tracestate


        response = httpx.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f'Error posting payload to submit: {str(e)} URL: {str(url)}')
        return e

@app.get('/queue', response_model=dict)
async def get_from_queue():
    try:
        result = receive_from_rabbitmq()
        if result == 'EMPTY':
            return {
                'status': 204,
                'message': 'No message available in the queue',
                'payload': None
            }
        else:
            payload = json.loads(result.decode('utf-8'))
            return {
                'status': 200,
                'message': 'Payload received from nerd-queue',
                'payload': payload
            }
    except Exception as e:
        error_msg = f'Error retrieving payload from RabbitMQ: {str(e)}'
        logging.error(error_msg)
        return {
            'status': 500,
            'message': error_msg,
            'payload': None
        }


@app.get('/save', response_model=dict)
async def save_and_get_from_queue():
    try:
        result = receive_from_rabbitmq()
        if result == 'EMPTY':
            return {
                'status': 204,
                'message': 'No message available in the queue',
                'payload': None
            }
        else:
            payload = json.loads(result.decode('utf-8'))
            traceparent = None
            tracestate = None

            if 'headers' in payload:
                traceparent = payload['headers'].get('traceparent')
                tracestate = payload['headers'].get('tracestate')


            # Add code to post payload to http://localhost:3000/submit
            submit_response = await post_to_submit(payload, '3001', '/save', traceparent, tracestate)

            return {
                'status': 200,
                'message': 'Payload received and saved to MySQL',
                'payload': payload
            }
    except Exception as e:
        error_msg = f'Error retrieving payload from RabbitMQ: {str(e)}'
        logging.error(error_msg)
        return {
            'status': 500,
            'message': error_msg,
            'payload': None
        }





if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3005)


