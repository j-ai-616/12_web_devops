# 제공 프로젝트의 Docker Compose

## 학습 목표

- Dockerfile과 Compose가 해결하는 문제를 구분할 수 있다.
- 제공된 `compose.yml`의 서비스, 환경 변수, 포트와 상태 검사를 설명할 수 있다.
- Compose 이미지 안에서 검사와 테스트를 실행할 수 있다.
- 로컬과 EC2가 같은 Compose 구조를 사용하는 방법을 설명할 수 있다.

## 1. Compose가 필요한 이유

`docker run` 명령이 길어지면 포트, 환경 변수, 재시작 정책과 상태 검사 옵션을 빠뜨리기 쉽다. Compose는 컨테이너 실행 방법을 YAML 파일에 선언해 같은 설정을 반복해서 사용할 수 있게 한다.

```text
Dockerfile  -> 이미지를 어떻게 만들 것인가
compose.yml -> 이미지를 어떤 설정으로 실행할 것인가
```

Compose는 Docker Engine을 대신하지 않는다. Compose가 `up`, `down`, `logs` 같은 명령을 해석하고 Docker Engine에 여러 컨테이너 작업을 요청한다.

## 2. 제공된 Compose 파일 읽기

VS Code에서 `cloud-class-app` 폴더를 열고 CMD 터미널을 실행한다.

```bat
REM 현재 터미널이 프로젝트 루트에 있는지 확인한다.
cd

REM Compose 파일을 줄 번호와 함께 확인한다.
findstr /n "^.*" compose.yml
```

제공된 `compose.yml`에는 `web` 서비스 하나가 정의되어 있다.

| 설정 | 의미 |
| --- | --- |
| `build.context: .` | 현재 프로젝트를 Build Context로 사용한다. |
| `image` | 로컬 기본 이미지 또는 `APP_IMAGE`로 지정한 ECR 이미지를 사용한다. |
| `env_file` | 로컬 또는 EC2 환경 변수 파일을 컨테이너에 전달한다. |
| `ports` | 호스트 8000번을 컨테이너 8000번에 연결한다. |
| `restart` | Docker 재시작 뒤 컨테이너 실행 정책을 정한다. |
| `healthcheck` | 컨테이너 내부의 `/health/` 응답을 주기적으로 확인한다. |

## 3. 변수 기본값 이해하기

`compose.yml`은 다음 두 변수에 기본값을 사용한다.

```text
APP_IMAGE가 없음    -> cloud-class-app:local
APP_ENV_FILE이 없음 -> .env.local
```

로컬에서는 별도 변수를 지정하지 않아도 된다. EC2에서는 `APP_IMAGE`에 ECR URI를, `APP_ENV_FILE`에 `/etc/cloud-class.env`를 지정한다.

```bat
REM 변수 치환이 끝난 최종 Compose 구성을 출력한다.
docker compose config
```

출력에서 이미지, 환경 파일, 포트와 상태 검사 URL을 확인한다. YAML 들여쓰기나 변수 이름이 잘못되면 컨테이너를 실행하기 전에 이 명령에서 오류를 발견할 수 있다.

## 4. 환경 변수 파일과 이미지 분리

`.env.local`은 로컬 실행용 값이고 이미지 안에 복사되지 않는다.

```bat
REM 로컬 환경 변수 파일의 경로와 정보를 확인한다.
dir .env.local

REM .env.local이 Git과 Docker Build Context에서 제외되는지 확인한다.
git status --short --ignored .env.local
findstr /n /b /l /c:".env" .gitignore .dockerignore
```

비밀값을 Dockerfile의 `ENV`나 `ARG`에 넣으면 이미지 메타데이터나 빌드 기록에 남을 수 있다. 실행 시점에 환경 변수 파일로 주입하면 같은 이미지를 여러 환경에서 사용할 수 있다.

## 5. 테스트 후 Compose 이미지 빌드

```bat
REM 로컬 Conda 환경을 활성화한다.
conda activate cloud-class-local

REM 로컬 Django 설정을 검사한다.
python manage.py check

REM 로컬 전체 테스트를 실행한다.
python manage.py test

REM compose.yml의 build 설정으로 이미지를 만든다.
docker compose build

REM 새 컨테이너에서 Django 설정을 검사하고 종료한다.
docker compose run --rm web python manage.py check

REM 새 컨테이너에서 전체 테스트를 실행하고 종료한다.
docker compose run --rm web python manage.py test
```

로컬 검사, 로컬 테스트, 컨테이너 검사와 컨테이너 테스트 중 하나라도 실패하면 `docker compose up`을 실행하지 않는다.

## 6. Compose로 애플리케이션 실행

```bat
REM Compose 정의에 따라 web 서비스를 백그라운드 실행한다.
docker compose up -d

REM 서비스와 컨테이너 건강 상태를 확인한다.
docker compose ps

REM 메인 HTML과 두 JSON API를 확인한다.
curl.exe -I http://127.0.0.1:8000/
curl.exe http://127.0.0.1:8000/health/
curl.exe http://127.0.0.1:8000/api/info/
```

브라우저에서 `http://127.0.0.1:8000`을 연다. 환경은 `.env.local`의 `APP_ENV`, 버전은 `APP_VERSION` 값으로 표시된다.

## 7. Compose가 만든 자원 관찰

```bat
REM Compose 프로젝트의 서비스 상태를 확인한다.
docker compose ps

REM Compose가 만든 컨테이너의 상세 설정을 확인한다.
docker inspect cloud-class-web

REM web 서비스의 최근 로그 50줄을 확인한다.
docker compose logs --tail 50 web

REM web 컨테이너 안의 주 프로세스와 작업자 프로세스를 확인한다.
docker compose top web

REM Compose가 만든 네트워크를 확인한다.
docker network ls --filter name=cloud-class
```

Compose는 기본적으로 프로젝트 전용 네트워크를 만든다. 현재 서비스는 하나지만 여러 서비스가 있으면 서비스 이름을 DNS 이름처럼 사용해 같은 Compose 네트워크에서 통신할 수 있다.

## 8. 선언 변경과 컨테이너 재생성

VS Code에서 `.env.local`의 `APP_VERSION`을 `compose-v2`로 변경하고 저장한다.

```bat
REM 변경된 환경 변수로 web 컨테이너를 다시 만든다.
docker compose up -d --force-recreate web

REM 새 버전 값이 적용되었는지 확인한다.
curl.exe http://127.0.0.1:8000/api/info/
```

이미지는 그대로이고 컨테이너 실행 설정만 달라졌다. 이미지를 다시 빌드해야 하는 변경과 컨테이너만 다시 만들어도 되는 변경을 구분해야 한다.

| 변경 내용 | 필요한 작업 |
| --- | --- |
| Python 코드, `requirements.txt`, Dockerfile | 이미지 재빌드 후 컨테이너 교체 |
| 환경 변수, 포트, 재시작 정책 | 컨테이너 재생성 |
| RDS 데이터 | 애플리케이션 컨테이너와 별도 관리 |

## 9. Compose 운영 명령

```bat
REM web 서비스 로그를 실시간으로 확인한다.
docker compose logs -f web

REM 실행 중인 컨테이너에서 Django 검사를 실행한다.
docker compose exec web python manage.py check

REM 컨테이너를 중지하고 Compose 네트워크를 제거한다.
docker compose down

REM 같은 선언으로 서비스를 다시 실행한다.
docker compose up -d
```

실시간 로그는 `Ctrl+C`로 종료한다. 로그 화면을 종료해도 컨테이너는 계속 실행된다.

## 10. EC2 배포 계약

EC2에서는 로컬 소스 코드를 다시 작성하지 않는다.

| 요소 | 역할 |
| --- | --- |
| ECR 이미지 | 테스트를 통과한 Django 코드와 실행 환경이다. |
| `compose.yml` | 이미지, 포트, 상태 검사와 재시작 방법이다. |
| `/etc/cloud-class.env` | RDS 주소, 비밀번호와 운영 환경 변수이다. |
| `deploy/deploy.sh` | 이미지 pull, 마이그레이션, 교체와 HTTP 확인을 수행한다. |

EC2에서는 다음 형태로 Compose가 실행된다.

```bash
# 실제 값은 CI/CD 배포 스크립트가 지정한다.
APP_IMAGE=<ECR_IMAGE_URI> \
APP_ENV_FILE=/etc/cloud-class.env \
docker compose up -d --no-build
```

위 명령은 Windows에서 실행하는 로컬 명령이 아니라 EC2의 Linux 환경에서 배포 스크립트가 사용하는 형태이다.

로컬 `.env.local`은 EC2로 복사하지 않고 `/etc/cloud-class.env`는 GitHub나 이미지에 넣지 않는다.

## 11. x86_64 배포 이미지 확인

Windows PC가 ARM64이거나 다른 CPU 환경에서 작업하더라도 x86_64 EC2에서 실행할 이미지는 `linux/amd64` 플랫폼으로 만든다.

```bat
REM x86_64 EC2용 이미지를 만들고 로컬 Docker Engine에 적재한다.
docker buildx build ^
  --platform linux/amd64 ^
  --tag cloud-class-app:amd64-test ^
  --load ^
  .

REM 이미지의 운영체제와 CPU 아키텍처를 확인한다.
docker image inspect cloud-class-app:amd64-test ^
  --format "OS={{.Os}} Architecture={{.Architecture}}"
```

로컬 CPU와 대상 플랫폼이 다르면 에뮬레이션 때문에 빌드와 실행이 느릴 수 있다. 최종 배포 이미지는 GitHub Actions의 AMD64 Linux Runner에서 다시 만든다.

## 12. 변경 내용 커밋

```bat
REM 비밀값 파일이 포함되지 않았는지 확인한다.
git status --short --ignored

REM 기능 변경과 Compose 설정을 커밋한다.
git add core compose.yml Dockerfile .dockerignore .gitignore .gitattributes requirements.txt
git commit -m "build: verify Docker Compose application"
```

`.env.local`과 `db.sqlite3`가 커밋 목록에 없어야 한다.

## 13. 로컬 컨테이너 정리

```bat
REM Compose 컨테이너와 네트워크를 제거한다.
docker compose down

REM 실행 중인 수업 컨테이너가 남았는지 확인한다.
docker ps --filter name=cloud-class
```

이미지는 CI/CD 과정에서 다시 사용하므로 삭제하지 않는다.

## 확인 과제

1. Dockerfile과 `compose.yml`의 역할 차이를 적는다.
2. 로컬과 EC2에서 서로 다른 환경 변수 파일을 사용하는 이유를 적는다.
3. 소스 코드 변경과 환경 변수 변경에 필요한 작업 차이를 적는다.

<details>
<summary>정답 예시</summary>

1. Dockerfile은 이미지를 만드는 방법이고 `compose.yml`은 이미지를 어떤 설정으로 실행할지 정의한다.
2. 실행 환경마다 주소와 비밀값은 다르지만 같은 이미지를 재사용하기 위해서이다.
3. 소스 코드 변경은 이미지를 다시 빌드해야 하고 환경 변수 변경은 같은 이미지로 컨테이너만 다시 만들면 된다.

</details>
