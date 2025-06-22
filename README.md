# price-trend-be
부동산 실거래/시세 기반 예측 백엔드 서비스


## 📦 환경 구축 가이드
### 1. 시스템 패키지 설치
```bash
# ubuntu 24.04
sudo apt update
sudo apt install -y python3-full python3-venv mysql-server
sudo apt install -y chromium-browser
sudo apt install -y uvicorn

google-chrome --version  # ex) Google Chrome 137.0.7151.68
wget https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.68/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
chromedriver --version   # ex) ChromeDriver 137.0.7151.68 
```

### 2. 가상환경 및 Python 패키지 설치
```bash
# 가상환경 생성 및 활성화
python3 -m venv price-trend-ai
source price-trend-ai/bin/activate

# 필수 라이브러리 설치 : 방법 1
pip install --upgrade pip
pip install pandas numpy matplotlib scikit-learn selenium
pip install fastapi uvicorn sqlalchemy pymysql
pip install python-dotenv cryptography

# 필수 라이브러리 설치 : 방법 2
pip install -r requirements.txt
```

### 3. MySQL 설정
```bash
# MySQL 실행
sudo mysql

# 비밀번호 인증 방식 설정
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '[비밀번호]';
FLUSH PRIVILEGES;

# DB 생성 및 권한 부여
CREATE DATABASE real_estate_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON real_estate_ai.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 4. 환경 변수 설정
```bash
# .env
MYSQL_USER=root
MYSQL_PASSWORD=[your-password]
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=real_estate_ai
PRIVATE_CORS=http://[front-end-ip]:[front-end-port]
```

## 🚀 서버 실행 방법
```bash
source price-trend-ai/bin/activate

# Run server (local only, accessible via 127.0.0.1)
uvicorn app.main:app --reload

# Run server (accessible from other devices)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🗂 디렉토리 구조
```bash
price-trend-be
├── README.md
├── .env
├── app
│   ├── crawler.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── price-trend-ai/ (venv)
└── requirements.txt
```
