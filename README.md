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
