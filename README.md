# Budgy - Manage Your Finances
6510615229 พลกฤต กันยายน\
6510615245 พลอยพรรณ เต็งประยูร\
6610685015 อติชาต เพ็ญวงษ์\
6610685031 กฤติน ด่านซ้าย\
6610685155 ณัฐศิษฏ์ ฐิติธรรมคุณ

[Canva Presentation Link](https://www.canva.com/design/DAG2LcR2s3g/7kqvF-aWzW9l06rd7O-O4g/edit?utm_content=DAG2LcR2s3g&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

![Budgy - Manage Your Finances](https://github.com/6610685031/cn331-project-budgy/blob/main/budgy.png?raw=true)

### Accessible via
https://cn331-project-budgy.onrender.com/ \
https://budgy.krentiz.dev/

## Cloning this repository
```
git clone https://github.com/6610685031/cn331-project-budgy
cd cn331-project-budgy/budgy
```

## Setting up Virtual Environment
```
python -m venv .venv
```
Activate virtual enviroment (for bash, unix-system alike)
```
source .vnev/bin/activate
```
and for Windows
```
.venv\Scripts\activate.bat
```
## Installing from requirements.txt
```
pip install -r requirements.txt
```
If you don't have pip installed, please refer to the Python official website: https://packaging.python.org/en/latest/tutorials/installing-packages/

## Create new database migrations (this is required for first time usage)
```
cd budgy
python manage.py makemigrations
python manage.py migrate
```

## Running the web server
```
python manage.py runserver
```

## Creating Superuser (this is required for accessing admin pages)
```
python manage.py createsuperuser
```

## Flush Database (for deployment purposes)
```
python manage.py flush
```
