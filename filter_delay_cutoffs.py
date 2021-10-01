
DATA_PATHS = [
    'CS1_SendFixed_50ms_JoinDupFilter',
    'CS1_SendFixed_50ms_JoinNoFilter',
    'CS1_SendFixed_100ms_JoinDupFilter',
    'CS1_SendFixed_100ms_JoinNoFilter',
    'CS1_SendVariable_50ms_JoinDupFilter',
    'CS1_SendVariable_50ms_JoinNoFilter',
    'CS1_SendVariable_100ms_JoinDupFilter',
    'CS1_SendVariable_100ms_JoinNoFilter',
    'CS2_SendFixed_50ms_JoinDupFilter',
    'CS2_SendFixed_50ms_JoinNoFilter',
    'CS2_SendFixed_100ms_JoinDupFilter',
    'CS2_SendFixed_100ms_JoinNoFilter',
    'CS2_SendVariable_50ms_JoinDupFilter',
    'CS2_SendVariable_50ms_JoinNoFilter',
    'CS2_SendVariable_100ms_JoinDupFilter',
    'CS2_SendVariable_100ms_JoinNoFilter',
]

filepaths = ['D:/temp/' + d + '/delay_converted.log' for d in DATA_PATHS]

converted_filepaths = ['D:/temp/' + d + '/delay_converted_filtered.log' for d in DATA_PATHS]


for idx, fp in enumerate(filepaths):

    with open(fp, mode='r') as file:
        content = file.readlines()

    filtered_content = filter(lambda x: int(x.split(' ')[1]) < 1000, content)

    with open(converted_filepaths[idx], mode='w') as file:
        file.writelines(filtered_content)
