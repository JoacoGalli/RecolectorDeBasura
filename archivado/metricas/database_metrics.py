from datetime import datetime

from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class Send_Metrics():
    self.url = 'http://localhost:8086'
    self.token = 'nmxoYaxoczxogpv6LnTmvxrKyxiMASQ_XLMrUvYKGqJDB8KUhLcllCkFQN-wLcEZHJ9BBfcsmFign7Ri0PIpiQ=='
    self.org = 'IRF'
    self.bucket = 'test_metrics'

    def send_metrics

with InfluxDBClient(url=url, token=token, org=org) as client:
    p = Point("Llenado del contenedor") \
        .tag("Contenedor", "1") \
        .field("llenado", 50) \
        .time(datetime.utcnow(), WritePrecision.MS)

    with client.write_api(write_options=SYNCHRONOUS) as write_api:
        write_api.write(bucket=bucket, record=p)


