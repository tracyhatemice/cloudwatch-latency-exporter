# CloudWatch-Latency-Exporter

Publish ping latency metric to AWS CloudWatch.

### Usage: 

Clone
```bash
git clone https://github.com/tracyhatemice/cloudwatch-latency-exporter.git
```

### Config

copy ```.env.sample``` to ```.env``` and change the settings.

### Build
```bash
docker build -t cloudwatch-latency-exporter .
```

### Run manually
```bash
docker run --rm -v "$PWD":/app -w /app --env-file .env cloudwatch-latency-exporter
```

### Or as cron job
```
*/1 * * * * docker run --rm -v /home/ubuntu/project/cloudwatch-latency-exporter:/app -w /app --env-file /home/ubuntu/project/cloudwatch-latency-exporter/.env cloudwatch-latency-exporter  >> /dev/null 2>&1
```

### Reference

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/cw-examples.html
