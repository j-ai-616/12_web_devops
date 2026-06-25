# 예제 Django 프로젝트와 컨테이너 이미지

## 학습 목표

- 제공된 Django 프로젝트의 URL, View, Template과 Test 구조를 설명할 수 있다.
- Windows에서 프로젝트를 실행하고 기능을 수정할 수 있다.
- 테스트를 통과한 프로젝트만 Docker 이미지로 만들 수 있다.
- 이미지와 실행 중인 컨테이너의 설정을 관찰할 수 있다.

## 1. 제공 프로젝트의 역할

`05_docker/cloud-class-app`에는 이후 AWS에 배포할 예제 프로젝트가 들어 있다. 이 프로젝트를 Windows의 VS Code로 열어 사용한다.

```text
05_docker/cloud-class-app
  -> Windows에서 프로젝트 열기
  -> 코드 구조 확인
  -> 로컬 테스트
  -> 기능 수정과 재테스트
  -> Docker 이미지 빌드
  -> Compose 실행
  -> GitHub Actions와 AWS 배포
```

앞 단계에서 EC2에 직접 만든 프로젝트는 Nginx, Gunicorn과 systemd의 관계를 이해하기 위한 수동 배포 결과이다. 제공 프로젝트는 Windows에서 개발하고 Docker와 CI/CD에서 계속 사용하는 소스 코드의 기준이다.

## 2. 로컬 Python 환경 준비

Windows에 설치한 Miniconda와 VS Code의 CMD 터미널을 사용한다. `conda activate`가 동작하지 않으면 한 번만 `conda init cmd.exe`를 실행한 뒤 VS Code 터미널을 닫고 새 CMD 터미널을 연다.

```bat
REM Python 3.12를 사용하는 로컬 개발 환경을 만든다.
conda create -n cloud-class-local python=3.12 -y

REM 로컬 개발 환경을 활성화한다.
conda activate cloud-class-local

REM 프로젝트에 기록된 Windows용 Python 패키지를 설치한다.
python -m pip install -r requirements.txt

REM Windows에서 사용할 Python과 Django 버전을 확인한다.
python --version
python -m django --version

REM 로컬 실행용 환경 변수 파일을 만든다.
copy .env.example .env.local
```

`.env.example`에는 비밀값이 아닌 예시만 들어 있다. `.env.local`은 Git과 Docker 이미지에서 제외된다.

Gunicorn은 Linux에서 동작하는 운영용 WSGI 서버이므로 Windows에서 직접 실행하지 않는다. Windows에서는 Django 개발 서버를 사용하고 Gunicorn은 Linux Docker 이미지를 빌드할 때 설치해 컨테이너 안에서 실행한다.

## 3. 프로젝트 구조 읽기

```bat
REM 프로젝트의 디렉터리와 파일 구조를 확인한다.
tree /F
```

```text
cloud-class-app/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── templates/core/index.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── deploy/deploy.sh
├── .github/workflows/deploy.yml
├── .gitattributes
├── Dockerfile
├── compose.yml
├── manage.py
└── requirements.txt
```

| 파일 | 역할 |
| --- | --- |
| `config/settings.py` | 환경 변수, 앱, 데이터베이스와 Django 전체 설정을 관리한다. |
| `config/urls.py` | 프로젝트의 최상위 URL을 연결한다. |
| `core/views.py` | HTML과 JSON 응답을 만드는 View 함수가 있다. |
| `core/tests.py` | 메인 화면과 API 동작을 자동으로 검사한다. |
| `Dockerfile` | Django 실행 이미지를 만드는 순서를 정의한다. |
| `compose.yml` | 이미지를 어떤 환경 변수와 포트로 실행할지 정의한다. |
| `deploy/deploy.sh` | ECR 이미지를 EC2에 배포하고 상태를 확인한다. |
| `.github/workflows/deploy.yml` | 테스트, 이미지 push와 SSM 배포 순서를 정의한다. |
| `.gitattributes` | Linux에서 실행할 셸 스크립트의 줄바꿈 형식을 고정한다. |

## 4. Django 요청 처리 흐름

프로젝트에는 세 URL이 준비되어 있다.

| URL | 응답 | 목적 |
| --- | --- | --- |
| `/` | HTML | 사용자가 보는 메인 화면이다. |
| `/health/` | JSON | 컨테이너와 배포 상태를 확인한다. |
| `/api/info/` | JSON | 서비스 이름, 실행 환경과 버전을 확인한다. |

```text
브라우저 요청
  -> config/urls.py
  -> core/urls.py
  -> core/views.py
  -> Template 또는 JsonResponse
  -> HTTP 응답
```

VS Code로 프로젝트를 열고 관련 파일을 함께 확인한다.

```bat
REM 현재 프로젝트를 VS Code로 연다.
code .
```

`code` 명령을 사용할 수 없다면 VS Code에서 `Open Folder`를 선택해 `cloud-class-app` 폴더를 연다.

## 5. 로컬 데이터베이스와 RDS 설정

`config/settings.py`는 `DB_HOST` 환경 변수에 따라 데이터베이스를 선택한다.

```text
DB_HOST 없음 -> 로컬 SQLite
DB_HOST 있음 -> RDS PostgreSQL
```

로컬 개발에서는 별도의 데이터베이스 서버 없이 SQLite를 사용한다. EC2에서는 `/etc/cloud-class.env`의 RDS 정보를 주입해 같은 코드와 이미지로 PostgreSQL에 연결한다.

환경에 따라 달라지는 주소와 비밀번호를 코드에 고정하지 않는 것이 중요하다.

## 6. 첫 번째 품질 검사

Docker 이미지를 만들기 전에 로컬 Python 환경에서 먼저 검사한다.

```bat
REM Django 설정과 URL 구성을 검사한다.
python manage.py check

REM 로컬 SQLite에 Django 기본 테이블을 만든다.
python manage.py migrate

REM 메인 화면과 두 API의 전체 테스트를 실행한다.
python manage.py test
```

성공 결과는 다음과 비슷하다.

```text
Ran 3 tests in ...
OK
```

테스트가 실패하면 이미지 빌드로 넘어가지 않는다. 실패한 테스트 이름, 예상값과 실제값을 확인하고 코드를 수정한 뒤 다시 실행한다.

## 7. 로컬 개발 서버 확인

`.env.local`은 이후 Docker Compose가 읽는 파일이다. Django 자체는 이 파일을 자동으로 읽지 않으므로 Windows에서 개발 서버를 실행할 때는 현재 CMD 세션에 환경 변수를 지정한다.

```bat
REM 현재 CMD 세션에 로컬 개발용 환경 변수를 지정한다.
set "DJANGO_SECRET_KEY=local-development-key"
set "DJANGO_DEBUG=True"
set "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1"
set "APP_ENV=windows-local"
set "APP_VERSION=dev"

REM Django 개발 서버를 로컬 8000번 포트에서 실행한다.
python manage.py runserver 127.0.0.1:8000
```

다른 터미널에서 세 URL을 확인한다.

```bat
REM HTML 메인 화면의 응답 헤더를 확인한다.
curl.exe -I http://127.0.0.1:8000/

REM 상태 확인 API를 호출한다.
curl.exe http://127.0.0.1:8000/health/

REM 애플리케이션 정보 API를 호출한다.
curl.exe http://127.0.0.1:8000/api/info/
```

브라우저에서 `http://127.0.0.1:8000`을 열어 메인 화면을 확인한다. 확인 후 개발 서버 터미널에서 `Ctrl+C`를 누른다.

## 8. 기능을 수정하고 테스트도 함께 변경

VS Code에서 `core/templates/core/index.html`의 소개 문장을 다음처럼 변경한다.

```html
<p>테스트를 통과한 Django 애플리케이션을 컨테이너로 실행한다.</p>
```

화면 문구가 바뀌면 기존 테스트의 기대값도 달라진다. 먼저 테스트를 실행해 실패를 확인한다.

```bat
REM 기존 테스트가 변경된 화면을 감지하는지 확인한다.
python manage.py test
```

`core/tests.py`의 메인 화면 기대 문자열을 새 문장에 맞게 변경한다.

```python
self.assertContains(response, "테스트를 통과한 Django 애플리케이션")
```

```bat
REM 변경한 기능과 테스트가 함께 성공하는지 확인한다.
python manage.py test
```

이 과정은 테스트를 맞추기 위해 무조건 기대값을 바꾸는 연습이 아니다. 화면 변경이 의도한 요구사항인지 먼저 판단한 뒤 테스트도 같은 요구사항을 표현하도록 수정한다.

## 9. Dockerfile 읽기

```bat
REM 이미지 빌드 순서를 줄 번호와 함께 확인한다.
findstr /n "^.*" Dockerfile
```

| 명령 | 실행 시점 | 역할 |
| --- | --- | --- |
| `FROM` | 빌드 | 기반 이미지를 선택한다. |
| `WORKDIR` | 빌드·실행 | 이후 명령의 기준 디렉터리를 정한다. |
| `RUN` | 빌드 | 패키지 설치처럼 이미지에 남길 작업을 수행한다. |
| `COPY` | 빌드 | Build Context의 파일을 이미지에 복사한다. |
| `USER` | 빌드·실행 | 이후 명령과 기본 실행 사용자를 정한다. |
| `EXPOSE` | 빌드 | 컨테이너가 사용할 포트를 문서화한다. |
| `HEALTHCHECK` | 실행 | 실행 중인 컨테이너 상태를 검사한다. |
| `CMD` | 실행 | 컨테이너의 기본 주 프로세스를 시작한다. |

`docker build .`의 마지막 `.`은 Build Context이다. Docker는 이 범위 안의 파일만 `COPY`할 수 있다. `.dockerignore`는 비밀값과 불필요한 파일을 Build Context에서 제외한다.

## 10. 테스트 성공 후 이미지 빌드

```bat
REM 이미지 빌드 직전에 Django 설정을 다시 검사한다.
python manage.py check

REM 전체 테스트를 다시 실행한다.
python manage.py test

REM 테스트가 성공한 현재 프로젝트로 이미지를 만든다.
docker build -t cloud-class-app:local .

REM 이미지의 태그와 크기를 확인한다.
docker image ls cloud-class-app
```

## 11. 이미지 레이어와 설정 관찰

```bat
REM Dockerfile 명령마다 만들어진 이미지 계층을 확인한다.
docker history cloud-class-app:local

REM 이미지의 사용자, 포트와 실행 명령을 확인한다.
docker image inspect cloud-class-app:local ^
  --format "User={{.Config.User}} Ports={{json .Config.ExposedPorts}} Cmd={{json .Config.Cmd}}"
```

`requirements.txt`를 소스 코드보다 먼저 복사하면 소스만 바뀌었을 때 패키지 설치 레이어의 캐시를 재사용할 수 있다. 패키지 목록이 바뀌면 해당 레이어부터 다시 빌드한다.

## 12. 컨테이너 실행과 기능 확인

```bat
REM 로컬 환경 변수 파일을 주입해 컨테이너를 실행한다.
docker run -d ^
  --name cloud-class-web ^
  --env-file .env.local ^
  -p 127.0.0.1:8000:8000 ^
  cloud-class-app:local

REM 컨테이너 상태와 건강 상태를 확인한다.
docker ps --filter name=cloud-class-web

REM 로컬 포트와 컨테이너 포트의 연결을 확인한다.
docker port cloud-class-web

REM 컨테이너의 Gunicorn 프로세스를 확인한다.
docker top cloud-class-web

REM 메인 화면과 두 API를 확인한다.
curl.exe -I http://127.0.0.1:8000/
curl.exe http://127.0.0.1:8000/health/
curl.exe http://127.0.0.1:8000/api/info/

REM Gunicorn과 Django 로그를 확인한다.
docker logs cloud-class-web
```

## 13. 컨테이너 내부에서도 테스트

로컬 Python 환경과 이미지 내부의 패키지 구성이 다를 수 있으므로 컨테이너 안에서도 검사한다.

```bat
REM 실행 중인 컨테이너에서 Django 설정을 검사한다.
docker exec cloud-class-web python manage.py check

REM 실행 중인 컨테이너에서 전체 테스트를 실행한다.
docker exec cloud-class-web python manage.py test

REM 이미지와 비교해 컨테이너에서 변경된 파일을 확인한다.
docker diff cloud-class-web

REM 확인이 끝난 컨테이너를 삭제한다.
docker rm -f cloud-class-web
```

로컬 테스트, 이미지 빌드와 컨테이너 테스트가 모두 성공해야 배포 가능한 이미지로 판단한다.

## 14. 로컬 Git 저장소 시작

제공 프로젝트에는 `.git` 디렉터리가 포함되어 있지 않다.

```bat
REM 현재 디렉터리를 main 브랜치의 Git 저장소로 만든다.
git init -b main

REM 비밀값과 로컬 DB가 제외되는지 확인한다.
git status --short --ignored

REM 테스트를 통과한 프로젝트를 첫 커밋으로 기록한다.
git add .
git commit -m "feat: add tested Django cloud app"
```

`.env.local`과 `db.sqlite3`가 커밋 목록에 없어야 한다. `.gitattributes`는 Windows에서 작성한 `deploy.sh`가 Git에 LF 줄바꿈으로 저장되게 한다. EC2의 Bash는 LF 형식의 스크립트를 그대로 실행할 수 있다.

## 확인 과제

1. EC2가 아니라 Windows의 프로젝트를 소스 코드의 기준으로 삼는 이유를 적는다.
2. `RUN`과 `CMD`가 실행되는 시점의 차이를 적는다.
3. Docker 이미지를 만들기 전에 실행해야 하는 두 Django 명령을 적는다.

<details>
<summary>정답 예시</summary>

1. 로컬 코드를 소스의 기준으로 삼고 테스트된 결과만 배포하기 위해서이다.
2. `RUN`은 이미지를 빌드할 때 실행되어 결과가 레이어에 남고 `CMD`는 컨테이너를 시작할 때 주 프로세스로 실행된다.
3. `python manage.py check`와 `python manage.py test`이다.

</details>
