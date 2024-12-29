# StudentWorkFlow
""
psql -U postgres -d study_tracker
DELETE FROM courses WHERE id = 5 RETURNING id;
\q
""

çalıştırmak istersen: "uvicorn app.main:app --reload --port 8001"

already exist hatası alırsan: "lsof -i :8001" yap ve çıkan PID ları tek tek "kill -9 ÇIKAN_PID" ile öldür.

DAY-1
DB Schema hazırladım.
PostgreSQL ile db hazırladım.
post-ADD endpoint yazdım postman da test ettim.
login ve register endpoint yazdım ve postmanda test ettim.

DAY-2
GET Endpoint Yazma--
<
Kullanıcıya ait dersleri SQL sorgusu ile veritabanından çektik.
Sonuçları JSON formatında Postman üzerinden döndürdük.
created_at alanına göre dersler son eklenenden ilk eklenene sıralandı.
>
dersleri güncelleme işlemini eklemek (PUT--ders güncelleme işlemi için bir endpoint)
dersleri silme endpointi eklendi (delete)
user_id ile raporlama 

Day-3
Google Cloud Entegrasyonu -- Dosya Yükleme: Kullanıcılar derslerine ait dosyaları (örneğin, resimler) Google Cloud Storage’a yükleyebiliyor.
Dosya URL'si: Yüklenen dosyanın URL’si veritabanına kaydediliyor.




import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="study_tracker",
            user="postgres",
            password="hazalaras07H.", 
            host="localhost",
            port="5432",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

http://localhost:8000/docs#/

http://34.135.249.120



# Test CI/CD Trigger
