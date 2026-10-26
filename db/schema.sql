CREATE TABLE estudiantes_academicos (
    student_id VARCHAR(50) PRIMARY KEY,
    course INT,
    curricular_units_1st_sem_enrolled INT,
    curricular_units_2nd_sem_enrolled INT,
    curricular_units_1st_sem_grade NUMERIC(5,2),
    curricular_units_2nd_sem_grade NUMERIC(5,2),
    target VARCHAR(20),
    attendance_percentage NUMERIC(5,2)
);
