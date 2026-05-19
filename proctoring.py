import cv2
import face_detector
import sqlite3
import uuid

# -------------------------------
# Load face detection model
# -------------------------------
model = face_detector.get_face_detector()

# -------------------------------
# Start webcam
# -------------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ Webcam not accessible")
    exit()

print("✅ Webcam started")

# -------------------------------
# Cheating detection variables
# -------------------------------
cheating_score = 0
status = "NORMAL"

def save_result(student_id, cheating_score, verdict):
    conn = sqlite3.connect("server/proctoring.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO exam_results (student_id, cheating_score, verdict)
        VALUES (?, ?, ?)
    """, (student_id, cheating_score, verdict))

    conn.commit()
    conn.close()


# -------------------------------
# Main loop
# -------------------------------
final_verdict = "NORMAL"
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_h, frame_w = frame.shape[:2]
    faces = face_detector.find_faces(frame, model)

    # -------------------------------
    # RULE 1: No face detected
    # -------------------------------
    if len(faces) == 0:
        cheating_score += 1
        status = "NO FACE DETECTED"

    # -------------------------------
    # RULE 2: Multiple faces detected
    # -------------------------------
    elif len(faces) > 1:
        cheating_score += 5
        status = "MULTIPLE FACES DETECTED"

    # -------------------------------
    # RULE 3: Single face detected
    # -------------------------------
    else:
        (x, y, x1, y1) = faces[0]
        face_center_x = (x + x1) // 2
        face_center_y = (y + y1) // 2

        frame_center_x = frame_w // 2
        frame_center_y = frame_h // 2

        threshold_x = int(frame_w * 0.10)
        threshold_y = int(frame_h * 0.10)

        # Looking away left or right
        if abs(face_center_x - frame_center_x) > threshold_x:
            cheating_score += 2
            status = "LOOKING AWAY (LEFT / RIGHT)"

        # Looking away up or down
        elif abs(face_center_y - frame_center_y) > threshold_y:
            cheating_score += 2
            status = "LOOKING AWAY (UP / DOWN)"

        else:
            status = "NORMAL"
        
    # Decide final verdict based on cheating score
    if cheating_score > 5:
        final_verdict = "CHEATING"
    else:
        final_verdict = "NORMAL"

    


    # -------------------------------
    # Draw face boxes
    # -------------------------------
    face_detector.draw_faces(frame, faces)

    # -------------------------------
    # Display status and score
    # -------------------------------
    cv2.putText(
        frame,
        f"Status: {status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"Cheating Score: {cheating_score}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 0, 0),
        2
    )

    cv2.imshow("AI Exam Proctoring System", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


student_id = str(uuid.uuid4())[:8]
 # demo student
save_result(student_id, cheating_score, final_verdict)
print("Result saved to database")



# -------------------------------
# Cleanup
# -------------------------------
cap.release()
cv2.destroyAllWindows()

# -------------------------------
# Final Verdict
# -------------------------------
if cheating_score > 15:
    verdict = "CHEATING"
elif cheating_score > 7:
    verdict = "SUSPICIOUS"
else:
    verdict = "NORMAL"

print("\n===== EXAM SESSION RESULT =====")
print("Final Cheating Score:", cheating_score)
print("Final Verdict:", verdict)
