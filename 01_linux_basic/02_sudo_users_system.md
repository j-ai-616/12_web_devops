# 02. sudo와 시스템 기초

## 학습 목표

- 리눅스의 사용자, 그룹, 관리자 권한을 이해한다.
- `sudo`가 필요한 상황과 사용 방법을 익힌다.
- WSL 환경에서 시스템 시작과 종료를 구분한다.
- 현재 로그인한 사용자와 권한 정보를 확인한다.

## 사용자와 관리자

리눅스는 여러 사용자가 함께 쓰는 운영체제로 설계되었다. 각 사용자는 고유한 사용자 ID를 가지고, 하나 이상의 그룹에 속한다.

관리자 계정은 보통 `root`라고 부른다. `root`는 시스템 전체를 변경할 수 있으므로 평소에는 일반 사용자로 작업하고, 필요한 순간에만 `sudo`로 관리자 권한을 빌려 쓴다.

## 사용자와 그룹 확인

Ubuntu 터미널에서 실행한다.

```bash
# 현재 사용자 이름을 출력한다
whoami

# 현재 사용자의 UID, GID, 그룹 정보를 출력한다
id

# 현재 사용자가 속한 그룹 이름을 출력한다
groups

# 현재 사용자 계정 정보를 passwd 데이터베이스에서 조회한다
getent passwd "$USER"

# sudo 그룹에 속한 사용자를 조회한다
getent group sudo
```

| 명령어 | 의미 |
| --- | --- |
| `whoami` | 현재 사용자 이름 출력 |
| `id` | 사용자 ID와 그룹 ID 출력 |
| `groups` | 현재 사용자가 속한 그룹 출력 |
| `getent passwd "$USER"` | 현재 사용자 계정 정보 조회 |
| `getent group sudo` | `sudo` 그룹 정보 조회 |

Ubuntu에서 설치 중 만든 첫 사용자는 보통 `sudo` 그룹에 속한다.

## sudo 이해

`sudo`는 "superuser do"의 줄임말로, 특정 명령을 관리자 권한으로 실행한다.

```bash
# sudo 비밀번호를 확인하고 인증 시간을 갱신한다
sudo -v

# 현재 사용자의 sudo 권한 범위를 확인한다
sudo -l

# 관리자 권한으로 root 홈 디렉터리 목록을 확인한다
sudo ls /root
```

`sudo -v`는 비밀번호를 확인하고 sudo 권한을 일정 시간 갱신한다. `sudo -l`은 현재 사용자가 실행할 수 있는 sudo 권한을 보여준다.

sudo 인증 정보를 지우고 다시 비밀번호를 묻게 하려면 다음을 실행한다.

```bash
# 기존 sudo 인증 정보를 지운다
sudo -k

# 다시 sudo 인증을 수행한다
sudo -v
```

## sudo가 필요한 예

시스템 패키지 목록 업데이트는 관리자 권한이 필요하다.

```bash
# 관리자 권한으로 패키지 목록을 갱신한다
sudo apt update
```

일반 사용자가 시스템 디렉터리에 파일을 만들려고 하면 실패한다.

```bash
# 일반 사용자 권한으로 시스템 디렉터리에 파일 생성을 시도한다
touch /usr/local/test-file
```

관리자 권한으로는 가능하지만, 수업에서는 시스템 디렉터리를 어지럽히지 않도록 만들었다가 바로 지운다.

```bash
# 관리자 권한으로 테스트 파일을 만든다
sudo touch /usr/local/test-file

# 생성된 파일의 권한과 소유자를 확인한다
ls -l /usr/local/test-file

# 관리자 권한으로 테스트 파일을 삭제한다
sudo rm /usr/local/test-file
```

## root 셸과 sudo의 차이

`sudo 명령어`는 한 번의 명령만 관리자 권한으로 실행한다. 반면 `sudo -i`는 root 로그인 셸로 들어간다. 초보 단계에서는 실수 범위가 커지므로 `sudo -i`는 되도록 사용하지 않는다.

```bash
# 관리자 권한으로 실행될 때의 사용자 이름을 확인한다
sudo whoami

# 일반 사용자로 실행될 때의 사용자 이름을 확인한다
whoami
```

첫 번째 명령은 `root`, 두 번째 명령은 내 사용자 이름을 출력한다.

## 시스템 시작과 종료

일반 리눅스 서버에서는 `shutdown`, `reboot`, `systemctl` 같은 명령으로 시스템을 종료하거나 재시작한다. WSL에서는 Windows가 WSL 배포판을 관리하므로 PowerShell의 `wsl` 명령으로 시작과 종료를 다룬다.

PowerShell에서 실행한다.

```powershell
# WSL 배포판의 실행 상태와 버전을 확인한다
wsl -l -v

# 기본 WSL 배포판을 실행한다
wsl

# Ubuntu 배포판만 종료한다
wsl --terminate Ubuntu

# 모든 WSL 배포판과 WSL 가상 머신을 종료한다
wsl --shutdown
```

Ubuntu 안에서는 현재 셸을 종료할 때 `exit`을 사용한다.

```bash
# 현재 Ubuntu 셸을 종료한다
exit
```

## systemd 확인

일부 WSL 환경에서는 `systemd`가 활성화되어 있다. 현재 1번 프로세스를 확인한다.

```bash
# PID 1번 프로세스의 이름과 실행 인자를 확인한다
ps -p 1 -o pid,comm,args
```

`systemd`가 보이면 `systemctl` 명령을 사용할 수 있다.

```bash
# systemd 버전을 확인한다
systemctl --version

# systemd 전체 상태를 확인한다
systemctl status
```

`systemctl`이 동작하지 않아도 수업의 기본 리눅스 명령어 학습에는 문제가 없다.

## 확인 과제

1. 현재 사용자가 속한 그룹 목록을 확인한다.
2. `sudo whoami`와 `whoami`의 출력 차이를 설명한다.
3. PowerShell에서 Ubuntu의 실행 상태를 확인하고 종료한다.
4. Ubuntu에서 1번 프로세스가 무엇인지 확인한다.

<details>
<summary>정답 예시</summary>

현재 사용자가 속한 그룹은 다음 명령으로 확인한다.

```bash
# 현재 사용자가 속한 그룹 이름을 확인한다
groups

# UID, GID, 그룹 정보를 함께 확인한다
id
```

`whoami`는 현재 일반 사용자 이름을 출력하고, `sudo whoami`는 관리자 권한으로 실행되므로 `root`를 출력한다.

```bash
# 일반 사용자 이름을 확인한다
whoami

# sudo로 실행했을 때 root가 되는지 확인한다
sudo whoami
```

PowerShell에서 Ubuntu 실행 상태를 확인하고 종료한다.

```powershell
# WSL 상태를 확인한다
wsl -l -v

# Ubuntu 배포판을 종료한다
wsl --terminate Ubuntu

# 종료 후 상태를 다시 확인한다
wsl -l -v
```

전체 WSL 환경을 종료하려면 다음을 사용한다.

```powershell
# 모든 WSL 배포판을 종료한다
wsl --shutdown
```

Ubuntu에서 1번 프로세스는 다음 명령으로 확인한다.

```bash
# PID 1번 프로세스 정보를 확인한다
ps -p 1 -o pid,comm,args
```

`comm` 값이 `systemd`이면 systemd가 1번 프로세스이다.

</details>
