# EC2 생성과 WSL SSH 접속

## 학습 목표

- Ubuntu EC2 인스턴스를 생성할 수 있다.
- AMI, 인스턴스 유형, EBS가 EC2를 어떻게 구성하는지 설명할 수 있다.
- 키 페어와 보안 그룹의 역할을 설명할 수 있다.
- WSL에서 PEM 개인키 권한을 설정하고 SSH로 접속할 수 있다.
- EC2에 Nginx를 설치하고 HTTP 요청을 확인할 수 있다.

## 1. 실습 결과

EC2는 AWS 데이터 센터의 물리 서버 일부를 가상 머신으로 빌려 사용하는 컴퓨팅 서비스이다. EC2 한 대를 만들 때는 운영체제, CPU·메모리 크기, 디스크, 네트워크와 접속 방법을 함께 정한다.

| 구성 요소 | 의미 | 이 실습의 선택 |
| --- | --- | --- |
| 인스턴스 | 실행 중인 가상 서버 한 대 | `cloud-class-ec2` |
| AMI | 운영체제가 들어 있는 서버 시작 이미지 | Ubuntu Server 24.04 LTS |
| 인스턴스 유형 | 가상 CPU와 메모리 조합 | `t3.micro` |
| EBS | EC2에 연결하는 가상 디스크 | `gp3` 16 GiB |
| 키 페어 | SSH 접속에 사용하는 공개키와 개인키 묶음 | `cloud-class-key` |
| 보안 그룹 | EC2 앞에서 포트 접근을 제한하는 방화벽 | `cloud-class-ec2-sg` |

EC2 인스턴스를 중지하면 CPU와 메모리 실행은 멈추지만 EBS의 파일은 남는다. 인스턴스를 종료하면 연결 자원의 삭제 설정에 따라 디스크도 함께 삭제될 수 있다. 실행 상태와 저장 상태의 생명주기를 구분해야 한다.

```text
[Windows 브라우저]
       |
       | HTTP 80
       v
[EC2 Ubuntu + Nginx]

[WSL]
  |
  | SSH 22 + PEM 개인키
  v
[EC2 Ubuntu]
```

이번 단계에서는 EC2와 Nginx까지만 구성한다. Django는 다음 문서에서 배포한다.

## 2. 실습 값 정하기

| 항목 | 값 |
| --- | --- |
| 리전 | 서울 `ap-northeast-2` |
| 인스턴스 이름 | `cloud-class-ec2` |
| AMI | Ubuntu Server 24.04 LTS x86_64 |
| 키 페어 | `cloud-class-key` |
| 보안 그룹 | `cloud-class-ec2-sg` |
| 태그 | `Project=cloud-class` |

인스턴스 유형은 `t3.micro`를 기준으로 한다. 목록에 없다면 현재 선택할 수 있는 가장 작은 범용 유형을 사용한다. "프리 티어 사용 가능" 표시가 있더라도 스토리지, 퍼블릭 IPv4, 데이터 전송 등 다른 항목에서 비용이 발생할 수 있다.

## 3. 보안 그룹 만들기

1. AWS 콘솔에서 `EC2`를 연다.
2. 왼쪽 메뉴에서 `Security Groups`를 선택한다.
3. `Create security group`을 선택한다.
4. 이름에 `cloud-class-ec2-sg`를 입력한다.
5. 설명에 `Security group for cloud class EC2`를 입력한다.
6. 기본 VPC를 선택한다.
7. 인바운드 규칙을 다음과 같이 추가한다.

| 유형 | 포트 | 소스 |
| --- | ---: | --- |
| SSH | 22 | `My IP` |
| HTTP | 80 | `Anywhere-IPv4` |

8. 태그에 `Project=cloud-class`를 추가한다.
9. 보안 그룹을 생성한다.

SSH 규칙의 소스가 `0.0.0.0/0`이 아닌 자신의 공인 IP `/32`인지 확인한다. 교육장 공인 IP가 바뀌면 규칙의 소스를 다시 `My IP`로 갱신한다.

## 4. 키 페어 만들기

SSH는 네트워크를 통해 다른 Linux 컴퓨터의 셸에 안전하게 접속하는 프로토콜이다. 비밀번호 대신 키 페어를 사용하면 서버에는 공개키가 저장되고 사용자는 개인키인 PEM 파일을 보관한다. 개인키는 서버로 전송하는 비밀번호가 아니라 접속 요청에 서명하는 데 사용한다.

1. EC2 왼쪽 메뉴에서 `Key Pairs`를 선택한다.
2. `Create key pair`를 선택한다.
3. 이름에 `cloud-class-key`를 입력한다.
4. 키 유형은 `RSA`를 선택한다.
5. 파일 형식은 `.pem`을 선택한다.
6. 키 페어를 생성해 다운로드한다.

PEM 파일은 개인키이다. 메신저, GitHub, 공유 드라이브에 올리지 않는다. AWS는 같은 개인키를 다시 다운로드하게 해 주지 않는다.

## 5. EC2 인스턴스 만들기

1. EC2의 `Instances` 화면에서 `Launch instances`를 선택한다.
2. 이름에 `cloud-class-ec2`를 입력한다.
3. AMI에서 `Ubuntu Server 24.04 LTS`의 x86_64 이미지를 선택한다.
4. 인스턴스 유형은 `t3.micro`를 선택한다. 목록에 없다면 현재 선택할 수 있는 가장 작은 범용 유형을 선택한다.
5. 키 페어로 `cloud-class-key`를 선택한다.
6. 네트워크 설정에서 기본 VPC와 퍼블릭 서브넷을 선택한다.
7. 퍼블릭 IP 자동 할당이 활성화되어 있는지 확인한다.
8. 기존 보안 그룹 `cloud-class-ec2-sg`를 선택한다.
9. 스토리지는 Docker 이미지와 패키지를 저장할 수 있도록 `gp3` 16 GiB로 설정한다.
10. 태그 `Project=cloud-class`를 확인한다.
11. 요약 화면의 예상 구성을 확인하고 인스턴스를 시작한다.

인스턴스 상태가 `Running`, 상태 검사가 `2/2 checks passed`가 될 때까지 기다린다.

## 6. 접속 정보 기록하기

인스턴스를 선택하고 다음 값을 기록한다.

| 항목 | 예시 |
| --- | --- |
| 인스턴스 ID | `i-0123456789abcdef0` |
| 퍼블릭 IPv4 | `3.35.100.20` |
| 퍼블릭 IPv4 DNS | `ec2-3-35-100-20.ap-northeast-2.compute.amazonaws.com` |
| 프라이빗 IPv4 | `172.31.10.25` |
| 사용자 이름 | `ubuntu` |

표의 IP와 DNS는 형식을 보여 주는 예시이므로 실제 접속에는 자신의 EC2 값을 사용한다. 퍼블릭 DNS에는 `http://`를 붙이지 않고 호스트 이름만 기록한다.

## 7. PEM 파일을 WSL로 복사하기

Windows PowerShell에서 사용자 이름과 파일 위치를 먼저 확인한다.

Windows와 WSL은 파일 시스템과 권한 처리 방식이 다르다. PEM 파일을 WSL 홈 디렉터리로 복사해야 `chmod`로 Linux 권한을 안정적으로 적용할 수 있다.

```powershell
# 현재 Windows 사용자 이름을 확인한다.
$env:USERNAME

# Downloads 폴더에 내려받은 PEM 파일이 있는지 확인한다.
Get-ChildItem "$HOME\Downloads\cloud-class-key.pem"
```

WSL Ubuntu를 열고 다음을 실행한다. `<WINDOWS_USER>`는 앞에서 확인한 이름으로 바꾼다.

```bash
# SSH 개인키를 저장할 홈 디렉터리의 .ssh 폴더를 만든다.
mkdir -p ~/.ssh

# Windows Downloads 폴더의 PEM 파일을 WSL 홈으로 복사한다.
cp /mnt/c/Users/<WINDOWS_USER>/Downloads/cloud-class-key.pem ~/.ssh/

# 개인키를 현재 사용자만 읽을 수 있게 제한한다.
chmod 400 ~/.ssh/cloud-class-key.pem

# 개인키의 권한과 소유자를 확인한다.
ls -l ~/.ssh/cloud-class-key.pem
```

`-r--------`와 비슷하게 표시되면 권한 설정이 완료된 것이다. Windows 파일 시스템의 원본을 직접 사용하는 대신 WSL 파일 시스템으로 복사해야 Linux 권한이 안정적으로 적용된다.

## 8. SSH로 접속하기

`<EC2_PUBLIC_DNS>`를 자신의 퍼블릭 IPv4 DNS로 바꾼다.

```bash
# PEM 개인키로 Ubuntu EC2 인스턴스에 SSH 접속한다.
ssh -i ~/.ssh/cloud-class-key.pem ubuntu@<EC2_PUBLIC_DNS>
```

처음 접속하면 호스트 키 지문을 신뢰할지 묻는다. AWS 콘솔의 인스턴스 정보와 IP가 맞는지 확인한 뒤 `yes`를 입력한다.

접속에 성공하면 프롬프트가 다음과 비슷하게 바뀐다.

```text
ubuntu@ip-172-31-10-25:~$
```

## 9. EC2 기본 정보 확인하기

다음 명령은 EC2 Ubuntu 안에서 실행한다.

```bash
# 현재 로그인 사용자 이름을 확인한다.
whoami

# 운영체제 배포판과 버전을 확인한다.
cat /etc/os-release

# 커널과 CPU 아키텍처 정보를 확인한다.
uname -a

# EC2의 프라이빗 IP 주소를 확인한다.
hostname -I

# 루트 파일 시스템의 사용량을 확인한다.
df -h /

# 현재 메모리 사용량을 사람이 읽기 쉬운 단위로 확인한다.
free -h
```

`whoami` 결과는 `ubuntu`여야 한다. `hostname -I`에는 AWS 콘솔에서 본 프라이빗 IPv4가 포함된다.

## 10. 패키지 업데이트와 Nginx 설치

Ubuntu의 `apt`는 운영체제 패키지를 검색하고 설치하는 패키지 관리자이다. `curl`은 URL에 요청을 보내 응답을 확인하거나 파일을 내려받는 도구이고, Nginx는 HTTP 요청을 받는 웹 서버이다.

이 단계에서는 Nginx가 기본 HTML 페이지를 직접 응답한다. 다음 단계부터는 Nginx가 요청을 Django 쪽으로 전달하는 리버스 프록시 역할도 맡는다.

```bash
# Ubuntu가 설치 가능한 최신 패키지 목록을 내려받는다.
sudo apt update

# 설치된 패키지를 보안 업데이트가 포함된 최신 버전으로 올린다.
sudo apt upgrade -y

# 웹 서버 Nginx와 이후 실습에 사용할 도구를 설치한다.
sudo apt install -y nginx curl git unzip

# Nginx를 지금 시작하고 재부팅 후에도 자동 시작하게 설정한다.
sudo systemctl enable --now nginx

# Nginx 서비스가 실행 중인지 확인한다.
sudo systemctl status nginx
```

상태 화면에 `Active: active (running)`이 표시되어야 한다. `q`를 누르면 상태 화면에서 나온다.

## 11. 안쪽과 바깥쪽에서 확인하기

먼저 EC2 내부에서 확인한다.

```bash
# EC2 자신의 80번 포트로 HTTP 요청을 보내 응답 헤더를 확인한다.
curl -I http://127.0.0.1

# 80번 포트를 어떤 프로세스가 듣고 있는지 확인한다.
sudo ss -lntp | grep ':80'
```

`HTTP/1.1 200 OK`와 `nginx` 프로세스가 보이면 서버 내부는 정상이다.

Windows 브라우저에서 다음 주소를 연다.

```text
http://<EC2_PUBLIC_DNS>
```

Nginx 기본 페이지가 표시되면 인터넷, 보안 그룹, Nginx까지 전체 경로가 정상이다.

## 12. SSH 설정 파일로 접속 단축하기

WSL에서 SSH 접속을 종료한 뒤 설정 파일을 만든다.

```bash
# EC2 SSH 접속 정보를 저장할 설정 파일을 편집한다.
vi ~/.ssh/config
```

다음 내용을 입력한다.

```sshconfig
Host cloud-class
    HostName <EC2_PUBLIC_DNS>
    User ubuntu
    IdentityFile ~/.ssh/cloud-class-key.pem
```

```bash
# SSH 설정 파일을 현재 사용자만 읽고 쓸 수 있게 제한한다.
chmod 600 ~/.ssh/config

# 저장한 별칭으로 EC2에 접속한다.
ssh cloud-class
```

수업 중에는 EC2를 실행 상태로 유지하므로 같은 `HostName`을 계속 사용할 수 있다. EC2를 중지 후 다시 시작했다면 AWS 콘솔에서 새 퍼블릭 IPv4 DNS를 확인해 `HostName`을 수정한다.

## 13. 접속 종료와 인스턴스 상태

```bash
# 현재 SSH 세션을 종료하고 로컬 WSL로 돌아간다.
exit
```

| 작업 | 의미 | 비용 관점 |
| --- | --- | --- |
| Stop | 가상 서버 실행을 멈춘다. | 컴퓨팅 비용은 멈추지만 볼륨 등은 남는다. |
| Start | 멈춘 인스턴스를 다시 실행한다. | 퍼블릭 IPv4와 퍼블릭 DNS가 바뀔 수 있다. |
| Reboot | 운영체제를 재부팅한다. | 인스턴스는 계속 실행 상태이다. |
| Terminate | 인스턴스를 삭제한다. | 연결된 자원과 삭제 정책을 확인해야 한다. |

다음 수업에서 같은 EC2를 사용하므로 지금은 종료하지 않는다.

## 14. 문제 해결

### SSH가 시간 초과된다

- 인스턴스가 실행 중인지 확인한다.
- 퍼블릭 IPv4 DNS가 바뀌지 않았는지 확인한다.
- 보안 그룹의 SSH 소스를 현재 공인 IP로 갱신한다.
- 교육장 네트워크가 22번 포트를 차단하는지 확인한다.

### `Permission denied (publickey)`가 나온다

- 사용자 이름이 `ubuntu`인지 확인한다.
- 생성할 때 선택한 키 페어와 PEM 파일이 같은지 확인한다.
- `chmod 400` 권한을 확인한다.

### 브라우저에서 Nginx가 보이지 않는다

- `curl -I http://127.0.0.1`이 성공하는지 확인한다.
- 보안 그룹의 HTTP 80번 규칙을 확인한다.
- 주소가 `https://`가 아니라 `http://`인지 확인한다.

## 확인 과제

1. SSH는 실패하지만 EC2 내부 Nginx가 정상일 수 있는 이유를 적는다.
2. `chmod 400`이 개인키에 필요한 이유를 적는다.
3. Nginx가 듣는 포트를 확인하는 명령을 실행하고 결과에서 포트 번호를 찾는다.

<details>
<summary>정답 예시</summary>

1. SSH 22번 포트의 보안 그룹 규칙이나 개인키가 잘못되어도 EC2 내부의 Nginx 프로세스는 별개로 실행될 수 있다.
2. 개인키를 다른 사용자가 읽지 못하게 제한하고 SSH 클라이언트의 보안 검사를 통과하기 위해서이다.
3. `sudo ss -lntp | grep ':80'`을 실행하면 Nginx가 80번 포트를 듣는지 확인할 수 있다.

</details>
