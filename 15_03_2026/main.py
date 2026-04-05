from fastapi import HTTPException
from fastapi import FastAPI
from pydantic import BaseModel #для проверки данных на типизацию

from createDB import get_connection, init_db

from fastapi import Request, From
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request:Request):
    return {"message":"Привет! FastApi сервер работает"}

@app.get("/students")
def get_all_students():
    return students_db

@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code = 404, detail = "Ученик не найден")

@app.post("/students/")
def create_student(student: StudentCreate):
    new_id = students_db[-1]["id"] + 1
    new_student = {
        "id": new_id,
        "name": student.name,
        "age": student.age,
        "grade": student.grade
    }
    students_db.append(new_student)
    return {"message":"Ученик добавлен!", "data":new_student}

@app.put("/students/{student_id}/grade")
def update_grade(student_id: int, new_grade: int):
    global students_db
    for student in students_db:
        if student["id"] == student_id:
            student["grade"] = new_grade
            return {"message":f"Оценка ученика {student['name']} "
                              f"обновлена на {new_grade}"}
    raise HTTPException(status_code=404, detail="Ученик не найден")

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    global students_db
    len_start = len(students_db)
    students_db = [student for student in students_db if student["id"] != student_id]

    if len(students_db) == len_start:
        raise HTTPException(status_code=404, detail="Ученик не найден")

    return {"message":"Ученик удален успешно"}
