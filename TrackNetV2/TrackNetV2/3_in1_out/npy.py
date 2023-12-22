import numpy as np

data = np.load('/home/porsche/dalhong/TrackNetV2/3_in_1_out/npy_tennis/y_data_1.npy')

# 4D 배열을 2D 배열로 펼치기
reshaped_data = data.reshape(data.shape[0], -1)

# 2D 배열을 텍스트 파일로 저장
np.savetxt("y_data_1_tennis.txt", reshaped_data, fmt='%f', delimiter=',')