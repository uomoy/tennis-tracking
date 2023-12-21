# tennis-tracking
tennis ball &amp; players tracking with various models

# YOLOv8-ByteTrack

최근 스포츠 분야에서의 AI 활용 사례가 증가하고 있다. 특히 경기나 훈련 영상에 컴퓨터 비전 기술을 적용하여 경기 내용 분석 및 선수 훈련 등에 활용하는 움직임이 늘고 있다. 선수나 심판과 같은 사람들에 대한 detection 및 tracking은 잘 수행해내지만, 공과 같이 작고 빠른 물체들에 대한 성능은 비교적 낮은 편이다. 작고 빠른 물체에 대한 detection 및 tracking을 향상시키면서 스포츠 영상을 실시간(real-time)으로 detection 및 tracking이 가능하다면 경기 내용 분석 및 선수 훈련에 더 잘 활용할 수 있을 것으로 보인다.

## Summary
비교적 카메라 움직임이 적은 테니스 영상에서 공 및 선수 등의 객체에 대하여 detection 및 tracking을 수행한다. 기존의 실시간 object detection에서 사용되는 YOLO의 경우 테니스 공과 같이 작고 빠르게 움직이는 물체에 대한 detection의 성능은 낮은 편이다. 또한 YOLO뿐만 아니라 다양한 detection 모델들이 존재하는데, YOLOv8 & ByteTrack과 TrackNetV2를 구현 및 실행해보면서 빠르고 작은 물체에 대한 detection에 좋은 모델 및 기법을 찾는다. 해당 방법들을 이용하여 우선적으로 detection 성능을 올린 뒤, tracking에서 성능을 향상시키기 위해 kalman filter 및 tracking algorithm을 적절히 조절하는 등의 기법을 사용한다. 

## Goal
- 테니스 중계 영상에 대한 object tracking에서 small object인 테니스공에 대한 detection performance는 사람 추적에 비해 비교적 낮은 문제 존재. 특히 real-time일수록 두드러짐.
-> 테니스 중계 영상에서의 공과 사람에 대한 검출 및 추적에 대한 성능 향상(특히 공)
- TrackNet에서 공이 bounce되는 부분이나, 서브를 하는 경우와 같이 공이 매우 빠른 경우에는 detection의 성능이 떨어지는 문제와 라켓이나 사람, 코트의 경계선과 같은 곳에서 blur가 일어나는 경우에도 성능 하락이 발생하는 문제 존재.
-> TrackNetV2 구현을 통해 TrackNet에서의 위 문제 및 낮은 image processing 속도 향상 
- YOLO에서 blur되고 background에 occlusion된 공을 높은 정확도로 검출 + tracking에서 빠르고 작은 물체에 대한 성능 향상 + 복잡도가 작은 모델(YOLOv8-nano model)을 이용해 real-time으로 추론
- 선수 검출 및 추적에서 심판, 볼보이, 관중 등 비선수에 대한 오분류 최소화


## Models
- 1. YOLOv8과 ByteTrack을 이용한 트래킹
  2. TrackNetV2를 이용한 트래킹

## Dataset
- 총 13,027장의 HD(1280*720) resolution 데이터셋
  - [TrackNet](https://nol.cs.nctu.edu.tw:234/open-source/TrackNet)의 총 19,842장의 학습 데이터 중 가시성 수준이 ‘공이 쉽게 식별됨’인 17,632장을 일차적으로 추출 후, 무작위로 25%를 샘플링한 4,407장의 이미지에 선수를 레이블링하여 학습에 사용.
  - 2023년에 진행된 메이저 대회(윔블던, 호주 오픈, US 오픈, 프랑스 오픈) 경기 영상 프레임 각 3,001, 1,500, 1,499, 2,620장에 공과 선수를 레이블링하여 사용.
<br>

- 테니스공이 타이트한 bounding box로 레이블링될 경우, 빠른 속도에 의해 blur되고 왜곡된 공을 cover하지 못하므로 여유로운 크기로 레이블링했다. (HD 기준 35px * 35px)
- 공의 레이블링 과정에서 공이 보이지 않을 정도로 heavy(full) occlusion이 일어난 경우에는 공의 annotation은 건너뛰고 선수의 annotation만 추가했다.
- 각 데이터는 코트 종류, 서브 포지션, 스트로크 종류 등을 균형적으로 고려하여 선별했다.

<br>  
<br> 

## Detector Training
- 초기에 YOLOv4-tiny 모델을 이용하여 훈련시켰으나 tracker와의 결합 및 시각화의 용이성, 향상된 성능을 고려하여 YOLOv8로 다시 학습하였다.
- Real-time tracking을 추구하기 위해 3.2M개의 파라미터를 가진 [Ultralytics](https://github.com/ultralytics/ultralytics)의 YOLOv8n 모델을 선택하였다.
- 13,027장에서 약 10%(1,301)를 validation set, 나머지 90%(11,726)를 training set으로 200 epoch 훈련시켰다.
- 훈련 시의 input image size는 640이고, lr, momentum 등의 하이퍼파라미터는 default value를 사용했다.
<br>

- 훈련 결과, validation set에 대한 confusion matrix는 다음과 같다. <p align="center"><img src="https://github.com/uomoy/tennis-tracking/assets/55055376/5a7d01ed-aa81-4250-afa0-81f23c980dde"></p> 
- mAP50, mAP50-95는 각각 0.986, 0.789로 측정되었다.

## Tracking
- 학습된 detector(YOLOv8n)와 tracker(ByteTrack)는 ultralytics 패키지의 track 메소드를 이용해 간단하게 결합했다.
- ByteTrack 추적 알고리즘을 수정 없이 적용시킨 결과 테니스공의 추적에서 fragmentation 및 ID switching이 잦고, 많은 tracklet을 생성하는 문제가 있었다.
  - update 과정에서 이전 프레임으로부터 예측된 공의 위치와 현재 프레임에서 검출된 공의 위치 사이의 거리가 멀어 IOU가 낮게 계산되었고, 이 때문에 동일한 공임에도 linear assignment에서 unmatched 되는 결과가 많이 발생했다.
  - 해당 문제점은 ByteTrack의 update 메소드의 entry에서, 검출된 공의 바운딩 박스 크기(width, height)를 세 배로 확장하여 해결할 수 있었다. <p align="center"><img src="https://github.com/uomoy/tennis-tracking/assets/55055376/16327234-5963-41e6-a61e-df1fdad36696"></p>
  - 이는 확장 배수에 따른 tracking evaluation 결과 비교를 통해 바운딩 박스 크기를 얼마나 확장시킬지 결정했다. 3배로 확장시켰을 때 MOTA가 가장 높았다.
<br>

- 또한 ByteTrack의 update 메소드에서 테니스공에 대한 conf threshold는 기존 default 값(0.5)을 유지하면서 선수 클래스에 대한 threshold만 증가시키는 간단한 로직을 추가했다.
- Kalman filter에서 속도 불확실성 가중치(_std_weight_velocity)를 1/160(default)에서 1/20으로 증가시켜 빠르게 움직이는 공에 대한 예측 정확도를 높이고자 했다.

<br>  
<br>  

## Tracking Evaluation
- 추적 추론 결과를 평가하기 위해 13초 내외의 테니스 경기 영상 시퀀스 3개를 선별했다.
- 모델의 generalization performance를 측정하는 것이 중요하므로 코트의 다양성, 타구의 다양성을 고려하였고, 모델 훈련에 사용되지 않은 테니스 대회 경기를 선택했다.
- 3개의 영상 시퀀스는 각 하드 코트, 잔디 코트, 클레이 코트에서 펼쳐지는 경기이며 서브, 포핸드 스트로크, 백핸드 스트로크, 발리, 드롭샷 등 다양한 타구를 포함한다.
- 해당 영상 시퀀스들에 대해 MOT16 format의 ground truth를 작성하고, tracking prediction 역시 MOT16 format의 txt 파일로 생성하였다. 이어서 py-motmetrics 패키지를 사용하여 MOTA, precision, recall 등의 metrics를 측정하였다.
<p align="center"><img src="https://github.com/uomoy/tennis-tracking/assets/55055376/235bb5e5-78d7-4439-b197-ea2cef801a13"></p>

- Length는 30fps 영상 시퀀스의 frame 수이며 GT는 영상 시퀀스의 전체 ground truth 수, Speed는 프레임당 평균 추론 시간(ms)이다.
- 추론은 12th Gen Intel Core(TM) i5-12400F, NVIDIA GeForce RTX 3060 (12,288MiB)의 하드웨어 환경에서 진행되었다.

<br>  
<br>  

## Visualization
- 앞서 학습을 통해 얻은 최적의 detection model weight를 사용하여 선수와 공을 시각화하는 코드를 작성했다.
- 프레임의 흐름에 따라 각 tracklet의 색상, 굵기, 크기 등을 변화시킴으로써 readable하게 temporal information을 제공하고자 했다.
- 테니스공은 노란색 계열의 원으로, 두 선수는 파란색 계열의 타원으로 시각화했다.<p align="center"><img src="https://github.com/uomoy/tennis-tracking/assets/55055376/df14a71e-2ecb-4d11-aea8-48fbbb9bf139"></p>


<br>  
<br>  

## Conclusion
- 테니스 중계 영상에서 테니스 선수와 테니스공을 빠른 추론속도로 검출 및 추적하고자 했다. 특히 빠르게 움직이고, 그 크기가 아주 작은 테니스공을 정확하게 검출/추적하고자 했다.
- 결과적으로 기존 ByteTrack의 update method에서 검출된 객체가 테니스공 클래스라면 바운딩 박스의 width와 height가 기존 크기의 세 배가 되도록 이를 확장시키는 간단한 로직을 추가함으로써 테니스공에 대한 추적 성능을 크게 향상시켰다.
- 또한 YOLOv8n을 detector로 사용하여 real-time 수준의 처리를 가능케 했다.
- 다음은 기존 ByteTrack과 update 메소드를 수정한 modified ByteTrack을 사용했을 때의 테니스공 추적 성능 비교이다. <p align="center"><img src="https://github.com/uomoy/tennis-tracking/assets/55055376/15796baf-7e49-40a6-9ede-ce8e7cf8c6bd"></p>


<br>  
<br>  

