import cv2
import mediapipe as mp
import time
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
smoothening = 7

# For static images:
IMAGE_FILES = []
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))

# For webcam input:
cap = cv2.VideoCapture(0)
prevTime = 0

fpscount = 0
fpssum = 0
handframe = 0
while(True):
  ret, image = cap.read()
  curTime = time.time()
  sec = curTime - prevTime
  prevTime = curTime
  fps = 1/(sec)
  print(fps)
  str1 = f"FPS : {round(fps,4)}"
  with mp_hands.Hands(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
      curTime = time.time()
      sec = curTime - prevTime
      prevTime = curTime
      fps = 1/(sec)
      fps = round(fps,2)
      str1 = f"FPS : {fps}"
      fpscount += 1
      fpssum = fpssum + fps
      print('fps평균: ',fpssum/fpscount, end='\t')
      print('손없는프레임: ',fpscount - handframe)
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frrame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

  
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
      image.flags.writeable = False
      results = hands.process(image)

    # Draw the hand annotations on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          mp_drawing.draw_landmarks(
              image,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              mp_drawing_styles.get_default_hand_landmarks_style(),
              mp_drawing_styles.get_default_hand_connections_style())
        handframe += 1

      cv2.putText(image, str1, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
      cv2.imshow('MediaPipe Hands', image)
      
      
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()
