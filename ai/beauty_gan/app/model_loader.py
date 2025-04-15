import tensorflow as tf
import dlib

# TensorFlow 세션 및 모델 로드
sess = tf.Session()
sess.run(tf.global_variables_initializer())

# 저장된 모델 메타 정보 로드
saver = tf.train.import_meta_graph('models/model.meta')
saver.restore(sess, tf.train.latest_checkpoint('models'))

graph = tf.get_default_graph()

# 입력/출력 텐서 추출
X = graph.get_tensor_by_name('X:0')
Y = graph.get_tensor_by_name('Y:0')
Xs = graph.get_tensor_by_name('generator/xs:0')

# 얼굴 탐지 및 랜드마크 모델 로딩 (dlib)
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_5_face_landmarks.dat')