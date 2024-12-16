from fastapi import APIRouter, HTTPException
from app.database import get_connection
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class CourseCreate(BaseModel):
    title: str
    goal_hours: int
    user_id: int

@router.post("/add")
def add_course(course: CourseCreate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        # SQL sorgusu: Yeni ders ekle
        cursor.execute(
            """
            INSERT INTO courses (title, goal_hours, user_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (course.title, course.goal_hours, course.user_id)
        )
        result = cursor.fetchone()
        print("SQL Query Result:", result)  
        if not result:
            raise HTTPException(status_code=500, detail="Failed to fetch course ID")
        
        course_id = result['id']
        conn.commit()
        return {"message": "Course added successfully", "course_id": course_id}
    except Exception as e:
        conn.rollback()  
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/")
def list_courses(user_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        # SQL sorgusu: Kullanıcının derslerini çek
        cursor.execute(
            """
            SELECT id, title, goal_hours, completed_hours, created_at
            FROM courses
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        courses = cursor.fetchall()
        if not courses:
            return {"message": "No courses found for this user"}
        
        return {"courses": courses}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
# Pydantic model for course update
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    goal_hours: Optional[int] = None

@router.put("/{course_id}")
def update_course(course_id: int, course: CourseUpdate):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        updates = []
        params = []

        # Dinamik olarak güncellenecek alanları kontrol et
        if course.title is not None:
            updates.append("title = %s")
            params.append(course.title)
        
        if course.goal_hours is not None:
            updates.append("goal_hours = %s")
            params.append(course.goal_hours)

        # Eğer hiçbir alan güncellenmiyorsa hata ver
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(course_id)
        query = f"""
            UPDATE courses
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, title, goal_hours, completed_hours, created_at
        """

        cursor.execute(query, tuple(params))
        updated_course = cursor.fetchone()

        if not updated_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Hata ayıklama: Güncellenen dersi yazdır
        print("Updated Course:", updated_course)

        conn.commit()

        # Güncellenen kursu JSON formatında döndür
        return {
            "message": "Course updated successfully",
            "course": {
                "id": updated_course['id'],
                "title": updated_course['title'],
                "goal_hours": updated_course['goal_hours'],
                "completed_hours": updated_course['completed_hours'],
                "created_at": updated_course['created_at'],
            }
        }
    except Exception as e:
        conn.rollback()
        # Daha açıklayıcı hata döndür
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
@router.delete("/{course_id}")
def delete_course(course_id: int):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        # Kursu sil ve silinen kursun id'sini döndür
        cursor.execute("DELETE FROM courses WHERE id = %s RETURNING id", (course_id,))
        deleted_course = cursor.fetchone()

        # Hata ayıklama: Silinen kursun sonucunu yazdır
        print("Deleted Course:", deleted_course)

        # Eğer kurs bulunamazsa
        if not deleted_course:
            raise HTTPException(
                status_code=404,
                detail=f"Course not found: ID {course_id}. Please ensure the ID exists in the database."
            )

        conn.commit()
        return {"message": "Course deleted successfully", "course_id": deleted_course[0]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
