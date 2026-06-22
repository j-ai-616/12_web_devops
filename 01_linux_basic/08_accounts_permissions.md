# 08. 계정과 권한

## 학습 목표

- 리눅스 파일 권한 표기법을 읽는다.
- 소유자, 그룹, 기타 사용자의 권한을 구분한다.
- `chmod`, `chown`, `chgrp`, `umask`를 이해한다.
- 계정과 그룹 관리 명령을 실습 환경에서 조심스럽게 다룬다.

## 권한 표기 읽기

```bash
# 현재 디렉터리 파일의 권한, 소유자, 그룹을 자세히 출력한다
ls -l
```

출력 예시는 다음과 같다.

```text
-rw-r--r-- 1 user user 12 Jun 19 10:00 note.txt
```

첫 번째 글자는 파일 종류이다.

| 문자 | 의미 |
| --- | --- |
| `-` | 일반 파일 |
| `d` | 디렉터리 |
| `l` | 심볼릭 링크 |

그 뒤 9글자는 세 묶음이다.

```text
rw- r-- r--
소유자 그룹 기타사용자
```

| 권한 | 파일에서 의미 | 디렉터리에서 의미 |
| --- | --- | --- |
| `r` | 읽기 | 목록 보기 |
| `w` | 수정 | 파일 생성/삭제/이름 변경 |
| `x` | 실행 | 디렉터리 안으로 진입 |

## 실습 준비

```bash
# 권한 실습 디렉터리를 만든다
mkdir -p ~/linux-class/permission-lab

# 권한 실습 디렉터리로 이동한다
cd ~/linux-class/permission-lab

# secret.txt에 실습 내용을 작성한다
printf "secret\n" > secret.txt

# data 디렉터리를 만든다
mkdir data

# 파일과 디렉터리 권한을 확인한다
ls -l
```

## chmod: 권한 변경

기호 방식이다.

```bash
# 소유자에게 실행 권한을 추가한다
chmod u+x secret.txt

# 변경된 권한을 확인한다
ls -l secret.txt

# 그룹에서 읽기 권한을 제거한다
chmod g-r secret.txt

# 변경된 권한을 확인한다
ls -l secret.txt

# 기타 사용자 권한을 모두 제거한다
chmod o= secret.txt

# 변경된 권한을 확인한다
ls -l secret.txt
```

숫자 방식이다.

| 숫자 | 권한 |
| --- | --- |
| `7` | `rwx` |
| `6` | `rw-` |
| `5` | `r-x` |
| `4` | `r--` |
| `0` | `---` |

```bash
# secret.txt 권한을 644로 설정한다
chmod 644 secret.txt

# 파일 권한을 확인한다
ls -l secret.txt

# data 디렉터리 권한을 700으로 설정한다
chmod 700 data

# 디렉터리 자체의 권한을 확인한다
ls -ld data
```

## 디렉터리 실행 권한

디렉터리의 `x` 권한은 그 안으로 들어갈 수 있는 권한이다.

```bash
# 디렉터리 실행 권한 실습용 디렉터리를 만든다
mkdir sample-dir

# 디렉터리 안에 파일을 만든다
touch sample-dir/a.txt

# 디렉터리 권한을 600으로 바꿔 실행 권한을 제거한다
chmod 600 sample-dir

# 디렉터리 목록 접근을 시도한다
ls sample-dir

# 디렉터리 권한을 다시 700으로 복구한다
chmod 700 sample-dir

# 복구 후 목록을 확인한다
ls sample-dir
```

## 소유자와 그룹

현재 파일의 소유자를 확인한다.

```bash
# 파일의 소유자, 그룹, 권한, 시간 정보를 자세히 확인한다
stat secret.txt

# 현재 사용자의 UID, GID, 그룹을 확인한다
id

# 현재 사용자가 속한 그룹 이름을 확인한다
groups
```

소유자 변경은 관리자 권한이 필요하다.

```bash
# secret.txt의 소유자와 그룹을 현재 사용자로 변경한다
sudo chown "$USER":"$USER" secret.txt
```

그룹 변경은 사용자가 속한 그룹 안에서 가능하다.

```bash
# secret.txt의 그룹을 현재 사용자의 기본 그룹으로 변경한다
chgrp "$(id -gn)" secret.txt
```

## umask

`umask`는 새 파일과 디렉터리를 만들 때 기본 권한에서 빼는 값이다.

```bash
# 현재 umask 값을 확인한다
umask

# umask가 적용될 파일을 만든다
touch umask-file.txt

# umask가 적용될 디렉터리를 만든다
mkdir umask-dir

# 새 파일의 기본 권한을 확인한다
ls -l umask-file.txt

# 새 디렉터리의 기본 권한을 확인한다
ls -ld umask-dir
```

임시로 `umask`를 바꿔 본다.

```bash
# 새 파일과 디렉터리의 기타 권한을 강하게 제한한다
umask 077

# 제한된 umask 상태에서 파일을 만든다
touch private.txt

# 제한된 umask 상태에서 디렉터리를 만든다
mkdir private-dir

# 새 파일 권한을 확인한다
ls -l private.txt

# 새 디렉터리 권한을 확인한다
ls -ld private-dir
```

새 터미널을 열면 보통 기본값으로 돌아간다.

## 계정과 그룹 관리

계정 생성과 삭제는 시스템에 영향을 준다. 개인 WSL 실습 환경에서만 실행한다.

```bash
# student1 계정을 만든다
sudo adduser student1

# student1 계정 정보를 확인한다
getent passwd student1

# student1을 sudo 그룹에 추가한다
sudo usermod -aG sudo student1

# student1이 속한 그룹을 확인한다
groups student1
```

실습 후 계정을 삭제하려면 다음을 사용한다.

```bash
# student1 계정을 삭제한다
sudo deluser student1
```

홈 디렉터리까지 지우려면 `--remove-home` 옵션이 있지만, 삭제 전 반드시 대상 계정을 확인한다.

## 확인 과제

1. `note.txt`를 만들고 권한을 `600`으로 변경한다.
2. `public.txt`를 만들고 권한을 `644`로 변경한다.
3. `script.sh`를 만들고 실행 권한을 추가한다.
4. 디렉터리에서 `x` 권한을 제거했을 때 어떤 일이 생기는지 확인한다.
5. `umask 077` 상태에서 새 파일을 만들고 기본 권한을 확인한다.

<details>
<summary>정답 예시</summary>

```bash
# 권한 실습 디렉터리로 이동한다
cd ~/linux-class/permission-lab
```

`note.txt`를 만들고 권한을 `600`으로 변경한다.

```bash
# note.txt 파일을 만든다
touch note.txt

# 소유자만 읽고 쓸 수 있게 권한을 600으로 설정한다
chmod 600 note.txt

# 권한을 확인한다
ls -l note.txt
```

`public.txt`를 만들고 권한을 `644`로 변경한다.

```bash
# public.txt 파일을 만든다
touch public.txt

# 소유자는 읽기/쓰기, 나머지는 읽기만 가능하게 설정한다
chmod 644 public.txt

# 권한을 확인한다
ls -l public.txt
```

`script.sh`에 실행 권한을 추가한다.

```bash
# 간단한 스크립트 파일을 만든다
printf '#!/usr/bin/env bash\necho hello\n' > script.sh

# 소유자에게 실행 권한을 추가한다
chmod u+x script.sh

# 권한을 확인한다
ls -l script.sh

# 스크립트를 실행한다
./script.sh
```

디렉터리의 `x` 권한을 제거하고 결과를 확인한다.

```bash
# 실행 권한 실습용 디렉터리를 만든다
mkdir -p no-exec-dir

# 디렉터리 안에 파일을 만든다
touch no-exec-dir/a.txt

# 디렉터리 실행 권한을 제거한다
chmod 600 no-exec-dir

# 접근이 제한되는지 확인한다
ls no-exec-dir

# 실습 후 권한을 복구한다
chmod 700 no-exec-dir
```

`x` 권한이 없으면 디렉터리 안으로 접근하거나 목록을 제대로 읽기 어렵다.

`umask 077` 상태에서 새 파일을 만든다.

```bash
# umask를 077로 설정해 새 파일 권한을 제한한다
umask 077

# 새 파일을 만든다
touch private-answer.txt

# 새 파일의 기본 권한을 확인한다
ls -l private-answer.txt
```

권한이 보통 `-rw-------` 형태이면 정상이다.

</details>
