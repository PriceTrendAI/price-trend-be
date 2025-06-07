# price-trend-be
부동산 실거래/시세 기반 예측 백엔드 서비스


## 📦 환경 구축 가이드
### 1. 시스템 패키지 설치
```bash
sudo apt update
sudo apt install python3-full python3-venv mysql-server
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
```

## 🚀 서버 실행 방법
```bash
source price-trend-ai/bin/activate
uvicorn app.main:app --reload
```

## 🗂 디렉토리 구조
```bash
price-trend-be/
├── app/
│   ├── main.py
│   ├── database.py
│   └── ...
├── .env
├── README.md
└── price-trend-ai/ (venv)
```