# SSM 기반 EC2 자동 배포

## 학습 목표

- SSH 배포와 Systems Manager 배포의 차이를 설명할 수 있다.
- 제공 프로젝트의 Compose와 배포 스크립트를 EC2에 준비할 수 있다.
- 테스트와 이미지 push가 성공한 경우에만 EC2 배포를 실행할 수 있다.
- 커밋 SHA 이미지로 배포하고 이전 SHA로 롤백할 수 있다.

## 1. 최종 배포 흐름

```text
Windows 로컬 코드 push
  -> GitHub Actions test
  -> Django와 컨테이너 테스트 성공
  -> AMD64 이미지 빌드
  -> ECR에 커밋 SHA 이미지 push
  -> SSM Run Command
  -> EC2 deploy.sh
  -> 이미지 pull, check, migrate
  -> 컨테이너 교체
  -> 메인 화면과 API 확인
```

EC2에서 애플리케이션 코드를 수정하지 않는다. EC2에는 `compose.yml`, `deploy.sh`와 운영 환경 변수만 두고 Django 코드는 ECR 이미지 안에서 실행한다.

## 2. Systems Manager와 SSM Agent

AWS Systems Manager는 EC2 같은 자원을 조회하고 원격 작업을 실행하는 운영 서비스이다. Run Command는 SSH 연결 없이 EC2에 명령을 전달한다.

```text
GitHub Actions
  -> Systems Manager API
  -> SSM Agent
  -> EC2 배포 스크립트
```

| 구성 요소 | 역할 |
| --- | --- |
| Systems Manager | 원격 명령을 등록하고 실행 상태를 관리한다. |
| SSM Agent | EC2 안에서 명령을 받아 실행하고 결과를 돌려준다. |
| EC2 IAM Role | EC2가 SSM과 통신하고 ECR 이미지를 pull할 권한이다. |
| GitHub IAM Role | 지정한 EC2에 Run Command를 보낼 권한이다. |

SSM 명령도 서버에서 높은 권한으로 실행될 수 있다. 대상 인스턴스와 실행 가능한 AWS 권한을 제한해야 한다.

## 3. EC2 역할에 SSM 권한 추가

`cloud-class-ec2-role`에 AWS 관리형 정책 `AmazonSSMManagedInstanceCore`를 연결한다. 앞 단계에서 만든 `cloud-class-ecr-pull-policy`도 연결되어 있어야 한다.

| 권한 | 목적 |
| --- | --- |
| `AmazonSSMManagedInstanceCore` | EC2가 SSM 관리형 노드로 등록되고 명령 결과를 전달한다. |
| `cloud-class-ecr-pull-policy` | EC2가 배포 이미지를 ECR에서 내려받는다. |

## 4. SSM Agent 확인

EC2에 SSH 접속해 실행한다.

```bash
# snap으로 설치된 SSM Agent 서비스 상태를 확인한다.
sudo systemctl status snap.amazon-ssm-agent.amazon-ssm-agent.service

# SSM Agent가 중지되어 있다면 시작하고 자동 시작을 설정한다.
sudo systemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service

# 서비스 이름이 다를 때 SSM 관련 unit을 찾는다.
systemctl list-unit-files | grep -i ssm
```

AWS 콘솔의 `Systems Manager -> Fleet Manager -> Managed nodes`에서 `cloud-class-ec2`가 Online인지 확인한다.

## 5. EC2에 Docker 실행 환경 준비

이미지는 GitHub Actions에서 만들지만 EC2에는 이미지를 실행할 Docker Engine과 Compose가 필요하다.

```bash
# 충돌할 수 있는 기존 Docker 관련 패키지가 있다면 제거한다.
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg"
done

# Docker 저장소 등록에 필요한 패키지를 설치한다.
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Docker 패키지 서명 키를 저장할 디렉터리를 만든다.
sudo install -m 0755 -d /etc/apt/keyrings

# Docker 공식 저장소의 GPG 키를 내려받는다.
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc

# APT가 서명 키를 읽을 수 있게 권한을 설정한다.
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 현재 Ubuntu 코드명과 CPU 아키텍처를 변수에 저장한다.
. /etc/os-release
UBUNTU_CODENAME="$VERSION_CODENAME"
DOCKER_ARCH=$(dpkg --print-architecture)

# 현재 Ubuntu 버전에 맞는 Docker 저장소를 등록한다.
echo "deb [arch=$DOCKER_ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker Engine, Buildx와 Compose 플러그인을 설치한다.
sudo apt-get update
sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# Docker 서비스를 시작하고 부팅 시 자동 시작하게 설정한다.
sudo systemctl enable --now docker

# ubuntu 사용자를 docker 그룹에 추가한다.
sudo usermod -aG docker ubuntu
```

SSH 연결을 종료하고 다시 접속한 뒤 확인한다.

```bash
# Docker Engine과 Compose가 정상인지 확인한다.
docker version
docker compose version
```

## 6. 포함된 배포 파일 확인

VS Code에서 `cloud-class-app` 폴더를 열고 CMD 터미널에서 실행한다.

```bat
REM 현재 터미널이 프로젝트 루트에 있는지 확인한다.
cd

REM Compose와 배포 스크립트가 포함되어 있는지 확인한다.
dir compose.yml deploy\deploy.sh

REM 배포 스크립트가 LF 줄바꿈으로 Git에 저장되도록 설정되었는지 확인한다.
git check-attr eol -- deploy/deploy.sh

REM 배포 스크립트를 줄 번호와 함께 확인한다.
findstr /n "^.*" deploy\deploy.sh
```

`deploy.sh`는 Windows에서 실행하는 파일이 아니다. GitHub Actions가 SSM으로 명령을 보내면 EC2의 Bash가 이 파일을 실행한다. 프로젝트의 `.gitattributes`는 Windows에서 커밋해도 셸 스크립트가 LF 줄바꿈으로 저장되게 한다.

`deploy.sh`는 다음 순서로 동작한다.

1. 현재 AWS 계정과 ECR 이미지 URI를 계산한다.
2. 커밋 SHA를 `APP_VERSION`으로 기록한다.
3. EC2 IAM Role로 ECR에 로그인한다.
4. 지정한 커밋 SHA 이미지를 pull한다.
5. 새 이미지에서 `manage.py check`를 실행한다.
6. RDS 마이그레이션을 적용한다.
7. Compose 컨테이너를 교체한다.
8. `/`, `/health/`, `/api/info/`를 확인한다.

단위 테스트는 GitHub Actions에서 이미 끝난다. 배포 스크립트는 운영 환경 변수, RDS, Nginx와 실제 HTTP 연결을 확인한다.

## 7. 배포 파일을 EC2에 준비

`<EC2_PUBLIC_DNS>`를 실제 값으로 바꿔 VS Code의 CMD 터미널에서 실행한다. `ssh`와 `scp` 명령이 없으면 Windows의 OpenSSH Client 기능을 먼저 설치한다.

```bat
REM Windows Downloads에 저장된 EC2 개인키와 접속 주소를 지정한다.
set "KEY_PATH=%USERPROFILE%\Downloads\cloud-class-key.pem"
set "EC2_HOST=ubuntu@<EC2_PUBLIC_DNS>"

REM Windows OpenSSH 명령과 개인키 파일을 확인한다.
where ssh
where scp
dir "%KEY_PATH%"

REM 개인키에 잘못 남아 있을 수 있는 명시적 권한을 초기화한다.
icacls "%KEY_PATH%" /reset

REM 상위 폴더의 권한 상속을 제거한다.
icacls "%KEY_PATH%" /inheritance:r

REM 현재 Windows 사용자에게 읽기 권한을 부여한다.
icacls "%KEY_PATH%" /grant:r "%USERDOMAIN%\%USERNAME%:(R)"

REM 개인키의 최종 권한을 확인한다.
icacls "%KEY_PATH%"

REM EC2에 애플리케이션 소스와 분리된 배포 디렉터리를 만든다.
ssh -i "%KEY_PATH%" ^
  %EC2_HOST% ^
  "mkdir -p /home/ubuntu/cloud-class-deploy"

REM Compose 파일과 배포 스크립트만 EC2에 복사한다.
scp -i "%KEY_PATH%" ^
  compose.yml ^
  deploy\deploy.sh ^
  "%EC2_HOST%:/home/ubuntu/cloud-class-deploy/"

REM EC2의 배포 스크립트 권한을 설정하고 Bash 문법을 검사한다.
ssh -i "%KEY_PATH%" ^
  %EC2_HOST% ^
  "chmod 750 /home/ubuntu/cloud-class-deploy/deploy.sh && bash -n /home/ubuntu/cloud-class-deploy/deploy.sh"
```

애플리케이션 Python 파일은 복사하지 않는다. 실제 코드는 ECR 이미지로 전달한다.

## 8. 수동 Gunicorn에서 컨테이너로 전환

EC2에서 한 번만 실행한다.

```bash
# 운영 환경 변수 파일을 docker 그룹이 읽을 수 있게 설정한다.
sudo chown root:docker /etc/cloud-class.env
sudo chmod 640 /etc/cloud-class.env

# 8000번 포트를 사용하던 수동 Gunicorn 서비스를 중지한다.
sudo systemctl disable --now cloud-class

# 이전 실습 컨테이너가 있다면 제거한다.
docker rm -f cloud-class-web 2>/dev/null || true

# 8000번 포트가 비어 있는지 확인한다.
sudo ss -lntp | grep ':8000' || true
```

Nginx는 계속 실행하며 `127.0.0.1:8000`으로 요청을 전달한다. 이후 이 포트는 Compose가 실행한 Django 컨테이너가 사용한다.

## 9. 배포 스크립트를 EC2에서 시험

GitHub Actions가 ECR에 올린 전체 커밋 SHA를 `<GIT_COMMIT_SHA>`로 지정한다.

```bash
# 배포할 Git 커밋 SHA를 지정한다.
export IMAGE_TAG=<GIT_COMMIT_SHA>

# 지정한 이미지로 첫 배포를 실행한다.
sudo -E /home/ubuntu/cloud-class-deploy/deploy.sh
```

마지막에 `deployment passed`가 표시되고 `/api/info/`의 version이 지정한 SHA와 같아야 한다.

```bash
# Nginx를 거친 메인 화면과 두 API를 확인한다.
curl -I http://127.0.0.1/
curl http://127.0.0.1/health/
curl http://127.0.0.1/api/info/
```

## 10. SSM Run Command로 시험

1. AWS 콘솔에서 `Systems Manager`를 연다.
2. `Run Command`에서 `Run command`를 선택한다.
3. 문서에서 `AWS-RunShellScript`를 선택한다.
4. 명령에 다음 값을 입력한다.

```text
IMAGE_TAG=<GIT_COMMIT_SHA> /home/ubuntu/cloud-class-deploy/deploy.sh
```

5. 대상 인스턴스로 `cloud-class-ec2`를 선택한다.
6. 명령을 실행한다.
7. 상태가 Success인지 확인한다.
8. 출력에서 `deployment passed`를 확인한다.

## 11. GitHub 역할에 SSM 권한 추가

`cloud-class-github-role`에 `cloud-class-github-ssm-policy` 인라인 정책을 추가한다. `<AWS_ACCOUNT_ID>`와 `<EC2_INSTANCE_ID>`를 실제 값으로 바꾼다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ssm:SendCommand",
      "Resource": [
        "arn:aws:ssm:ap-northeast-2::document/AWS-RunShellScript",
        "arn:aws:ec2:ap-northeast-2:<AWS_ACCOUNT_ID>:instance/<EC2_INSTANCE_ID>"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetCommandInvocation",
        "ssm:ListCommandInvocations"
      ],
      "Resource": "*"
    }
  ]
}
```

GitHub 역할은 지정한 EC2에 명령을 보내고 결과를 읽을 수 있지만 다른 EC2를 생성하거나 종료할 수는 없다.

## 12. 자동 배포 조건 활성화

GitHub Repository Variables에 다음 값을 추가한다.

| 변수 | 값 |
| --- | --- |
| `EC2_INSTANCE_ID` | `cloud-class-ec2`의 인스턴스 ID |

제공 Workflow의 deploy Job에는 다음 조건이 있다.

```yaml
if: github.event_name != 'pull_request' && vars.EC2_INSTANCE_ID != ''
needs: build-and-push
```

이제 main push에서 `build-and-push`가 성공하면 deploy Job도 실행된다. Pull Request와 `EC2_INSTANCE_ID`가 없는 저장소에서는 배포하지 않는다.

## 13. 기능 변경 후 자동 배포

VS Code에서 `core/templates/core/index.html`의 제목을 다음처럼 바꾼다.

```html
<h1>Cloud Class CI/CD</h1>
```

`core/tests.py`의 메인 화면 테스트에도 새 제목 검사를 추가한다.

```python
self.assertContains(response, "Cloud Class CI/CD")
```

로컬에서 먼저 검사한다.

```bat
REM Django 설정과 전체 테스트를 실행한다.
python manage.py check
python manage.py test

REM 변경된 파일을 확인한다.
git diff
```

테스트가 성공한 경우에만 커밋하고 push한다.

```bat
REM 기능과 테스트 변경을 커밋한다.
git add core
git commit -m "feat: update deployed home page"

REM main 브랜치에 push해 전체 CI/CD를 실행한다.
git push origin main
```

Actions에서 `test -> build-and-push -> deploy`가 순서대로 성공해야 한다.

```text
http://<EC2_PUBLIC_DNS>/
http://<EC2_PUBLIC_DNS>/health/
http://<EC2_PUBLIC_DNS>/api/info/
```

메인 제목이 변경되고 `/api/info/`의 version이 배포한 Git 커밋 SHA와 같으면 자동 배포가 완료된 것이다.

## 14. 배포 실패 확인 위치

1. GitHub Actions의 `test` Job
2. GitHub Actions의 `build-and-push` Job
3. GitHub Actions의 `deploy` Job
4. Systems Manager Run Command의 표준 출력과 오류
5. EC2의 `docker compose ps`
6. EC2의 `docker compose logs --tail 100 web`
7. Nginx `/var/log/nginx/error.log`

처음 실패한 단계부터 확인한다. 테스트가 실패했다면 AWS 권한이나 EC2 로그를 볼 필요가 없다.

## 15. 커밋 SHA로 롤백

ECR에 남아 있는 이전 커밋 SHA를 `<PREVIOUS_SHA>`로 지정한다.

```bash
# 이전 커밋 SHA 이미지로 다시 배포한다.
IMAGE_TAG=<PREVIOUS_SHA> \
sudo -E /home/ubuntu/cloud-class-deploy/deploy.sh
```

롤백도 이미지 pull, 설정 검사, 마이그레이션과 HTTP 확인 절차를 거친다. 데이터베이스 마이그레이션이 이전 코드와 호환되지 않으면 이미지 롤백만으로 충분하지 않을 수 있다.

## 확인 과제

1. 제공 프로젝트의 배포 스크립트를 EC2에 복사하지만 Python 소스는 복사하지 않는 이유를 적는다.
2. 첫 push에서는 건너뛴 deploy Job이 나중에 실행되는 조건을 적는다.
3. 커밋 SHA로 배포할 때의 장점을 적는다.

<details>
<summary>정답 예시</summary>

1. 애플리케이션 코드는 테스트를 통과한 ECR 이미지로 전달하고 EC2에는 실행 절차와 환경 변수만 유지하기 위해서이다.
2. `EC2_INSTANCE_ID`가 등록되고 `build-and-push` Job이 성공한 main push일 때 실행된다.
3. 어떤 소스 버전을 실행하는지 추적하고 이전 SHA 이미지로 정확히 롤백할 수 있다.

</details>
