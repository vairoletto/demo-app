const amqp = require('amqplib/callback_api');
const ON_DEATH = require('death');

const localIp = process.env.local_ip || '10.0.0.1';
const url = `amqp://nerd:12345678@${localIp}:5672`;

const publish = (exchange, routerKey, msgPayload, callback) => {

    amqp.connect(url, (connectError, connection) => {

        if (connectError) {
            callback(connectError);
            return;
        }

        connection.createChannel((channelError, channel) => {

            if (channelError) {
                callback(channelError);
                return;
            }

            channel.assertExchange(exchange, 'direct', {durable: true});
            channel.publish(exchange, routerKey, Buffer.from(msgPayload));

            console.log(`\n[X] Send: ${routerKey}`);

            callback(null, 'Message sent successfully'); // Call the callback with no error
        });

        ON_DEATH((signal, error) => {
            console.log("\nClear...");
            setTimeout(() => {
                connection.close();
                process.emit(0);
            }, 500);
        });
    });
}

module.exports = { publish };
