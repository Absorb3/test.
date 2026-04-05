
from fastapi import HTTPException
from fastapi import FastAPI
from pydantic import BaseModel #для проверки данных на типизацию

from createDB import get_connection, init_db

from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI() #созается экземпляр приложения

students_db = [
    {"id": 1, "name": "Анна", "age": 12, "grade": 5},
    {"id": 2, "name": "Борис", "age": 13, "grade": 4},
    {"id": 3, "name": "Вика", "age": 12, "grade": 5}
]

class StudentCreate(BaseModel): #модель данных для валидации
    name: str
    age: int
    grade: int

init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    students = [dict(row) for row in rows]
    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={"students": students}
    )

@app.get("/add_student", response_class=HTMLResponse)
async def add_students_page(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="add_student.html"
    )

@app.post("/add_student")
async def add_student(request: Request,
                      name: str = Form(...),
                      age: int = Form(...),
                      grade: int = Form(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, age, grade) VALUES (?, ?, ?)
    """, (name, age, grade))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="add_student.html",
        context={"message": f"Ученик {new_id} добавлен"}
    )

@app.get("/students")
def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    return dict(row)

@app.post("/students/")
def create_student(student: StudentCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, age, grade) VALUES (?, ?, ?)
    """, (student.name, student.age, student.grade))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "name":student.name}

@app.put("/students/{student_id}/grade")
def update_grade(student_id: int, new_grade: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET grade = ? WHERE id = ?", (new_grade, student_id))
    conn.commit()
    updateRow = cursor.rowcount
    conn.close()
    if updateRow == 0:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    return {"message": f"Оценка обновлена на {new_grade}"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    return {"message": f"Ученик успешно удален"}

