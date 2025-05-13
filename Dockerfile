FROM python:3.10

# กำหนด working directory
WORKDIR /app

# คัดลอกไฟล์ทั้งหมดไปยัง container
COPY . /app

# ติดตั้ง dependency
RUN pip install -r requirements.txt

# รันเซิร์ฟเวอร์ Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
