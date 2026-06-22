# 00. WSL 환경 설정

## 학습 목표

- Windows에서 WSL 2와 Ubuntu를 설치한다.
- PowerShell 명령과 Ubuntu 명령을 구분한다.
- WSL의 시작, 종료, 상태 확인 방법을 익힌다.
- Windows 파일 시스템과 Linux 파일 시스템의 차이를 이해한다.

## 핵심 개념

WSL은 Windows 안에서 리눅스 배포판을 실행하게 해주는 기능이다. 수업에서는 WSL 2 기반 Ubuntu를 사용한다. WSL 2는 가벼운 가상 머신 구조를 사용하지만 일반 가상 머신보다 Windows와의 통합이 좋고 터미널에서 빠르게 사용할 수 있다.

Ubuntu는 WSL 위에 설치되는 리눅스 배포판이다. 수업의 리눅스 명령어는 대부분 Ubuntu 터미널 안에서 실행한다.

## 설치 전 확인

PowerShell을 열고 Windows 버전을 확인한다.

```powershell
# Windows 버전 정보를 확인한다
winver
```

WSL 설치 명령은 Windows 10 버전 2004, 빌드 19041 이상 또는 Windows 11에서 사용할 수 있다.

## WSL 설치

관리자 권한 PowerShell을 열고 실행한다.

```powershell
# WSL과 기본 Ubuntu 배포판을 설치한다
wsl --install
```

설치가 끝나면 Windows를 재시작한다. 처음 Ubuntu를 실행하면 리눅스 사용자 이름과 비밀번호를 만들게 된다. 비밀번호 입력 중에는 화면에 아무 글자도 보이지 않는 것이 정상이다.

설치 가능한 배포판 목록은 다음으로 확인한다.

```powershell
# 설치 가능한 리눅스 배포판 목록을 확인한다
wsl --list --online
```

Ubuntu를 명시해서 설치하려면 다음을 실행한다.

```powershell
# Ubuntu 배포판을 지정해 설치한다
wsl --install -d Ubuntu
```

설치가 0%에서 멈추거나 Microsoft Store 접근이 어려운 환경이면 다음 방식도 사용할 수 있다.

```powershell
# Microsoft Store 대신 웹 다운로드 방식으로 Ubuntu를 설치한다
wsl --install --web-download -d Ubuntu
```

## WSL 상태 확인

PowerShell에서 실행한다.

```powershell
# WSL의 기본 상태 정보를 확인한다
wsl --status

# WSL 버전 정보를 확인한다
wsl --version

# 설치된 배포판, 실행 상태, WSL 버전을 확인한다
wsl --list --verbose
```

`wsl --list --verbose` 출력에서 `VERSION`이 `2`이면 WSL 2로 실행 중이다.

기본 WSL 버전을 2로 지정하려면 다음을 실행한다.

```powershell
# 새 배포판의 기본 WSL 버전을 2로 지정한다
wsl --set-default-version 2
```

## Ubuntu 실행과 종료

PowerShell에서 기본 배포판을 실행한다.

```powershell
# 기본 WSL 배포판을 실행한다
wsl
```

홈 디렉터리에서 시작하려면 다음을 사용한다.

```powershell
# 기본 WSL 배포판을 홈 디렉터리에서 실행한다
wsl ~
```

Ubuntu 셸에서 빠져나오려면 다음을 입력한다.

```bash
# 현재 Ubuntu 셸을 종료한다
exit
```

실행 중인 모든 WSL 배포판과 WSL 2 가상 머신을 종료하려면 PowerShell에서 실행한다.

```powershell
# 실행 중인 모든 WSL 배포판과 WSL 가상 머신을 종료한다
wsl --shutdown
```

특정 배포판만 종료하려면 다음을 사용한다.

```powershell
# Ubuntu 배포판만 종료한다
wsl --terminate Ubuntu
```

주의: `wsl --unregister Ubuntu`는 Ubuntu 배포판과 내부 파일을 삭제한다. 수업 중에는 사용하지 않는다.

## Ubuntu 패키지 업데이트

Ubuntu 터미널에서 실행한다.

```bash
# 패키지 목록을 최신 상태로 갱신한다
sudo apt update

# 설치된 패키지를 최신 버전으로 업그레이드한다
sudo apt upgrade
```

`sudo`는 관리자 권한으로 명령을 실행한다는 뜻이다. 처음 실행할 때 Ubuntu 사용자 비밀번호를 묻는다.

## 실습 디렉터리 만들기

모든 수업 실습은 홈 디렉터리 아래 `linux-class`에서 진행한다.

```bash
# 실습 디렉터리를 만든다
mkdir -p ~/linux-class

# 실습 디렉터리로 이동한다
cd ~/linux-class

# 현재 위치를 확인한다
pwd
```

## Windows와 Linux 파일 위치

Ubuntu 홈 디렉터리는 보통 다음과 같은 Linux 경로이다.

```bash
# Ubuntu 홈 디렉터리 경로 예시이다
/home/사용자이름
```

Windows의 C 드라이브는 WSL에서 다음 위치에 연결된다.

```bash
# Windows C 드라이브가 WSL에 연결되는 위치이다
/mnt/c
```

예를 들어 Windows 다운로드 폴더는 대개 다음 경로이다.

```bash
# Windows 사용자 폴더 목록을 확인한다
ls /mnt/c/Users
```

현재 WSL 디렉터리를 Windows 파일 탐색기로 열려면 Ubuntu에서 실행한다.

```bash
# 현재 WSL 디렉터리를 Windows 파일 탐색기로 연다
explorer.exe .
```

성능을 위해 리눅스 명령어로 다루는 프로젝트는 `/home/사용자이름` 아래에 두는 것이 좋다. Windows 도구만 쓰는 파일은 `C:\Users\...` 아래에 두는 편이 자연스럽다.

## Windows 도구와 함께 쓰기

PowerShell에서 리눅스 명령을 한 번만 실행할 수 있다.

```powershell
# WSL 안에서 현재 디렉터리를 출력한다
wsl pwd

# WSL 안에서 현재 디렉터리의 파일 목록을 자세히 출력한다
wsl ls -la

# WSL 안에서 현재 날짜와 시간을 출력한다
wsl date
```

Ubuntu에서 Windows 프로그램을 실행할 수도 있다.

```bash
# Windows 메모장으로 Bash 설정 파일을 연다
notepad.exe ~/.bashrc

# 현재 Ubuntu 디렉터리를 Windows 파일 탐색기로 연다
explorer.exe .
```

## 확인 과제

1. PowerShell에서 설치된 WSL 배포판 이름과 버전을 확인한다.
2. Ubuntu에서 `~/linux-class` 디렉터리를 만들고 그 위치를 출력한다.
3. Ubuntu에서 `explorer.exe .`를 실행해 현재 폴더를 Windows 탐색기로 연다.
4. PowerShell에서 `wsl --shutdown`을 실행한 뒤 `wsl -l -v`로 상태가 바뀌는지 확인한다.

<details>
<summary>정답 예시</summary>

PowerShell에서 WSL 배포판과 버전을 확인한다.

```powershell
# 설치된 WSL 배포판과 버전을 확인한다
wsl -l -v
```

Ubuntu에서 실습 디렉터리를 만들고 위치를 확인한다.

```bash
# 실습 디렉터리를 만든다
mkdir -p ~/linux-class

# 실습 디렉터리로 이동한다
cd ~/linux-class

# 현재 위치를 출력한다
pwd
```

예상 출력은 `/home/사용자이름/linux-class` 형태이다.

현재 Ubuntu 디렉터리를 Windows 탐색기로 연다.

```bash
# 현재 Ubuntu 디렉터리를 Windows 파일 탐색기로 연다
explorer.exe .
```

PowerShell에서 WSL을 종료하고 상태를 확인한다.

```powershell
# 모든 WSL 배포판을 종료한다
wsl --shutdown

# 배포판 상태가 Stopped인지 확인한다
wsl -l -v
```

`STATE`가 `Stopped`로 보이면 정상이다.

</details>
