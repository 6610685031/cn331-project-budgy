# Budgy - Manage Your Finances

## Members

6510615229 พลกฤต กันยายน\
6510615245 พลอยพรรณ เต็งประยูร\
6610685015 อติชาต เพ็ญวงษ์\
6610685031 กฤติน ด่านซ้าย\
6610685155 ณัฐศิษฏ์ ฐิติธรรมคุณ

---

[Canva Presentation Link](https://www.canva.com/design/DAG2LcR2s3g/7kqvF-aWzW9l06rd7O-O4g/edit?utm_content=DAG2LcR2s3g&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

![Budgy - Manage Your Finances](https://github.com/6610685031/cn331-project-budgy/blob/main/budgy.png?raw=true)


### สามารถเข้าใช้งานได้ผ่าน URLs ข้างล่างนี้
https://cn331-project-budgy.onrender.com/ \
https://budgy.krentiz.dev/

---

## วิธีติดตั้ง & รัน (Dev)
1. โคลนไฟล์จาก github repo
```
git clone https://github.com/6610685031/cn331-project-budgy
cd cn331-project-budgy/budgy
```

2. สร้าง virtual environment และติดตั้งแพ็กเกจ
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```
>If you don't have pip installed, please refer to the Python official website: https://packaging.python.org/en/latest/tutorials/installing-packages/

3. สร้างฐานข้อมูล
```
cd budgy
python manage.py makemigrations
python manage.py migrate
```

4. สร้างผู้ดูแลระบบ (สำหรับเข้า /admin/ และ/หรือสิทธิ์แอดมินในระบบ)
```
python manage.py createsuperuser
```

5. รันเซิร์ฟเวอร์
```
python manage.py runserver
```

Extra: คำสั่งสำหรับล้างฐานข้อมูล local
```
python manage.py flush
```

## วิดีโอตัวอย่างการใช้งาน
[Demo Video Link](https://youtu.be/bNGkeYdZr34)
