# Django 수동 배포

## 학습 목표

- EC2에 Miniconda 별도 환경을 만들 수 있다.
- Django 개발 서버, WSGI와 Gunicorn의 역할을 구분할 수 있다.
- WSGI와 ASGI의 차이를 설명할 수 있다.
- systemd로 Gunicorn 프로세스를 관리할 수 있다.
- Nginx를 리버스 프록시로 구성할 수 있다.
- 로그를 이용해 요청 경로의 문제를 찾을 수 있다.

## 1. 최종 요청 경로

```text
브라우저
  -> EC2 보안 그룹 80번 허용
  -> Nginx :80
  -> Gunicorn 127.0.0.1:8000
  -> Django WSGI 애플리케이션
```

Django의 `runserver`는 개발 편의를 위한 서버이다. 외부 요청을 직접 받는 운영 구조에서는 Gunicorn 같은 애플리케이션 서버를 사용한다. Nginx는 외부 연결, 정적 파일, 프록시 헤더를 처리한다.

### 배포 구성 요소를 나누는 이유

Django는 URL, 데이터베이스, 화면과 비즈니스 로직을 다루는 웹 프레임워크이다. 인터넷 연결 관리, 프로세스 재시작, 정적 파일 전송까지 모두 Django 한 프로그램에 맡기지 않고 역할에 맞는 도구로 나눈다.

| 계층 | 도구 | 담당하는 일 |
| --- | --- | --- |
| 웹 프레임워크 | Django | 요청에 맞는 Python 코드를 실행하고 응답을 만든다. |
| 애플리케이션 서버 | Gunicorn | Django 프로세스를 실행하고 HTTP 요청을 WSGI 호출로 전달한다. |
| 프로세스 관리자 | systemd | Gunicorn을 백그라운드에서 실행하고 재시작한다. |
| 웹 서버 | Nginx | 외부 HTTP 연결, 정적 파일, 리버스 프록시를 처리한다. |

이렇게 분리하면 Nginx가 정상인지, Gunicorn이 실행 중인지, Django 코드에서 오류가 났는지를 계층별로 확인할 수 있다.

### WSGI와 ASGI

Python 웹 프레임워크와 애플리케이션 서버가 요청과 응답을 주고받으려면 공통 규칙이 필요하다. 이 연결 규칙이 WSGI 또는 ASGI이다.

| 구분 | WSGI | ASGI |
| --- | --- | --- |
| 처리 모델 | 동기 요청·응답 중심 | 비동기 처리 지원 |
| 적합한 기능 | 일반적인 웹 페이지와 REST API | WebSocket, 실시간 알림, 긴 연결 |
| 대표 서버 | Gunicorn | Uvicorn, Daphne |
| Django 진입점 | `config/wsgi.py` | `config/asgi.py` |

WSGI는 한 요청을 받아 응답을 돌려주는 전통적인 웹 처리 방식에 적합하다. ASGI는 요청을 기다리는 동안 다른 작업을 처리할 수 있고 WebSocket처럼 연결을 오래 유지하는 기능도 다룬다. 이번 애플리케이션은 일반 HTTP 요청만 사용하므로 WSGI와 Gunicorn으로 배포한다.

### Gunicorn이 하는 일

Gunicorn은 Python 웹 애플리케이션을 실행하는 WSGI 애플리케이션 서버이다. 브라우저에서 받은 요청을 Python이 이해할 수 있는 WSGI 형식으로 Django에 전달하고, Django가 만든 응답을 다시 HTTP 응답으로 돌려준다. Django 프레임워크나 데이터베이스를 대신하는 프로그램은 아니다.

| 구성 요소 | 이 수업에서 하는 일 |
| --- | --- |
| Nginx | 인터넷의 80번 포트에서 요청을 받고 정적 파일 처리와 리버스 프록시를 담당한다. |
| Gunicorn | 여러 Python 작업자 프로세스를 실행하고 Django WSGI 애플리케이션에 요청을 전달한다. |
| Django | URL을 해석하고 비즈니스 로직을 실행해 응답을 만든다. |
| systemd | Gunicorn을 백그라운드에서 시작하고 장애나 재부팅 후 다시 실행한다. |

`config.wsgi:application`은 `config/wsgi.py` 모듈의 `application` 객체를 실행하라는 뜻이다. `--workers 2`는 요청을 처리할 Gunicorn 작업자 프로세스를 2개 실행한다는 뜻이다. 이 수업에서는 외부 연결을 Nginx만 받게 하려고 Gunicorn을 `127.0.0.1:8000`에 묶는다.

## 2. Miniconda 설치

EC2에 SSH 접속한 상태에서 실행한다.

Miniconda는 Python 버전과 패키지를 프로젝트별 환경으로 분리하는 도구이다. 운영체제의 기본 Python에 패키지를 직접 설치하면 Ubuntu 관리 도구와 프로젝트 패키지가 섞일 수 있다. 별도 Conda 환경을 만들면 프로젝트에 필요한 Python과 라이브러리만 독립적으로 관리할 수 있다.

```bash
# 홈 디렉터리로 이동한다.
cd ~

# x86_64 Linux용 최신 Miniconda 설치 파일을 내려받는다.
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 설치 파일의 SHA256 체크섬을 출력한다.
# 공식 저장소(repo.anaconda.com/miniconda/)의 SHA256 값과 비교해
# 파일이 손상되거나 변조되지 않았는지 확인한다.
sha256sum Miniconda3-latest-Linux-x86_64.sh

# 홈 디렉터리의 miniconda3 경로에 대화 없이 설치한다.
bash Miniconda3-latest-Linux-x86_64.sh -b -p "$HOME/miniconda3"

# 현재 셸에서 conda 명령을 사용할 수 있게 초기화 스크립트를 불러온다.
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# Bash를 열 때 conda 명령을 사용할 수 있도록 셸 설정을 초기화한다.
conda init bash

# 설치된 conda 버전을 확인한다.
conda --version
```

설치 후 SSH에 다시 접속하거나 `source ~/.bashrc`를 실행한다.



```bash
# Anaconda 기본 채널의 Terms of Service 동의
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```


## 3. 배포용 Conda 환경 만들기

`base` 환경에 프로젝트 패키지를 설치하지 않는다. 프로젝트별 환경을 따로 만든다.

```bash
# Python 3.12를 사용하는 cloud-class 환경을 생성한다.
conda create -n cloud-class python=3.12 -y

# 생성한 환경을 현재 셸에서 활성화한다.
conda activate cloud-class

# 현재 Python 실행 파일이 cloud-class 환경에 있는지 확인한다.
which python

# Python과 pip 버전을 확인한다.
python --version
pip --version
```

`which python` 결과가 `/home/ubuntu/miniconda3/envs/cloud-class/bin/python`과 비슷해야 한다.

## 4. Django 프로젝트 만들기

Django에서 프로젝트는 웹 서비스 전체 설정을 담고, 앱은 회원·게시판·결제처럼 특정 기능을 묶는다. 이번 수동 배포에서는 구조를 단순하게 확인하기 위해 별도 앱 없이 프로젝트의 URL 설정에 상태 확인 함수를 작성한다. Docker 단계에서는 `core` 앱과 HTML 템플릿을 가진 프로젝트로 확장한다.

`django-admin`은 프로젝트 뼈대를 만들고, `manage.py`는 생성된 프로젝트의 검사·서버 실행·마이그레이션 같은 관리 작업을 수행한다.

```bash
# Django와 운영용 WSGI 서버 Gunicorn을 설치한다.
pip install django gunicorn

# 프로젝트를 저장할 디렉터리를 만든다.
mkdir -p ~/cloud-class-app

# 프로젝트 디렉터리로 이동한다.
cd ~/cloud-class-app

# 현재 디렉터리에 config 이름의 Django 프로젝트를 생성한다.
django-admin startproject config .

# 설치된 패키지 버전을 requirements.txt에 기록한다.
pip freeze > requirements.txt

# Django 기본 데이터베이스 구조를 생성한다.
python manage.py migrate

# 프로젝트 자체 검사 명령을 실행한다.
python manage.py check
```

## 5. 상태 확인 URL 만들기

`config/urls.py`를 다음과 같이 수정한다.

```python
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health(request):
    # 배포 후 애플리케이션 프로세스가 응답하는지 확인하는 경로이다.
    return JsonResponse({"status": "ok", "service": "cloud-class-app"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
]
```

## 6. 환경 변수 파일 만들기

비밀값을 코드와 Git 저장소에 넣지 않는다. 운영 환경 변수는 `/etc/cloud-class.env`에 둔다.

먼저 안전한 Django 비밀 키를 생성한다.

```bash
# Django가 제공하는 함수로 무작위 비밀 키를 생성한다.
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

출력값을 복사한 뒤 환경 변수 파일을 연다.

```bash
# root만 수정할 수 있는 운영 환경 변수 파일을 만든다.
sudo vi /etc/cloud-class.env
```

다음 내용을 입력한다. 예시 키 대신 방금 생성한 값을 사용하고 퍼블릭 DNS도 실제 값으로 바꾼다. `DJANGO_ALLOWED_HOSTS`에는 `http://`를 붙이지 않는다.

```dotenv
DJANGO_SECRET_KEY='방금_생성한_비밀_키'
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<EC2_PUBLIC_DNS>,127.0.0.1,localhost
```

```bash
# 환경 변수 파일은 root가 소유하되, ubuntu 사용자가 읽을 수 있게 그룹 권한을 설정한다.
# 8번 단계에서 ubuntu 사용자가 source 명령으로 이 파일을 읽어야 하기 때문이다.
sudo chown root:ubuntu /etc/cloud-class.env
sudo chmod 640 /etc/cloud-class.env

# 파일의 소유자와 권한만 확인하고 비밀값은 화면에 출력하지 않는다.
sudo stat -c '%U %G %a %n' /etc/cloud-class.env
```

정상 예시는 다음과 비슷하다.

```text
root ubuntu 640 /etc/cloud-class.env
```

## 7. Django 설정에서 환경 변수 읽기

`config/settings.py` 위쪽에 `import os`를 추가하고 기존 `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`를 다음 코드로 바꾼다.

```python
import os

# 비밀 키가 없으면 애플리케이션이 시작되지 않게 한다.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# 문자열 true만 개발 모드로 해석한다.
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

# 쉼표로 구분된 호스트 목록을 Django 리스트로 변환한다.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
```

정적 파일을 수집할 경로도 파일 아래쪽에 추가한다.

```python
# collectstatic 명령이 정적 파일을 모을 디렉터리이다.
STATIC_ROOT = BASE_DIR / "staticfiles"
```

## 8. 환경 변수를 읽어 Django 확인하기

systemd를 만들기 전 현재 셸에서 환경 변수를 임시로 불러온다.

```bash
# 환경 변수 파일의 각 줄을 현재 셸의 환경 변수로 내보낸다.
set -a
source /etc/cloud-class.env
set +a

# 환경 변수가 정상적으로 불러와졌는지 확인한다.
# 비밀값 자체를 출력하지 않고, 값이 존재하는지만 확인한다.
test -n "$DJANGO_SECRET_KEY" && echo "DJANGO_SECRET_KEY loaded"

# 환경 변수가 적용된 상태에서 Django 설정을 검사한다.
python manage.py check --deploy

# 운영 정적 파일을 staticfiles 디렉터리에 수집한다.
python manage.py collectstatic --noinput
```

`check --deploy`의 경고는 HTTPS와 보안 쿠키처럼 이후에 적용할 항목을 알려 준다. 현재 HTTP 실습에서는 내용을 읽고 의미를 확인한다.

## 9. Gunicorn을 직접 실행해 보기

```bash
# Gunicorn으로 Django WSGI 애플리케이션을 로컬 8000번 포트에 실행한다.
gunicorn --bind 127.0.0.1:8000 config.wsgi:application
```

새 SSH 창을 하나 더 열고 EC2에 접속한 뒤 확인한다.

```bash
# EC2 내부에서 Gunicorn 상태 확인 URL을 호출한다.
curl http://127.0.0.1:8000/health/

# 8000번 포트를 듣는 프로세스를 확인한다.
sudo ss -lntp | grep ':8000'
```

JSON 응답이 보이면 Gunicorn과 Django는 정상이다. Gunicorn을 실행한 첫 번째 창에서 `Ctrl+C`를 눌러 종료한다.

## 10. systemd 서비스 만들기

systemd는 Gunicorn을 백그라운드 서비스로 실행하고 장애나 재부팅 후 다시 시작하게 한다.

터미널에서 Gunicorn을 직접 실행하면 SSH 연결을 끊거나 프로세스를 종료했을 때 서비스도 멈춘다. systemd에 서비스 정의를 등록하면 로그인한 터미널과 관계없이 운영체제가 프로세스를 관리한다.

```bash
# Gunicorn systemd 서비스 파일을 연다.
sudo vi /etc/systemd/system/cloud-class.service
```

다음 내용을 입력한다.

```ini
[Unit]
Description=Cloud Class Django Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/cloud-class-app
EnvironmentFile=/etc/cloud-class.env
ExecStart=/home/ubuntu/miniconda3/envs/cloud-class/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 config.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 새로 만든 서비스 파일을 systemd가 다시 읽게 한다.
sudo systemctl daemon-reload

# Gunicorn 서비스를 시작하고 부팅 시 자동 시작하게 설정한다.
sudo systemctl enable --now cloud-class

# Gunicorn 서비스 상태를 확인한다.
sudo systemctl status cloud-class

# EC2 내부에서 서비스 응답을 확인한다.
curl http://127.0.0.1:8000/health/
```

Conda 환경을 `activate`하지 않아도 `ExecStart`가 해당 환경의 Gunicorn 절대 경로를 사용하므로 정상 실행된다.

## 11. Nginx 리버스 프록시 설정

기본 사이트 대신 프로젝트 전용 설정을 만든다.

리버스 프록시는 외부 요청을 먼저 받은 뒤 내부 서버에 대신 전달하는 구성이다. 브라우저는 Nginx의 80번 포트만 알고, Gunicorn의 8000번 포트는 EC2 내부에서만 사용한다. 외부 접점이 하나로 모이므로 TLS, 접근 로그, 정적 파일과 요청 크기 제한을 Nginx에서 공통으로 처리할 수 있다.

```bash
# cloud-class 전용 Nginx 사이트 설정 파일을 연다.
sudo vi /etc/nginx/sites-available/cloud-class
```

다음 내용을 입력한다.

```nginx
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /home/ubuntu/cloud-class-app/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# sites-enabled에 설정 파일의 심볼릭 링크를 만든다.
sudo ln -s /etc/nginx/sites-available/cloud-class /etc/nginx/sites-enabled/cloud-class

# Ubuntu 기본 Nginx 사이트 링크를 제거한다.
sudo rm /etc/nginx/sites-enabled/default

# Nginx 설정 파일의 문법을 검사한다.
sudo nginx -t

# 문법 검사가 성공한 경우 Nginx 설정을 다시 불러온다.
sudo systemctl reload nginx
```

`nginx -t`가 실패하면 재시작하지 말고 표시된 파일과 줄 번호를 수정한다.

## 12. 전체 경로 확인

EC2 내부에서 계층별로 확인한다.

```bash
# Django와 Gunicorn 계층에 직접 요청한다.
curl http://127.0.0.1:8000/health/

# Nginx를 거쳐 같은 URL에 요청한다.
curl http://127.0.0.1/health/

# Nginx와 Gunicorn 서비스가 모두 실행 중인지 한 줄씩 확인한다.
systemctl is-active nginx
systemctl is-active cloud-class
```

Windows 브라우저에서 다음 주소를 연다.

```text
http://<EC2_PUBLIC_DNS>/health/
```

다음과 비슷한 응답이 보이면 성공이다.

```json
{"status": "ok", "service": "cloud-class-app"}
```

## 13. 로그 확인

```bash
# Gunicorn 서비스의 최근 로그 50줄을 확인한다.
sudo journalctl -u cloud-class -n 50 --no-pager

# Gunicorn 로그를 실시간으로 관찰한다.
sudo journalctl -u cloud-class -f

# Nginx 접근 로그의 최근 요청을 확인한다.
sudo tail -n 30 /var/log/nginx/access.log

# Nginx 오류 로그의 최근 내용을 확인한다.
sudo tail -n 30 /var/log/nginx/error.log
```

실시간 로그 화면은 `Ctrl+C`로 종료한다.

## 14. 재부팅 후 자동 시작 확인

```bash
# EC2 운영체제를 재부팅한다. SSH 연결이 끊기는 것이 정상이다.
sudo reboot
```

1분 정도 뒤 다시 SSH로 접속한다.

```bash
# 재부팅 후 Nginx와 Django 서비스 상태를 확인한다.
systemctl is-active nginx
systemctl is-active cloud-class

# Nginx를 거친 상태 확인 URL을 호출한다.
curl http://127.0.0.1/health/
```

두 서비스가 `active`이면 자동 시작 설정이 정상이다.

## 15. 문제 해결

### Nginx에서 `502 Bad Gateway`가 나온다

```bash
# Gunicorn 서비스가 실행 중인지 확인한다.
sudo systemctl status cloud-class

# 8000번 포트가 열려 있는지 확인한다.
sudo ss -lntp | grep ':8000'

# Gunicorn 시작 실패 원인을 로그에서 확인한다.
sudo journalctl -u cloud-class -n 100 --no-pager
```

### `DisallowedHost`가 나온다

`/etc/cloud-class.env`의 `DJANGO_ALLOWED_HOSTS`에 현재 퍼블릭 IPv4 DNS가 있는지 확인하고 서비스를 다시 시작한다.

```bash
# 환경 변수 변경 내용을 반영하도록 Gunicorn 서비스를 재시작한다.
sudo systemctl restart cloud-class
```

### Nginx 설정 문법이 잘못되었다

```bash
# Nginx 설정 문법과 오류 줄 번호를 다시 확인한다.
sudo nginx -t
```

## 확인 과제

1. Gunicorn을 `127.0.0.1:8000`에 바인딩한 이유를 적는다.
2. systemd 서비스에서 `conda activate`가 없어도 되는 이유를 적는다.
3. `502 Bad Gateway`가 발생했을 때 가장 먼저 확인할 두 가지를 적는다.

<details>
<summary>정답 예시</summary>

1. 외부에서 Gunicorn에 직접 접근하지 못하게 하고 Nginx를 통해서만 요청을 받기 위해서이다.
2. `ExecStart`에 Conda 환경 내부 Gunicorn의 절대 경로를 지정했기 때문이다.
3. `cloud-class` 서비스 상태와 `127.0.0.1:8000` 포트의 리스닝 상태를 확인한다.

</details>
