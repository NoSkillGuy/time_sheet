import cv2
import face_recognition
import os

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    # Display the image
    cv2.imshow("Live Image", frame)
    # Hit 's' on the keyboard to save!
    keyboard_input = cv2.waitKey(1)
    if keyboard_input == ord('s'):
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if not face_locations:
            print('No faces in the captured Picture')
        else:
            # Release handle to the webcam
            video_capture.release()
            cv2.destroyAllWindows()
            # This is for Mac Specific. Others please bear 1ms delay.
            cv2.waitKey(1)
            while True:
                name = input("Enter your name (should not contain '.'): ")
                if ((not not name) and (not '.' in name)):
                    break
                else:
                    print("warning: You name either contains '.' or is an empty string")
            save_name = "{}/images/{}.jpg".format(os.getcwd(),name)
            # Converting color image to gray
            grayscale_image = cv2.cvtColor(rgb_small_frame, cv2.COLOR_BGR2GRAY)
            # Saving grayscale_image to save_name location
            cv2.imwrite(save_name, grayscale_image)
            print("Image Saved here {}".format(save_name))
            break
    # Hit 'q' on the keyboard to quit!
    elif keyboard_input == ord('q'):
        print('Picture not taken')
        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
        break