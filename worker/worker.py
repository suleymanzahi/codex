import pika, redis
import time,json, os, shutil, subprocess, sys, sandbox


print("Worker startup...:", )

def create_files(job):
    files = job["files"]
    os.mkdir("./tmp")
    for filename, code in files.items():
        file = open(f"./tmp/{filename}", mode='w')
        file.write(code)

def callback(ch, method, properties, body):
    job = body.decode()
    print(f"[x] Received {job}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    job = json.loads(job)
    job_id = job["job_id"]
    print("Job id:", job_id)
    entry_file = job["entry"]
    create_files(job)
    out, err = sandbox.run_sandbox(f"./tmp/{entry_file}")
    res = out + err
    shutil.rmtree("./tmp")
    print("Code execution:", res)
    r.publish(job_id, res)

while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="queue", port=5672)
        )
        break
    except pika.exceptions.AMQPConnectionError:
        print("RabbitMQ not ready, retrying...")
        time.sleep(3)
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
r = redis.Redis(host="pubsub")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()