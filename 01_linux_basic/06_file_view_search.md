# 06. 파일 확인과 검색

## 학습 목표

- 텍스트 파일 내용을 다양한 방식으로 확인한다.
- 파일 종류, 크기, 수정 시간 같은 메타데이터를 조회한다.
- `find`로 파일 이름과 조건을 검색한다.
- `grep`으로 파일 내용에서 패턴을 찾는다.

## 실습 준비

```bash
# 검색 실습용 로그 디렉터리를 만든다
mkdir -p ~/linux-class/search-lab/logs

# 검색 실습 디렉터리로 이동한다
cd ~/linux-class/search-lab

# fruits.txt에 과일 목록을 작성한다
printf "apple\nbanana\ncarrot\napple pie\n" > fruits.txt

# logs/app.log에 로그 예시를 작성한다
printf "INFO start\nWARN disk\nERROR network\nINFO done\n" > logs/app.log

# notes.txt에 검색할 문장을 작성한다
printf "Linux shell\nLinux file\nWindows WSL\n" > notes.txt

# 비어 있는 파일을 만든다
touch empty.txt
```

## 파일 내용 확인

```bash
# 파일 전체 내용을 출력한다
cat fruits.txt

# 줄 번호와 함께 파일 내용을 출력한다
nl fruits.txt

# 파일의 앞 2줄을 출력한다
head -n 2 fruits.txt

# 파일의 뒤 2줄을 출력한다
tail -n 2 fruits.txt

# 줄 수, 단어 수, 바이트 수를 출력한다
wc fruits.txt
```

| 명령어 | 설명 |
| --- | --- |
| `cat` | 파일 전체 출력 |
| `nl` | 줄 번호와 함께 출력 |
| `head` | 앞부분 출력 |
| `tail` | 뒷부분 출력 |
| `wc` | 줄 수, 단어 수, 바이트 수 출력 |

긴 파일은 `less`로 본다.

```bash
# 긴 파일을 페이지 단위로 확인한다
less logs/app.log
```

`less` 안에서는 `q`로 종료하고, `/검색어`로 검색한다.

## 파일 정보 확인

```bash
# 현재 디렉터리의 파일 목록을 사람이 읽기 쉬운 크기로 출력한다
ls -lh

# 파일 종류를 추정한다
file fruits.txt

# 파일의 자세한 메타데이터를 출력한다
stat fruits.txt

# 현재 디렉터리 전체 사용량을 확인한다
du -sh .
```

`file`은 파일 종류를 추정하고, `stat`은 권한, 소유자, 크기, 시간 정보를 자세히 보여준다.

## find로 파일 검색

현재 디렉터리 아래 모든 파일을 찾는다.

```bash
# 현재 디렉터리 아래의 일반 파일을 모두 찾는다
find . -type f
```

이름으로 찾는다.

```bash
# 이름이 .txt로 끝나는 파일을 찾는다
find . -name "*.txt"

# 이름이 .log로 끝나는 파일을 찾는다
find . -name "*.log"
```

크기와 수정 시간 조건을 사용할 수 있다.

```bash
# 크기가 0인 빈 파일을 찾는다
find . -type f -size 0

# 최근 1일 안에 수정된 파일을 찾는다
find . -type f -mtime -1
```

검색한 파일에 명령을 실행할 수도 있다.

```bash
# 찾은 .txt 파일마다 ls -lh 명령을 실행한다
find . -name "*.txt" -exec ls -lh {} \;
```

## grep으로 내용 검색

```bash
# fruits.txt에서 apple이 포함된 줄을 찾는다
grep "apple" fruits.txt

# notes.txt에서 Linux가 포함된 줄을 줄 번호와 함께 찾는다
grep -n "Linux" notes.txt

# 대소문자를 무시하고 linux를 찾는다
grep -i "linux" notes.txt

# 현재 디렉터리 아래 모든 파일에서 ERROR를 찾는다
grep -R "ERROR" .
```

| 옵션 | 설명 |
| --- | --- |
| `-n` | 줄 번호 표시 |
| `-i` | 대소문자 무시 |
| `-R` | 하위 디렉터리까지 재귀 검색 |
| `-v` | 일치하지 않는 줄 출력 |
| `-E` | 확장 정규식 사용 |

정규식 예제이다.

```bash
# INFO 또는 WARN이 포함된 줄을 찾는다
grep -E "INFO|WARN" logs/app.log

# ERROR로 시작하는 줄을 찾는다
grep -E "^ERROR" logs/app.log

# apple로 끝나는 줄을 찾는다
grep -E "apple$" fruits.txt
```

## 명령어 위치 검색

```bash
# grep 명령의 종류와 위치를 확인한다
type grep

# grep 실행 파일 경로를 확인한다
command -v grep

# grep 관련 실행 파일과 문서 위치를 찾는다
whereis grep
```

`type`은 셸이 실제로 어떤 명령을 실행하는지 확인할 때 가장 먼저 사용하기 좋다.

## 확인 과제

1. `logs/app.log`에서 `WARN` 또는 `ERROR`가 들어간 줄만 출력한다.
2. 현재 디렉터리 아래 비어 있는 파일을 찾는다.
3. `*.txt` 파일의 크기를 `ls -lh` 형태로 출력한다.
4. `notes.txt`에서 대소문자를 무시하고 `linux`를 검색한다.
5. `/etc` 아래에서 이름이 `hosts`인 파일을 찾아본다.

<details>
<summary>정답 예시</summary>

```bash
# 검색 실습 디렉터리로 이동한다
cd ~/linux-class/search-lab
```

`WARN` 또는 `ERROR`가 들어간 줄만 출력한다.

```bash
# WARN 또는 ERROR가 포함된 로그 줄을 출력한다
grep -E "WARN|ERROR" logs/app.log
```

현재 디렉터리 아래 비어 있는 파일을 찾는다.

```bash
# 현재 디렉터리 아래 크기가 0인 파일을 찾는다
find . -type f -size 0
```

`*.txt` 파일의 크기를 확인한다.

```bash
# .txt 파일마다 자세한 파일 정보를 출력한다
find . -name "*.txt" -exec ls -lh {} \;
```

대소문자를 무시하고 `linux`를 검색한다.

```bash
# notes.txt에서 linux를 대소문자 구분 없이 검색한다
grep -i "linux" notes.txt
```

`/etc` 아래에서 이름이 `hosts`인 파일을 찾는다.

```bash
# /etc 아래 hosts 파일을 찾고 권한 오류는 숨긴다
find /etc -name hosts 2>/dev/null
```

일반적으로 `/etc/hosts`가 출력된다.

</details>
