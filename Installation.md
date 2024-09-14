## Installation

---

## Change the directory to the project directory

```bash
cd ku-polls
```

---

## Create virtual environment

```bash
python -m venv .venv
```

---

## Activate the virtual environment

### on Window

```bash
.venv\Scripts\activate
 ```

### on MacOS / Linux

```bash
source .venv/bin/activate
```

---

## Install require packages

```bash
pip install -r requirements.txt
```

---

## Set environment variables (You can change your environment variables)

### on Window

```bash
copy sample.env .env
 ```

### on MacOS / Linux

```bash
cp sample.env .env
```

---

## Migrate database

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

---

## Load data into database

```bash
python manage.py loaddata data/polls-v4.json
```

```bash
python manage.py loaddata data/users.json
```

```bash
python manage.py loaddata data/votes-v4.json
```

---

## Run tests

```bash
python manage.py test
```

---
