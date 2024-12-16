from fastapi import APIRouter, HTTPException
from app.database import get_connection

router = APIRouter()

@router.get("/weekly")
def weekly_report(user_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        # SQL Sorgusu
        cursor.execute(
            """
            SELECT
                title,
                goal_hours,
                completed_hours,
                (goal_hours - completed_hours) AS remaining_hours
            FROM courses
            WHERE user_id = %s
            ORDER BY title;
            """,
            (user_id,)
        )
        report = cursor.fetchall()

        # Hata Ayıklama: Sorgu Sonucunu Yazdır
        print("Query Result:", report)

        # Eğer sonuç boşsa
        if not report:
            raise HTTPException(status_code=404, detail="No data found for the user.")

        # RealDictRow Nesnelerini JSON Formatına Dönüştür
        result = [dict(row) for row in report]

        return {"weekly_report": result}

    except Exception as e:
        # Hata Detaylarını Yazdır
        print("Error Details:", str(e))
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    finally:
        cursor.close()
        conn.close()
