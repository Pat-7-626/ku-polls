## Installation

---

## Change the directory to the project directory

```bash
cd ku-polls
```

---

## Create virtual environment

```bash
python -m venv env
```

---

## Activate the virtual environment

### on Window

```bash
env\Scripts\activate
 ```

### on MacOS / Linux

```bash
source env/bin/activate
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
python manage.py migrate
```

---

## Load data into database

### Data for Question and Choices only (no Votes)

```bash
python manage.py loaddata data/polls-v4.json
```

### Data for Votes

```bash
python manage.py loaddata data/users.json
```

### The auth.user data in a file ```data/users.json```

```bash
python manage.py loaddata data/votes-v4.json
```

### load all data files

```bash
python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```

---

## Run tests

```bash
python manage.py test
```

---