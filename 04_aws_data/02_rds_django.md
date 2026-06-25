# RDS PostgreSQL과 Django 연동

## 학습 목표

- EC2 내부 데이터베이스와 RDS의 차이를 설명할 수 있다.
- 퍼블릭 접근이 차단된 RDS PostgreSQL을 생성할 수 있다.
- 보안 그룹 참조로 EC2에서만 RDS에 접근하게 만들 수 있다.
- Django 데이터베이스 설정을 환경 변수로 분리할 수 있다.

## 1. RDS를 사용하는 이유

EC2에 PostgreSQL을 직접 설치하면 운영체제 패치, 데이터베이스 설치, 백업, 장애 대응을 모두 사용자가 관리한다. RDS는 데이터베이스 서버의 설치, 백업, 모니터링 같은 작업 일부를 AWS가 관리하는 서비스이다.

PostgreSQL은 테이블의 행과 열로 데이터를 저장하고 SQL로 조회하는 관계형 데이터베이스이다. 사용자와 주문처럼 서로 관계가 있는 구조화된 데이터를 저장하는 데 적합하다. 이미지나 큰 파일은 S3에 두고, 파일의 이름·소유자·S3 키 같은 구조화된 정보는 데이터베이스에 두는 방식으로 역할을 나눌 수 있다.

| 구성 요소 | 역할 |
| --- | --- |
| RDS | PostgreSQL 서버 실행, 백업과 기반 운영 일부를 관리한다. |
| PostgreSQL 엔드포인트 | 애플리케이션이 DB 서버를 찾는 DNS 이름이다. |
| `psql` | 사람이 터미널에서 PostgreSQL에 접속하는 클라이언트이다. |
| `psycopg` | Django가 Python 코드에서 PostgreSQL에 연결하는 드라이버이다. |
| Django ORM | Python 객체와 데이터베이스 테이블을 연결한다. |

RDS를 사용해도 다음 항목은 사용자가 책임진다.

- 데이터베이스 계정과 비밀번호
- 보안 그룹과 네트워크 접근
- 테이블 구조와 데이터
- 백업 보존 기간과 삭제 정책
- 애플리케이션의 연결 정보 관리

## 2. 네트워크 구조

```text
[인터넷]
    |
    | 80
    v
[EC2 보안 그룹]
    |
    | 5432, 소스가 EC2 보안 그룹인 경우만 허용
    v
[RDS 보안 그룹]
    |
[PostgreSQL RDS, 퍼블릭 접근 비활성화]
```

브라우저나 로컬 PC에서 RDS에 직접 접속하지 않는다. EC2를 애플리케이션 서버이자 관리 접속 경로로 사용한다.

## 3. RDS 보안 그룹 만들기

1. EC2 콘솔의 `Security Groups`를 연다.
2. `Create security group`을 선택한다.
3. 이름에 `cloud-class-rds-sg`를 입력한다.
4. 기본 VPC를 선택한다.
5. 인바운드 규칙을 추가한다.

| 유형 | 포트 | 소스 |
| --- | ---: | --- |
| PostgreSQL | 5432 | `cloud-class-ec2-sg` 보안 그룹 |

6. 태그 `Project=cloud-class`를 추가한다.
7. 보안 그룹을 생성한다.

소스에는 IP 주소가 아니라 EC2 보안 그룹을 지정한다.

## 4. RDS PostgreSQL 만들기

1. AWS 콘솔에서 `RDS`를 연다.
2. `Databases`에서 `Create database`를 선택한다.
3. 생성 방식은 `Standard create`를 선택한다.
4. 엔진은 `PostgreSQL`을 선택한다.
5. 화면에서 기본으로 제안하는 PostgreSQL 메이저 버전을 선택한다.
6. 템플릿은 계정의 실습 또는 무료 플랜 조건에 맞는 항목을 선택한다.
7. DB 식별자에 `cloud-class-db`를 입력한다.
8. 마스터 사용자 이름에 `cloudadmin`을 입력한다.
9. 강력한 비밀번호를 생성해 비밀번호 관리자에 저장한다.
10. 인스턴스 클래스는 `db.t4g.micro`를 선택한다. 목록에 없다면 현재 선택할 수 있는 가장 작은 범용 유형을 선택한다.
11. 가용성은 `Single-AZ`를 선택한다. 이번 수업에서는 Multi-AZ를 사용하지 않는다.
12. 스토리지는 `gp3` 20 GiB로 지정하고 스토리지 자동 확장은 비활성화한다.
13. 기본 VPC를 선택한다.
14. 퍼블릭 접근은 `No`를 선택한다.
15. 기존 보안 그룹 `cloud-class-rds-sg`를 선택하고 기본 보안 그룹은 제거한다.
16. 초기 데이터베이스 이름에 `cloudapp`을 입력한다.
17. RDS Proxy와 유료 고급 모니터링 기능은 활성화하지 않는다.
18. 백업 보존 기간과 삭제 방지 설정을 확인한다. 수업 자원은 마지막에 삭제할 수 있어야 한다.
19. 태그 `Project=cloud-class`를 추가한다.
20. 예상 월별 비용과 설정 요약을 확인한 뒤 생성한다.

RDS 생성에는 시간이 걸린다. 상태가 `Available`이 될 때까지 다음 절의 패키지를 먼저 설치한다.

## 5. PostgreSQL 클라이언트 설치

EC2에 SSH 접속해 실행한다.

RDS에는 PostgreSQL 서버가 이미 실행되고 있으므로 EC2에 데이터베이스 서버를 다시 설치하지 않는다. `postgresql-client` 패키지는 원격 PostgreSQL과 통신하는 `psql`, `pg_isready` 같은 도구만 제공한다.

```bash
# PostgreSQL 서버에 연결할 명령줄 클라이언트를 설치한다.
sudo apt update
sudo apt install -y postgresql-client

# 설치된 psql 버전을 확인한다.
psql --version
```

## 6. RDS 엔드포인트 확인

RDS 콘솔에서 `cloud-class-db`를 선택하고 `Connectivity & security` 정보를 확인한다.

| 항목 | 기록할 값 |
| --- | --- |
| 엔드포인트 | `cloud-class-db.xxxxx.ap-northeast-2.rds.amazonaws.com` |
| 포트 | `5432` |
| 데이터베이스 | `cloudapp` |
| 사용자 | `cloudadmin` |

엔드포인트는 URL이 아니라 호스트 이름이다. 앞에 `http://`를 붙이지 않는다.

HTTP와 PostgreSQL은 서로 다른 프로토콜이다. 브라우저는 HTTP URL로 웹 서버에 접속하지만 Django와 `psql`은 엔드포인트와 5432번 포트를 사용해 PostgreSQL 프로토콜로 통신한다.

## 7. EC2에서 연결 시험

`<RDS_ENDPOINT>`를 실제 엔드포인트로 바꾼다.

```bash
# PostgreSQL 포트가 네트워크 수준에서 응답하는지 확인한다.
pg_isready -h <RDS_ENDPOINT> -p 5432 -d cloudapp

# 암호를 직접 명령에 적지 않고 대화형으로 입력해 RDS에 접속한다.
psql -h <RDS_ENDPOINT> -p 5432 -U cloudadmin -d cloudapp
```

`Password for user cloudadmin:`이 나오면 저장한 비밀번호를 입력한다. 접속 후 다음 SQL을 실행한다.

```sql
-- 현재 접속한 데이터베이스와 사용자 정보를 확인한다.
SELECT current_database(), current_user;

-- PostgreSQL 서버 버전을 확인한다.
SELECT version();

-- psql 세션을 종료한다.
\q
```

## 8. Django PostgreSQL 드라이버 설치

Django ORM이 SQL을 만들더라도 실제 네트워크 연결과 PostgreSQL 프로토콜 처리는 데이터베이스 드라이버가 담당한다. `psycopg`가 없으면 Django는 PostgreSQL 설정을 읽어도 서버와 통신할 수 없다.

```bash
# Django 프로젝트의 Conda 환경을 활성화한다.
conda activate cloud-class

# Django가 PostgreSQL에 연결할 수 있도록 psycopg 드라이버를 설치한다.
pip install "psycopg[binary]>=3.1"

# 프로젝트 디렉터리로 이동해 패키지 목록을 갱신한다.
cd ~/cloud-class-app
pip freeze > requirements.txt
```

## 9. 데이터베이스 환경 변수 추가

```bash
# 운영 환경 변수 파일을 root 권한으로 편집한다.
sudo vi /etc/cloud-class.env
```

기존 내용 아래에 다음 값을 추가한다.

```dotenv
DB_NAME=cloudapp
DB_USER=cloudadmin
DB_PASSWORD=RDS에서_설정한_비밀번호
DB_HOST=<RDS_ENDPOINT>
DB_PORT=5432
```

비밀번호에 공백, `#`, 따옴표처럼 환경 파일 해석에 영향을 주는 문자가 있으면 systemd의 `EnvironmentFile` 문법에 맞게 따옴표를 사용한다. 수업용 비밀번호도 GitHub에 저장하지 않는다.

## 10. Django 데이터베이스 설정 변경

`config/settings.py`의 `DATABASES`를 다음 코드로 바꾼다.

```python
# RDS PostgreSQL 연결 정보를 코드가 아닌 환경 변수에서 읽는다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}
```

`CONN_MAX_AGE`는 요청마다 새 연결을 만들지 않고 일정 시간 연결을 재사용하게 한다.

## 11. 마이그레이션 실행

현재 셸에서 환경 변수를 불러온 뒤 마이그레이션을 실행한다.

마이그레이션은 Django 모델의 변경 내역을 데이터베이스 테이블 생성·변경 작업으로 적용하는 과정이다. 애플리케이션 코드를 새로 배포해도 마이그레이션을 실행하지 않으면 코드가 기대하는 테이블과 실제 데이터베이스 구조가 달라질 수 있다.

```bash
# /etc/cloud-class.env의 모든 값을 현재 셸 환경으로 내보낸다.
set -a
source /etc/cloud-class.env
set +a

# Django 설정과 데이터베이스 연결을 검사한다.
python manage.py check

# Django 기본 테이블을 RDS PostgreSQL에 생성한다.
python manage.py migrate

# 적용된 마이그레이션 목록을 확인한다.
python manage.py showmigrations

# 변경된 환경과 DB 설정을 적용하도록 Gunicorn 서비스를 재시작한다.
sudo systemctl restart cloud-class

# 애플리케이션 상태와 최근 로그를 확인한다.
sudo systemctl status cloud-class
sudo journalctl -u cloud-class -n 50 --no-pager
```

## 12. RDS에 테이블이 생겼는지 확인

```bash
# RDS PostgreSQL에 다시 접속한다.
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
```

```sql
-- 현재 데이터베이스의 테이블 목록을 확인한다.
\dt

-- Django 마이그레이션 기록 수를 확인한다.
SELECT COUNT(*) FROM django_migrations;

-- psql 세션을 종료한다.
\q
```

`django_migrations`, `auth_user` 같은 Django 테이블이 보이면 연동이 정상이다.

## 13. 브라우저에서 최종 확인

```bash
# Gunicorn 서비스가 실행 중인지 확인한다.
systemctl is-active cloud-class

# Nginx를 거친 Django 상태 URL을 EC2 내부에서 확인한다.
curl http://127.0.0.1/health/
```

브라우저에서 다음 주소를 열어 JSON 응답을 확인한다.

```text
http://<EC2_PUBLIC_DNS>/health/
```

## 14. 문제 해결

### `connection timed out`이 나온다

- RDS 상태가 `Available`인지 확인한다.
- RDS와 EC2가 같은 VPC에 있는지 확인한다.
- RDS 보안 그룹의 소스가 `cloud-class-ec2-sg`인지 확인한다.
- 엔드포인트와 포트가 정확한지 확인한다.

### `password authentication failed`가 나온다

- 마스터 사용자 이름을 확인한다.
- 비밀번호 앞뒤 공백이 들어가지 않았는지 확인한다.
- 필요하면 RDS에서 마스터 비밀번호를 변경하고 환경 파일도 갱신한다.

### Django 서비스가 시작되지 않는다

```bash
# Django 서비스 실패 원인을 최근 로그에서 확인한다.
sudo journalctl -u cloud-class -n 100 --no-pager

# 환경 변수를 현재 셸에 불러와 Django 설정을 직접 검사한다.
set -a
source /etc/cloud-class.env
set +a
python manage.py check
```

## 15. 비용 주의

RDS는 EC2보다 삭제를 잊기 쉬운 자원이다. 인스턴스를 중지해도 저장소나 백업 비용이 남을 수 있다. 수업 마지막에는 DB 식별자, 스냅샷, 자동 백업까지 확인한다. 다음 수업에서 사용할 예정이므로 지금은 삭제하지 않는다.

## 확인 과제

1. RDS 퍼블릭 접근을 비활성화해도 Django가 연결할 수 있는 이유를 적는다.
2. 데이터베이스 비밀번호를 `settings.py`에 직접 적지 않는 이유를 두 가지 적는다.
3. PostgreSQL 네트워크와 인증 문제를 각각 확인하는 명령을 적는다.

<details>
<summary>정답 예시</summary>

1. 같은 VPC의 EC2에서 RDS 프라이빗 주소로 접근하고 RDS 보안 그룹이 EC2 보안 그룹을 허용하기 때문이다.
2. Git 이력이나 소스 배포본에 비밀번호가 남는 것을 막고 환경마다 다른 값을 코드 수정 없이 적용하기 위해서이다.
3. 네트워크 응답은 `pg_isready`로 확인하고 실제 인증은 `psql` 접속으로 확인한다.

</details>
