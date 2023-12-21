# tennis-tracking
tennis ball &amp; players tracking with various models


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
1. YOLOv8 & ByteTrack
2. TrackNetV2

## Dataset
- 총 13,027장의 HD(1280*720) resolution 데이터셋
  - [TrackNet](https://nol.cs.nctu.edu.tw:234/open-source/TrackNet)의 총 19,842장의 학습 데이터 중 가시성 수준이 ‘공이 쉽게 식별됨’인 17,632장을 일차적으로 추출 후, 무작위로 25%를 샘플링한 4,407장의 이미지에 선수를 레이블링하여 학습에 사용.
  - 2023년에 진행된 메이저 대회(윔블던, 호주 오픈, US 오픈, 프랑스 오픈) 경기 영상 프레임 각 3,001, 1,500, 1,499, 2,620장에 공과 선수를 레이블링하여 사용.
<br>

- 테니스공이 타이트한 bounding box로 레이블링될 경우, 빠른 속도에 의해 blur되고 왜곡된 공을 cover하지 못하므로 여유로운 크기로 레이블링 진행(HD 기준 35px * 35px)
- 공의 레이블링 과정에서 공이 보이지 않을 정도로 heavy(full) occlusion이 일어난 경우에는 공의 annotation은 건너뛰고 선수의 annotation만 추가.
- 각 데이터는 코트 종류, 서브 포지션, 스트로크 종류 등을 균형적으로 고려하여 선별.


<br>  
<br>  

## Conclusion
TrackNetV2와 YOLOv8n & ByteTracker을 이용하여 테니스공에 대한 tracking의 성능을 올리고자 했다. TrackNet은 tiny and fast 물체에 대한 tracking을 하기 위한 heatmap기반의 deep learning network이고 YOLOv8n은 YOLOv8의 nano model로 detection에서 좋은 성능을 보이며 속도가 빠르다.

본 보고서에서는 기존의 TrackNet보다 더 빠른 속도와 우수한 성능을 보인 TrackNetV2를 사용하였고 deepsort 대신 real-time에 조금 더 적합한 bytetracker를 활용하였다. TrackNetV2에서는 기존 논문에 비해 optimizer와 parameters를 바꿔줌으로써 성능 향상을 이뤄냈고 skip connection을 적용하여 속도 부분에서도 향상을 이뤄냈다. (6FPS -> 7FPS) 

state-of-the-art 검출 모델인 YOLOv8을 통해 작고 빠른 테니스공을 높은 precision, recall로 검출하고자 했고, ByteTrack과 결합하여 일관된 객체 추적을 수행하고자 했다. 특히 검출된 테니스공의 바운딩 박스 크기를 확장시켜 linear assignment에서 발생하는 matching problem을 해결했다. 이로써 테니스공에 대한 MOTA를 61.4%(baseline)에서 77.8%로 크게 향상시켰다. 그리고 프레임당 처리 속도가 11.5ms (on RTX 3060) 내외로 측정되어 real-time 수준의 처리가 가능했다.

하지만 tiny object detection에  있어서 occlusion이라는 한계는 추후 연구에서 보완이 필요하다.
ByteTrack 대신에 속도 부분에서 약간 떨어지지만 정확도면에서 조금 더 정교한 DeepSort를 사용한다면 보완이 될 것으로 보인다. 


<br>  
<br>  

