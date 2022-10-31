"""
utility script that generates valid pgfplots data from the raw observables data
"""


DATA_LOG_PATH = 'D:/temp/' + 'CS3_SendVariable_100ms_JoinNoFilter' + '/'


filepaths = [DATA_LOG_PATH + f for f in ('delay.log', 'button.log', 'co2.log', 'dht11.log', 'rotary_encoder.log', 'ultrasonic.log', 'total.log')]
converted_filepaths = [DATA_LOG_PATH + f for f in ('delay_converted.log', 'button_converted.log', 'co2_converted.log', 'dht11_converted.log', 'rotary_encoder_converted.log', 'ultrasonic_converted.log', 'total_converted.log')]

minimum = float('inf')

for fp in filepaths:
    with open(fp, mode='r') as file:
        content = file.read()
        first_ts = content.split('(')[1].split(',')[0]

        minimum = min(minimum, float(first_ts))

for idx, fp in enumerate(filepaths):
    with open(fp, mode='r') as f:
        data = f.read()

    tuples = data.replace(')', '(').replace('((', '(').split('(')

    converted = ''
    first_ts = minimum
    for t in (i for i in tuples if i):
        ts, val = t.split(',')

        converted += '{} {}\n'.format(round((float(ts)-first_ts)/1000), val)

    with open(converted_filepaths[idx], mode='w') as f:
        f.write(converted)
