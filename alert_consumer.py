import json, smtplib
import pika
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

def _format_addr(s):
	name, addr = parseaddr(s)
	return formataddr((Header(name, 'utf-8').encode(), addr))

def send_mail(recipients, subject, message):
	headers = ("From: %s\r\nTo: \r\nDate: \r\n" +\
		"Subject: %s\r\n\r\n") % ("1442893553@qq.com",subject)

	msg = MIMEText(str(message), "plain", "utf-8")
	msg["From"] = _format_addr("System <15292188037@163.com>")
	msg["To"] = _format_addr("Admin <%s>" %recipients)
	msg["Subject"] = Header(subject, "utf-8").encode()	

	smtp_server = smtplib.SMTP()
	smtp_server.connect("smtp.163.com", 25)
	smtp_server.login("15292188037@163.com", "qp7896541230")
	smtp_server.sendmail("15292188037@163.com",
			recipients,
			msg.as_string())
	smtp_server.close()

def critical_notify(channel, method, header, body):
	EMAIL_RECIPS = ["517904148@qq.com",]
	message = json.loads(body)
	send_mail(EMAIL_RECIPS, "CRITICAL ALERT", message)
	print("Sent alert via e-mail! Alert Text: %s " + \
		"Recipients: %s") % (str(message), str(EMAIL_RECIPS))
	channel.basic_ack(delivery_tag=method.delivery_tag)

def rate_limit_notify(channel, method, header, body):
	EMAIL_RECIPS = ["3235538352@qq.com",]
	message = json.loads(body)
	send_mail(EMAIL_RECIPS, "RATE LIMIT ALERT!", message)
	print("Sent alert via e-mail! Alert Text %s " +\
		"Recipients: %s") % (str(message), str(EMAIL_RECIPS))
	channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
	AMQP_SERVER = "localhost"
	AMQP_USER = "guest"
	AMQP_PASS = "guest"
	AMQP_VHOST = "/"
	AMQP_EXCHANGE = "alerts"

	creds_broker = pika.PlainCredentials(AMQP_USER, AMQP_PASS)
	conn_params = pika.ConnectionParameters(AMQP_SERVER, virtual_host= AMQP_VHOST,
						credentials = creds_broker)
	conn_broker = pika.BlockingConnection(conn_params)
	channel = conn_broker.channel()
	channel.exchange_declare(exchange=AMQP_EXCHANGE,
				type="topic",
				auto_delete=False)
	channel.queue_declare(queue="critical", auto_delete=False)
	channel.queue_bind(queue="critical",
			exchange="alerts",
			routing_key="critical.*")
	channel.queue_declare(queue="rate_limit", auto_delete=False)
	channel.queue_bind(queue="rate_limit",
			exchange="alerts",
			routing_key="*.rate_limit")
	channel.basic_consume(critical_notify,
			queue="critical",
			no_ack=False,
			consumer_tag="critical")
	channel.basic_consume(rate_limit_notify,
			queue="rate_limit",
			no_ack=False,
			consumer_tag="rate_limit")

	print "Ready for alerts!"
	channel.start_consuming()
