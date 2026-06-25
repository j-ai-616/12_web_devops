# 로컬 Docker 기초

## 학습 목표

- 가상 머신과 컨테이너의 차이를 설명할 수 있다.
- 이미지, 컨테이너, Dockerfile과 레지스트리의 관계를 설명할 수 있다.
- 이미지 레이어, 빌드 캐시와 컨테이너 주 프로세스를 설명할 수 있다.
- 볼륨과 바인드 마운트의 차이를 설명할 수 있다.
- 로컬 PC에서 컨테이너를 실행하고 로그와 포트를 확인할 수 있다.
- Windows와 macOS의 CPU 아키텍처 차이가 이미지 빌드에 미치는 영향을 설명할 수 있다.

## 1. 개발 위치 변경

앞 단계에서는 배포 구조를 이해하기 위해 EC2에 직접 접속해 Django와 Nginx를 구성했다. 실제 개발에서는 서버의 파일을 직접 수정하기보다 로컬 PC에서 코드를 작성하고 테스트한 결과를 서버에 배포한다.

```text
[앞 단계]
EC2 접속 -> EC2에서 코드 수정 -> EC2에서 실행

[이후 단계]
로컬에서 코드 수정 -> 로컬 테스트 -> 이미지 생성 -> AWS 배포
```

이제부터 Django 소스의 기준은 로컬 프로젝트 폴더이다. EC2는 코드를 작성하는 장소가 아니라 검증된 결과를 실행하는 배포 대상이 된다.

## 2. Docker가 해결하는 문제

Python 애플리케이션은 코드만으로 실행되지 않는다. Python 버전, 시스템 라이브러리, Python 패키지와 실행 명령이 함께 맞아야 한다. 개발 PC와 서버의 환경이 다르면 로컬에서는 성공한 코드가 서버에서 실패할 수 있다.

Docker는 애플리케이션 실행에 필요한 파일과 설정을 이미지로 묶는다. 같은 이미지를 로컬과 EC2에서 실행하면 설치 환경의 차이를 줄일 수 있다.

Docker가 코드 오류, 데이터베이스 운영, 비밀값 관리까지 해결하는 것은 아니다. 테스트와 환경 변수, 로그와 배포 절차는 별도로 설계해야 한다.

## 3. 가상 머신과 컨테이너

| 항목 | 가상 머신 | 컨테이너 |
| --- | --- | --- |
| 격리 단위 | 운영체제 전체 | 프로세스와 파일 시스템 |
| 커널 | 게스트 운영체제마다 별도 커널 | 호스트의 Linux 커널 공유 |
| 시작 속도 | 상대적으로 느림 | 상대적으로 빠름 |
| 이미지 크기 | 대체로 큼 | 대체로 작음 |
| 이 과정의 예 | EC2 | Django Docker 컨테이너 |

Windows와 macOS는 Linux 커널을 직접 사용하지 않는다. Docker Desktop은 내부에 작은 Linux 가상 머신을 실행하고 그 안에서 Linux 컨테이너를 실행한다. WSL에서 `docker` 명령을 입력해도 실제 컨테이너 실행은 Docker Desktop의 Docker Engine이 담당한다.

## 4. Docker 핵심 구성 요소

| 용어 | 의미 |
| --- | --- |
| Dockerfile | 이미지를 만드는 순서와 실행 방법을 적은 파일이다. |
| 이미지 | 애플리케이션 실행 환경을 담은 읽기 전용 템플릿이다. |
| 컨테이너 | 이미지를 실제 프로세스로 실행한 상태이다. |
| Docker Engine | 이미지와 컨테이너를 관리하는 백그라운드 프로그램이다. |
| Docker CLI | 사용자가 `docker` 명령으로 Engine에 요청을 보내는 도구이다. |
| 레지스트리 | 이미지를 저장하고 다른 컴퓨터에 배포하는 서버이다. |

```text
Dockerfile
  -> docker build
  -> 이미지
  -> docker run
  -> 컨테이너
```

이미지는 실행할 때 바뀌지 않는다. 컨테이너에서 생긴 변경은 컨테이너 쓰기 계층에 저장되며 컨테이너를 삭제하면 함께 사라질 수 있다. 유지해야 하는 데이터는 볼륨이나 RDS, S3 같은 외부 저장소에 둔다.

### 빌드 시점과 실행 시점

Dockerfile에는 이미지를 만들 때 실행하는 명령과 컨테이너를 시작할 때 적용하는 설정이 함께 들어 있다.

```text
빌드 시점: FROM, RUN, COPY
  -> 이미지에 파일과 패키지를 기록한다.

실행 시점: CMD, ENTRYPOINT, 환경 변수, 포트 연결
  -> 이미지로 새 컨테이너 프로세스를 시작한다.
```

이미지 빌드 중 실행한 `RUN pip install ...`은 컨테이너를 시작할 때마다 반복되지 않는다. 반대로 `CMD`는 이미지 빌드 때 Django를 실행하는 명령이 아니라 컨테이너 시작 시 실행할 기본 명령이다.

### 이미지 레이어와 빌드 캐시

이미지는 여러 읽기 전용 레이어가 쌓인 구조이다. Dockerfile의 `RUN`, `COPY` 같은 명령이 새 레이어를 만들며 앞 단계의 입력이 같으면 기존 빌드 결과를 캐시로 재사용할 수 있다.

```text
기반 Python 이미지
  + 운영체제 패키지 레이어
  + Python 패키지 레이어
  + 애플리케이션 소스 레이어
```

자주 바뀌지 않는 `requirements.txt`를 소스 코드보다 먼저 복사하면 Python 패키지 설치 레이어를 더 자주 재사용할 수 있다. 앞 레이어가 바뀌면 그 뒤 레이어도 다시 만들어진다.

## 5. 로컬 Docker 환경 준비

### Windows

1. Docker Desktop을 설치하고 실행한다.
2. Docker Desktop 설정에서 WSL 2 기반 엔진을 사용한다.
3. `Resources -> WSL Integration`에서 수업에 사용하는 Ubuntu 배포판을 활성화한다.
4. 이후 Docker 명령은 WSL Ubuntu 터미널에서 실행한다.

### macOS

1. Mac의 CPU에 맞는 Docker Desktop을 설치하고 실행한다.
2. 이후 Docker 명령은 Terminal 또는 iTerm2에서 실행한다.

두 환경 모두 다음 명령으로 연결 상태를 확인한다.

```bash
# Docker CLI와 Docker Engine 정보를 함께 확인한다.
docker version

# Compose 플러그인 버전을 확인한다.
docker compose version

# Docker Engine이 사용하는 운영체제와 CPU 아키텍처를 확인한다.
docker info --format 'OS={{.OperatingSystem}} Architecture={{.Architecture}}'
```

`docker version`에 Client와 Server가 모두 표시되어야 한다. Server 연결 오류가 나오면 Docker Desktop이 실행 중인지 확인한다.

## 6. 첫 컨테이너 실행

```bash
# 작은 테스트 이미지를 내려받아 컨테이너 실행 경로 전체를 확인한다.
docker run --rm hello-world
```

로컬에 이미지가 없으면 Docker가 레지스트리에서 이미지를 내려받는다. 컨테이너가 안내 문구를 출력하고 종료되며 `--rm` 옵션이 종료된 컨테이너를 자동 삭제한다.

```bash
# 현재 로컬에 저장된 이미지 목록을 확인한다.
docker image ls

# 실행 중인 컨테이너와 종료된 컨테이너를 모두 확인한다.
docker ps -a
```

## 7. Nginx 컨테이너와 포트 매핑

컨테이너 안의 포트는 로컬 PC의 포트와 별개이다. `-p 127.0.0.1:8080:80`은 로컬의 8080번을 컨테이너의 80번에 연결한다.

```text
브라우저 127.0.0.1:8080
  -> 로컬 Docker 포트 8080
  -> 컨테이너 Nginx 포트 80
```

```bash
# Nginx 컨테이너를 로컬 8080번 포트에 연결해 백그라운드 실행한다.
docker run -d \
  --name demo-nginx \
  -p 127.0.0.1:8080:80 \
  nginx:alpine

# 실행 중인 컨테이너와 포트 연결을 확인한다.
docker ps

# Docker가 기록한 실제 포트 매핑을 확인한다.
docker port demo-nginx

# 컨테이너의 네트워크 모드와 내부 IP를 확인한다.
docker inspect demo-nginx \
  --format 'Network={{.HostConfig.NetworkMode}} IP={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# 로컬 PC에서 Nginx 응답 헤더를 확인한다.
curl -I http://127.0.0.1:8080

# 컨테이너가 표준 출력으로 남긴 로그를 확인한다.
docker logs demo-nginx
```

브라우저에서 `http://127.0.0.1:8080`을 열어 Nginx 기본 화면을 확인한다.

컨테이너의 `127.0.0.1`은 로컬 PC의 `127.0.0.1`과 다른 네트워크 공간이다. 포트 매핑이 두 공간을 연결한다. `EXPOSE 80`만 적는다고 로컬 8080번이 자동으로 열리지는 않는다.

## 8. 컨테이너 내부와 생명주기

컨테이너는 작은 가상 머신처럼 보이지만 실제로는 격리된 프로세스이다. 컨테이너의 주 프로세스가 종료되면 컨테이너도 종료된다.

```bash
# 컨테이너의 주 프로세스와 자식 프로세스를 확인한다.
docker top demo-nginx
```

Dockerfile의 `CMD`나 `ENTRYPOINT`로 시작한 프로세스가 컨테이너 내부의 첫 번째 프로세스인 PID 1이 된다. 서버 프로그램을 백그라운드로 보내지 않고 포그라운드에서 실행해야 Docker가 종료 상태와 로그를 관리할 수 있다.

```bash
# 실행 중인 컨테이너 안에서 별도의 sh 프로세스를 실행한다.
docker exec -it demo-nginx sh

# 컨테이너가 사용하는 Linux 배포판 정보를 확인한다.
cat /etc/os-release

# 컨테이너 셸을 종료하고 로컬 터미널로 돌아간다.
exit
```

`docker exec`로 들어간 셸은 컨테이너의 주 프로세스가 아니다. 셸을 종료해도 Nginx는 계속 실행된다.

```bash
# 이미지와 비교해 컨테이너 쓰기 계층에서 바뀐 파일을 확인한다.
docker diff demo-nginx
```

`A`는 추가, `C`는 변경, `D`는 삭제를 뜻한다. 컨테이너 내부에서 직접 수정한 파일은 새 이미지를 만들지 않으며 컨테이너를 삭제하면 사라질 수 있다.

```bash
# Nginx 컨테이너의 실행을 중지한다.
docker stop demo-nginx

# 중지된 컨테이너를 다시 시작한다.
docker start demo-nginx

# 컨테이너를 중지하고 삭제한다.
docker rm -f demo-nginx
```

## 9. 볼륨으로 데이터 유지하기

컨테이너 쓰기 계층은 임시 데이터에 적합하다. 유지하거나 호스트와 공유해야 하는 데이터는 볼륨 또는 바인드 마운트를 사용한다.

| 방식 | 저장 위치 | 주요 용도 |
| --- | --- | --- |
| 이름 있는 볼륨 | Docker가 관리 | 데이터베이스 데이터, 컨테이너 간 영구 데이터 |
| 바인드 마운트 | 사용자가 지정한 호스트 경로 | 로컬 소스 코드, 설정 파일 공유 |

볼륨은 Docker가 실제 저장 경로를 관리하고 바인드 마운트는 호스트 파일 경로를 그대로 연결한다. 운영 배포에서는 이미지 자체에 코드를 포함하고 RDS와 S3에 데이터를 분리하므로 소스 코드 바인드 마운트를 사용하지 않는다.

```bash
# Docker가 관리하는 이름 있는 볼륨을 만든다.
docker volume create demo-data

# 볼륨을 Nginx 문서 디렉터리에 연결한다.
docker run -d \
  --name volume-nginx \
  -p 127.0.0.1:8080:80 \
  -v demo-data:/usr/share/nginx/html \
  nginx:alpine

# 볼륨에 HTML 파일을 작성한다.
docker exec volume-nginx sh -c \
  'echo "volume survives" > /usr/share/nginx/html/index.html'

# 작성한 HTML 응답을 확인한다.
curl http://127.0.0.1:8080

# 컨테이너만 삭제한다.
docker rm -f volume-nginx

# 같은 볼륨을 새 컨테이너에 연결한다.
docker run -d \
  --name volume-nginx-2 \
  -p 127.0.0.1:8080:80 \
  -v demo-data:/usr/share/nginx/html \
  nginx:alpine

# 새 컨테이너에서도 기존 파일이 보이는지 확인한다.
curl http://127.0.0.1:8080
```

컨테이너를 교체해도 볼륨은 남는다. RDS와 S3를 컨테이너 밖에 둔 이유도 애플리케이션 컨테이너와 데이터의 생명주기를 분리하기 위해서이다.

### 바인드 마운트 관찰

```bash
# 현재 디렉터리에 바인드 마운트용 HTML 파일을 만든다.
mkdir -p ~/docker-bind-demo
echo 'bind mount from host' > ~/docker-bind-demo/index.html

# 호스트 디렉터리를 Nginx 문서 디렉터리에 읽기 전용으로 연결한다.
docker run -d \
  --name bind-nginx \
  -p 127.0.0.1:8081:80 \
  -v ~/docker-bind-demo:/usr/share/nginx/html:ro \
  nginx:alpine

# 컨테이너가 호스트 파일 내용을 응답하는지 확인한다.
curl http://127.0.0.1:8081

# 바인드 마운트의 호스트 경로와 컨테이너 경로를 확인한다.
docker inspect bind-nginx \
  --format '{{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}}{{end}}'

# 관찰이 끝난 컨테이너를 삭제한다.
docker rm -f bind-nginx
```

## 10. CPU 아키텍처 확인

```bash
# 로컬 운영체제가 보고하는 CPU 아키텍처를 확인한다.
uname -m

# Docker Engine의 CPU 아키텍처를 확인한다.
docker info --format '{{.Architecture}}'
```

Intel·AMD 기반 PC는 보통 `x86_64` 또는 `amd64`로 표시되고 Apple Silicon Mac은 `arm64` 또는 `aarch64`로 표시된다. 이 과정의 EC2는 x86_64이므로 최종 배포 이미지는 `linux/amd64`로 만든다.

Docker Hub의 Python과 Nginx 공식 이미지는 여러 CPU 아키텍처를 지원한다. 로컬 실습은 현재 PC의 기본 아키텍처로 실행하고, AWS에 올릴 이미지는 Docker Buildx 또는 GitHub Actions에서 대상 플랫폼을 지정한다.

## 11. 실습 자원 정리

```bash
# 볼륨 확인용 컨테이너를 삭제한다.
docker rm -f volume-nginx-2

# 실습용 볼륨을 삭제한다.
docker volume rm demo-data

# 바인드 마운트 실습 파일과 빈 디렉터리를 삭제한다.
rm ~/docker-bind-demo/index.html
rmdir ~/docker-bind-demo

# 남은 컨테이너를 확인한다.
docker ps -a
```

`docker system prune -a`는 다른 프로젝트의 이미지와 캐시까지 삭제할 수 있으므로 사용하지 않는다.

## 12. 다음 단계의 개발 환경

이번 문서의 Docker 기초 실습은 WSL Ubuntu에서 진행했다. 다음 문서부터는 Windows에 저장한 Django 프로젝트를 VS Code로 수정하고 VS Code의 CMD 터미널에서 Miniconda, Git과 Docker 명령을 실행한다.

```text
05_docker/01: WSL Ubuntu에서 Docker 기본 동작 확인
05_docker/02 이후: Windows에서 Django 개발 -> Docker 이미지 생성 -> AWS 배포
```

WSL과 Windows CMD에서 실행한 `docker` 명령은 Docker Desktop의 같은 Docker Engine을 사용할 수 있다. WSL 안에 Docker Engine을 별도로 설치하지 않고 Docker Desktop의 WSL Integration을 사용한다.

## 확인 과제

1. 이미지와 컨테이너의 차이를 적는다.
2. `127.0.0.1:8080:80`의 두 포트가 각각 어디에 속하는지 적는다.
3. Apple Silicon Mac에서 x86_64 EC2용 이미지를 만들 때 지정할 플랫폼을 적는다.

<details>
<summary>정답 예시</summary>

1. 이미지는 컨테이너를 만들기 위한 읽기 전용 템플릿이고 컨테이너는 이미지를 프로세스로 실행한 상태이다.
2. 8080번은 로컬 PC의 포트이고 80번은 컨테이너 안의 Nginx 포트이다.
3. `linux/amd64`를 지정한다.

</details>
