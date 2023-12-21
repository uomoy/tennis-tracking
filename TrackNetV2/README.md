# TrackNetV2

## Configuration Setting
기존의 Yolo에서 공의 tracking 성능이 안나올 경우를 대비하여, 부가적으로 공의 tracking에만 집중된 TrackNet 구현을 진행하기로 하였다. 
TrackNet은 tiny and fast 물체에 대한 tracking을 하기 위한 heatmap기반의 deep learning network이다. 
초기에는 TrackNetV1의 구현 및 훈련을 진행하였다. 하지만 TrackNetV1의 경우 CPU에 특화된 환경으로, 본 프로젝트에서 사용한 3090 GPU와는 호환이 잘 되지 않았다. 
이에, TrackNetV2로 모델로 변경하여 실험을 진행하였다. 
TrackNetV2는 기존의 V1에서 성능 향상을 위한 방법이 여러 적용되었으며(loss function 변경, 데이터셋 처리 방식 변경, 모델에 skip connection 추가 등), 이미지 처리 속도가 V1에 비해 최대 15배 정도 향상되는 결과를 가져온다.


<br>
<br>

## Dataset
위의 YOLOv8 & ByteTrack과 마찬가지로 TrackNet[1] 학습에 사용된 테니스공 데이터셋을 사용했다 (약 2만장).
기존의 TrackNetV1은 이미지 한장씩 읽어서 처리하는 반면, TrackNetV2는 처리속도를 빠르게 하기위해 image를 npy파일로 변환하여 처리한다. 
따라서 기존의 TrackNetV1에서 사용한 데이터 셋을 npy파일로 변경하여 dataset을 구성하였다. train과 validation의 비율은 8:2이다.


<br>
<br>

## Progression
### Training
처음에는 논문과 동일한 실험환경으로 진행을 하였으며 메모리 이슈로 batch사이즈만 3에서 1로 변경하였다. 
하지만 논문에서는 epoch2에서도 validation set의 confusion matrix를 확인하면 훈련이 되는 것을 알 수 있는데, 이와 달리 epoch 30이 되어도 훈련이 되지 않았다. 
이를 해결하기 위해 실험 환경을 변경하며 실험해 본 결과, 크게 2가지의 수정사항이 성공하였다. 
1) 논문에서 사용된 optimizer는 Adadelta인데, 이를 Adam으로 변경하였다. 
2) learning rate를 1에서 0.001로 변경하였다.
<br>
적은 epoch에도 빠르게 학습이 진행되는 결과를 얻었다.

### Layer Pruning
TrackNetV2를 학습하여 test해본 결과, 기존의 논문과 비슷한 성능을 보였다. 하지만 처리 속도에서는 많이 떨어지는 경향을 보인다(12FPS -> 6FPS). 
이는 현재 짜여진 코드와 GPU의 호환성 문제라고 생각된다. 이를 해결하기는 어려울 것으로 판단되어, 기존의 모델에 대해 경량화를 진행해보았다. 
기존의 모델 parameter는 약 11M 개로 공 하나만을 detection하는데 필요 이상으로 깊은 모델인 것으로 판단하였다. 
따라서 기존의 모델에서 layer를 몇 개 줄여서 위와 동일한 환경으로 학습을 진행하였다(parameter 약 7M개). 
실험 결과, 기존의 모델과 성능차이는 크게 변하지 않았으며 이미지 처리속도 부분에 있어서 미소한 성능 향상을 보였다(6FPS -> 7FPS). 
하지만 아직도 실시간 처리에는 어려움이 있어 보인다. 


<br>
<br>


## Evaluation
50 epoch 중에서 가장 성능이 좋은 epoch 46 모델을 이용하여 evaluation을 진행하였다.

YOLOv8 & ByteTrack와 마찬가지로 약 13초의 HARD, GRASS, CLAY코트의 세가지 영상으로 test을 진행하였다. 
공의 좌표값으로 t 거리만큼 떨어진 거리 안에서 detection되었으면 detection 되었다고 판단한다. 

<br>
<br>

## Performance
### Ball Detection

- 사진 추가
  
Length: 영상의 프레임 수
TP: 정답값과 예측값의 거리가 t 이하일 경우
TN: 정답값에 공이 없는 것을 잘 예측한 경우
FP1: 정답값과 예측값의 거리가 t 초과일 경우
FP2: 정답값에 공이 없는데 예측한 경우
FN: 정답값에 공이 있는데 예측하지 못한 경우
Acc., Prec., Recall: 각각 Accuracy, Precision, Recall

기존의 TrackNetV1에 비해 V2를 사용하여 detection을 진행한 결과, 공의 속도가 빠른 부분, 공이 bounce되는 부분에서의 detection이 향상된 것으로 보인다.
하지만 기존 논문의 결과와 비교했을 때 Accuracy, Precision, Recall 모두 조금씩 줄어든 것을 확인할 수 있다. 
이는 기존의 V1 모델에서는 epoch를 500까지 진행하였기 때문에, 현재 돌린 46 epoch로는 학습이 덜 되었기 때문이라고 판단된다. 
더 많은 epoch로 학습한다면 해결될 것으로 판단되지만 GPU나 메모리 이슈로 인해 추가 진행은 하지 못했다.
다른 문제점은 fps가 기존의 논문에서는 12fps정도가 나온다고 나와있지만, 그의 절반인 6fps 정도의 성능밖에 내지 못하고 있다는 점이다. 
이는 RTX 3090과 tensorflow 1.x 버전의 호환성 문제라고 생각되지만 정확한 원인은 찾지 못한 상황이다. 
처리 속도를 더 높이기 위해 모델을 경량화하는 등의 실험을 진행해 보았지만 fps가 1정도 밖에 증가하지 않았다. 

### Ball Tracking
TrackNet은 Ball을 detection한 후에, detection된 점들을 이어서 Tracking을 하기 때문에, 실질적으로 Tracking이라고 볼 수 없다.
따라서 Tracking에 대한 성능 평가 척도를 적용할 수 없다. 
따라서 위의 test dataset에서 ball을 detection한 후에, 이들을 이어 붙여 공의 궤적을 그려서 공을 잘 추적하고 있는지 판단한다.
세 test영상에 대해 공의 궤적을 그려본 결과, 공을 잘 추적하고 있다고 판단된다.
특히 TrackNetV1과 달리 공이 매우 빠른 부분, bounce되는 부분에서도 공을 잘 추적하고 있는 것으로 보인다. 

### Characteristics
TrackNet의 주요 특징으로는 input data로 3장의 sequence 데이터를 사용해서 공의 궤적을 추적하는데 있다. 
3장의 이미지를 입력으로 넣기 때문에, 공이 사람에 의해 가려지거나 코트에 의해 가려지는 부분에 대해서도 공을 추적할 수 있다는 장점이 있다.
하지만 그렇기 때문에 속도에 있어서 취약점이 존재한다. 
TrackNetV2는 TrackNet V1에서 loss function, 데이터셋 처리 방식등을 변경하고 모델에 skip connection 추가하여 tennis ball tracking의 성능을 올렸으며 속도도 TrackNetV1에 비해 비약적으로 향상됐다. 
빠르게 변화하고, blur한 이미지를 detection하는데 있어서 기존의 V1모델에 비해 훨씬 좋은 성능을 보였다.
- 사진 추가


<br>
<br>

