import cv2
import face_recognition
from datetime import datetime, timedelta
import os
import argparse
import json

args_list = ["known_images_path","download_path"]

def user_input():
    config = argparse.ArgumentParser()
    config.add_argument('-cf', '--config_file', help='config file name', default='', type=str, required=False)
    config_file_check = config.parse_known_args()
    object_check = vars(config_file_check[0])

    if object_check['config_file'] != '':
        records = []
        json_file = json.load(open(config_file_check[0].config_file))
        for record in range(0,len(json_file['Records'])):
            arguments = {}
            for i in args_list:
                arguments[i] = None
            for key, value in json_file['Records'][record].items():
                arguments[key] = value
            records.append(arguments)
        records_count = len(records)
    else:
        # Taking command line arguments from users
        parser = argparse.ArgumentParser()
        parser.add_argument('-kip', '--known-images-path', help='Known images path', type=str, required=False)
        parser.add_argument('-dp', '--download-path', help='Time sheet save path', type=str, required=False)
        args = parser.parse_args()
        arguments = vars(args)
        records = []
        records.append(arguments)
    return records


class timesheet:
    def __init__(self):
        pass

    def display_frame(self, frame, face_locations, face_names):
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

    def display_results(self, known_face_names_time_hash):
        for known_face in known_face_names_time_hash:
            print("{}:".format(known_face))
            for time_lapse in known_face_names_time_hash[known_face]:
                time_lapse = known_face_names_time_hash[known_face][time_lapse]
                print("    Session Started at {}, Ended at {}, Time spent {}".format(time_lapse['start_time'].strftime("%d %b, %Y - %H:%M:%S"), time_lapse['end_time'].strftime("%d %b, %Y - %H:%M:%S"), time_lapse['time_diff']))

    def capture(self, known_images_path, download_path):
        print(known_images_path)
        print(download_path)
        # Get a reference to webcam #0 (the default one)
        video_capture = cv2.VideoCapture(0)
        # Load a sample pictures and learn how to recognize it.
        known_face_names = []
        known_face_encodings = []
        if not known_images_path:
            known_images_path = 'images'

        for image in os.listdir(known_images_path):
            # Load the picture
            loaded_image = face_recognition.load_image_file("{}/{}".format(known_images_path,image))
            # Get facial encodings
            face_encoding = face_recognition.face_encodings(loaded_image)[0]
            known_face_names.append(image.split('.')[0])
            known_face_encodings.append(face_encoding)
        known_face_names_time_hash = {}
        for face_name in known_face_names:
            known_face_names_time_hash[face_name] = {}
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        # Session Buffer. If face is not detected in 30 Sec, Session is ended.
        max_time_face_not_detected = 30
        print("Script started at {}".format(datetime.now()))
        prev_frame_time = datetime.now()

        while True:
            # Get the time at the current frame
            current_frame_time = datetime.now()    
            # Grab a single frame of video
            _ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                # Initialize a empty array
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                        current_length = len(known_face_names_time_hash[name])
                        if (current_length == 0) or (current_frame_time - known_face_names_time_hash[name][current_length-1]['end_time']).total_seconds() > max_time_face_not_detected:
                            known_face_names_time_hash[name][current_length] = {}
                            known_face_names_time_hash[name][current_length]['start_time'] = prev_frame_time
                            known_face_names_time_hash[name][current_length]['end_time'] = current_frame_time
                            known_face_names_time_hash[name][current_length]['time_diff'] = ( current_frame_time - prev_frame_time).total_seconds()
                        else:
                            known_face_names_time_hash[name][current_length-1]['end_time'] = current_frame_time
                            known_face_names_time_hash[name][current_length-1]['time_diff'] += ( current_frame_time - prev_frame_time).total_seconds()

                    face_names.append(name)
                prev_frame_time = current_frame_time
            process_this_frame = not process_this_frame

            self.display_frame(frame, face_locations, face_names)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Script stopped at {}".format(datetime.now()))
                break
        # Release handle to the webcam
        video_capture.release()
        # Destroy all open windows
        cv2.destroyAllWindows()
        self.display_results(known_face_names_time_hash)

def main():
    records = user_input()
    # print(records)
    for arguments in records:
        response = timesheet()
        if (arguments['known_images_path'] or arguments['download_path']):
            response.capture(arguments['known_images_path'], arguments['download_path'])
        else:
            response.capture('images/','downloads/')


if __name__ == "__main__":
    main()