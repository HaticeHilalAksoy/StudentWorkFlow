from fastapi import APIRouter, File, UploadFile, HTTPException
from google.cloud import storage
from app.database import get_connection
import uuid

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
