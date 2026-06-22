# 12. 패키지와 네트워크 기초

## 학습 목표

- Ubuntu의 `apt` 패키지 관리 흐름을 익힌다.
- 네트워크 주소와 연결 상태를 기본 명령어로 확인한다.
- WSL에서 Windows 명령과 Linux 명령을 함께 사용하는 방법을 익힌다.
- 수업 환경에서 필요한 도구를 안전하게 설치하고 제거한다.

## apt 패키지 관리자

Ubuntu는 `apt`로 패키지를 설치하고 업데이트한다.

```bash
# 패키지 목록을 최신 상태로 갱신한다
sudo apt update

# tree라는 이름의 패키지를 검색한다
apt search tree

# tree 패키지의 상세 정보를 확인한다
apt show tree
```

패키지를 설치한다.

```bash
# tree 패키지를 설치한다
sudo apt install tree

# 설치된 tree 명령의 버전을 확인한다
tree --version
```

설치된 패키지를 제거한다.

```bash
# tree 패키지를 제거한다
sudo apt remove tree
```

패키지 목록 업데이트와 패키지 업그레이드는 다르다.

| 명령어 | 의미 |
| --- | --- |
| `sudo apt update` | 패키지 목록 갱신 |
| `sudo apt upgrade` | 설치된 패키지를 새 버전으로 업그레이드 |
| `sudo apt install 패키지` | 패키지 설치 |
| `sudo apt remove 패키지` | 패키지 제거 |
| `apt search 키워드` | 패키지 검색 |
| `apt show 패키지` | 패키지 정보 확인 |

## 네트워크 정보 확인

```bash
# 네트워크 인터페이스와 IP 주소를 확인한다
ip addr

# 기본 게이트웨이와 라우팅 정보를 확인한다
ip route

# 현재 시스템에 할당된 IP 주소만 간단히 출력한다
hostname -I
```

| 명령어 | 설명 |
| --- | --- |
| `ip addr` | 네트워크 인터페이스와 IP 주소 |
| `ip route` | 라우팅 정보 |
| `hostname -I` | 현재 시스템의 IP 주소 |

WSL 2는 Windows 안의 가상 네트워크를 사용하므로 IP 주소가 Windows의 IP와 다를 수 있다.

## 연결 확인

```bash
# IP 주소로 외부 연결이 되는지 확인한다
ping -c 4 8.8.8.8

# 도메인 이름 해석과 외부 연결을 함께 확인한다
ping -c 4 google.com
```

첫 번째는 IP 연결을 확인하고, 두 번째는 DNS 이름 해석까지 함께 확인한다.

HTTP 응답 헤더를 확인하려면 `curl`을 사용한다.

```bash
# example.com의 HTTP 응답 헤더만 확인한다
curl -I https://example.com
```

`curl`이 없다면 설치한다.

```bash
# curl 패키지를 설치한다
sudo apt install curl
```

## 열린 포트 확인

```bash
# 현재 열려 있는 TCP/UDP listening 포트를 확인한다
ss -tulpen
```

| 옵션 | 의미 |
| --- | --- |
| `-t` | TCP |
| `-u` | UDP |
| `-l` | listening 상태 |
| `-p` | 프로세스 정보 |
| `-n` | 이름 변환 없이 숫자로 출력 |

## Windows와 WSL 상호 운용

PowerShell에서 Linux 명령을 실행한다.

```powershell
# WSL 안에서 커널 정보를 확인한다
wsl uname -a

# WSL 안에서 현재 디렉터리를 출력한다
wsl pwd

# WSL 안에서 파일 목록을 자세히 출력한다
wsl ls -la
```

Ubuntu에서 Windows 명령을 실행한다.

```bash
# Windows 네트워크 설정 정보를 출력한다
ipconfig.exe

# Windows 네트워크 정보 중 IPv4 줄만 필터링한다
ipconfig.exe | grep IPv4

# Windows 메모장으로 Bash 설정 파일을 연다
notepad.exe ~/.bashrc

# 현재 WSL 디렉터리를 Windows 탐색기로 연다
explorer.exe .
```

PowerShell 명령과 Linux 명령을 섞을 수도 있다.

```powershell
# Windows 명령 출력에서 WSL grep으로 IPv4 줄만 검색한다
ipconfig.exe | wsl grep IPv4
```


## 확인 과제

1. `apt search`로 `htop` 패키지를 찾아본다.
2. `curl -I https://example.com`의 첫 줄 HTTP 상태 코드를 확인한다.
3. `ip addr`에서 WSL의 IP 주소를 찾는다.
4. Ubuntu에서 `ipconfig.exe`를 실행해 Windows 네트워크 정보를 본다.
5. `ss -tulpen` 출력에서 listening 상태의 항목을 확인한다.

<details>
<summary>정답 예시</summary>

`htop` 패키지를 검색한다.

```bash
# htop 패키지를 검색한다
apt search htop

# htop 패키지 상세 정보를 확인한다
apt show htop
```

HTTP 상태 코드는 다음처럼 확인한다.

```bash
# HTTP 응답 헤더의 첫 줄만 확인한다
curl -I https://example.com | head -n 1
```

예상 출력은 `HTTP/2 200` 또는 `HTTP/1.1 200 OK` 형태이다.

WSL의 IP 주소를 확인한다.

```bash
# 네트워크 인터페이스별 IP 주소를 확인한다
ip addr

# 할당된 IP 주소만 간단히 출력한다
hostname -I
```

`eth0` 항목이나 `hostname -I` 출력에 보이는 주소가 WSL의 IP 주소이다.

Ubuntu에서 Windows 네트워크 정보를 확인한다.

```bash
# Windows 네트워크 설정 정보를 출력한다
ipconfig.exe
```

IPv4 주소만 보고 싶다면 다음처럼 필터링한다.

```bash
# Windows 네트워크 정보 중 IPv4 줄만 출력한다
ipconfig.exe | grep IPv4
```

listening 상태의 포트를 확인한다.

```bash
# listening 상태의 네트워크 포트를 확인한다
ss -tulpen
```

출력의 `State` 또는 상태 열에 `LISTEN`이 보이면 대기 중인 포트이다.

</details>
