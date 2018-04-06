import cv2
import face_recognition
import datetime as dt
import os

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample pictures and learn how to recognize it.
known_face_names = []
known_face_encodings = []
for image in os.listdir('images'):
    # Load the picture
    loaded_image = face_recognition.load_image_file("images/{}".format(image))
    # Get facial encodings
    face_encoding = face_recognition.face_encodings(loaded_image)[0]
    known_face_names.append(image.split('.')[0])
    known_face_encodings.append(face_encoding)

known_face_names_time_hash = {}
for face_name in known_face_names:
    known_face_names_time_hash[face_name] = 0

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

print("Calculating Time before the machine from now {}".format(dt.datetime.now()))

prev_frame_time = dt.datetime.now()

while True:
    current_frame_time = dt.datetime.now()    

    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                known_face_names_time_hash[name] += ( current_frame_time - prev_frame_time).microseconds

            face_names.append(name)
    prev_frame_time = current_frame_time
    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Script stopped calculating time at {}".format(dt.datetime.now()))
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

for known_face in known_face_names_time_hash:
    print("{} worked before this machine for {} Seconds".format(known_face, known_face_names_time_hash[known_face]/1000000))

