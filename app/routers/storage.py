from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from google.cloud import storage, vision
from app.database import get_connection
import uuid
import logging
# Logging yapılandırması
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_file(course_id: int, file: UploadFile = File(...)):
    """Google Cloud Storage'a dosya yükler ve URL'yi veritabanına kaydeder."""
    bucket_name = "student-workflow-bucket"  # Bucket adınızı buraya yazın
    storage_client = storage.Client()

    # Benzersiz dosya adı oluştur
    file_name = f"{uuid.uuid4()}-{file.filename}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        # Dosyayı Google Cloud Storage'a yükle
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        file_url = blob.public_url  # Yüklenen dosyanın URL'si

        # URL'yi veritabanına kaydet
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE courses SET file_url = %s WHERE id = %s RETURNING id",
            (file_url, course_id)
        )
        updated_id = cursor.fetchone()
        conn.commit()

        if not updated_id:
            raise HTTPException(status_code=404, detail="Course not found")

        return {"message": "File uploaded and URL saved successfully", "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
@router.post("/ocr")
async def upload_and_process_file(file: UploadFile = File(...), course_id: int = None):
    """Resmi Google Cloud Storage'a yükle ve Vision API ile metin tanı."""
    bucket_name = "student-workflow-bucket"  # Bucket adınız
    storage_client = storage.Client()
    vision_client = vision.ImageAnnotatorClient()  # Vision API istemcisi

    # Benzersiz dosya adı oluştur
    file_name = f"{uuid.uuid4()}-{file.filename}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        # 1. Dosyayı Google Cloud Storage'a yükle
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        file_url = blob.public_url

        # 2. Vision API ile resmi işleme
        image = vision.Image(source=vision.ImageSource(image_uri=file_url))
        response = vision_client.text_detection(image=image)

        # 3. Algılanan metni al
        texts = response.text_annotations
        detected_text = texts[0].description if texts else "No text detected"

        # 4. Yanıtı döndür
        return {
            "message": "File uploaded and processed successfully",
            "file_url": file_url,
            "detected_text": detected_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
# Dosya yükleme ve veritabanına kaydetme
@router.post("/storage/upload")
def upload_file_to_course(course_id: int = Query(...), file: UploadFile = File(...)):
    try:
        # Google Cloud Storage'a dosya yükleme
        storage_client = storage.Client()
        bucket = storage_client.bucket("student-workflow-bucket")
        unique_filename = f"{uuid.uuid4()}-{file.filename}"
        blob = bucket.blob(unique_filename)
        blob.upload_from_file(file.file)

        # Dosyanın URL'si
        file_url = f"https://storage.googleapis.com/{bucket.name}/{unique_filename}"

        # Veritabanına dosya URL'sini kaydetme
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO course_files (course_id, file_url)
            VALUES (%s, %s)
            RETURNING id
            """,
            (course_id, file_url)
        )
        conn.commit()

        return {"message": "File uploaded and linked to course", "file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/storage/files")
def get_files_for_course(course_id: int = Query(...)):
    logger.info("Step 1: Endpoint accessed with course_id: %s", course_id)
    try:
        conn = get_connection()
        logger.info("Step 2: Database connection successful!")

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, file_url, uploaded_at
            FROM course_files
            WHERE course_id = %s
            """,
            (course_id,)
        )
        files = cursor.fetchall()
        logger.info("Step 3: SQL Query Result: %s", files)

        if not files:
            logger.error("Step 4: No files found for course_id: %s", course_id)
            raise HTTPException(status_code=404, detail="No files found")

        response = {"files": [{"id": row["id"], "file_url": row["file_url"], "uploaded_at": row["uploaded_at"]} for row in files]}
        logger.info("Step 5: Response generated: %s", response)
        return response
    except Exception as e:
        logger.error("Step 6: Error occurred: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
            logger.info("Step 7: Cursor closed")
        if 'conn' in locals():
            conn.close()
            logger.info("Step 8: Database connection closed")

def test_database_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM course_files WHERE course_id = 2")
        result = cursor.fetchall()
        print("Database query result:", result)
    except Exception as e:
        print("Database connection or query error:", str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

test_database_connection()