# 05. 파일과 디렉터리

## 학습 목표

- 리눅스 파일 시스템의 계층 구조를 이해한다.
- 절대 경로와 상대 경로를 구분한다.
- 파일과 디렉터리를 생성, 복사, 이동, 삭제한다.
- 하드 링크와 심볼릭 링크의 차이를 확인한다.

## 파일 시스템 구조

리눅스의 최상위 디렉터리는 `/`이다. Windows처럼 `C:\`, `D:\`로 시작하지 않고 모든 경로가 `/` 아래에 놓인다.

| 경로 | 역할 |
| --- | --- |
| `/` | 최상위 디렉터리 |
| `/home` | 일반 사용자 홈 디렉터리 |
| `/etc` | 시스템 설정 파일 |
| `/bin`, `/usr/bin` | 실행 명령어 |
| `/var` | 로그, 캐시처럼 변하는 데이터 |
| `/tmp` | 임시 파일 |
| `/mnt/c` | WSL에서 보이는 Windows C 드라이브 |

## 절대 경로와 상대 경로

절대 경로는 `/`부터 시작하는 전체 경로이다. 상대 경로는 현재 디렉터리를 기준으로 한 경로이다.

```bash
# 현재 작업 디렉터리를 출력한다
pwd

# 현재 사용자의 홈 디렉터리로 이동한다
cd ~

# 홈 디렉터리 경로를 확인한다
pwd

# 시스템 설정 디렉터리로 이동한다
cd /etc

# /etc 경로에 있는지 확인한다
pwd

# 수업 실습 디렉터리로 이동한다
cd ~/linux-class
```

| 표현 | 의미 |
| --- | --- |
| `.` | 현재 디렉터리 |
| `..` | 부모 디렉터리 |
| `~` | 현재 사용자의 홈 디렉터리 |
| `-` | 바로 이전 디렉터리 |

```bash
# 수업 실습 디렉터리로 이동한다
cd ~/linux-class

# 부모 디렉터리로 이동한다
cd ..

# 이동한 위치를 확인한다
pwd

# 바로 이전 디렉터리로 돌아간다
cd -

# 다시 수업 실습 디렉터리인지 확인한다
pwd
```

## 실습 준비

```bash
# 파일 실습용 디렉터리를 만든다
mkdir -p ~/linux-class/file-lab

# 파일 실습용 디렉터리로 이동한다
cd ~/linux-class/file-lab

# 현재 위치를 확인한다
pwd
```

## 파일과 디렉터리 만들기

```bash
# docs, logs, backup 디렉터리를 만든다
mkdir docs logs backup

# 빈 readme.txt 파일을 만든다
touch docs/readme.txt

# hello.txt 파일에 문자열을 저장한다
printf "hello linux\n" > docs/hello.txt

# 현재 디렉터리의 파일과 디렉터리를 확인한다
ls

# docs 디렉터리 안의 파일을 자세히 확인한다
ls -l docs
```

`mkdir -p`는 중간 디렉터리가 없어도 함께 만든다.

```bash
# 중간 디렉터리까지 한 번에 만든다
mkdir -p project/src project/test project/docs

# project 아래 2단계 깊이까지 디렉터리만 출력한다
find project -maxdepth 2 -type d
```

## 복사와 이동

```bash
# hello.txt를 backup 디렉터리에 복사한다
cp docs/hello.txt backup/hello-copy.txt

# 복사된 파일을 확인한다
ls -l backup

# 복사된 파일 이름을 변경한다
mv backup/hello-copy.txt backup/hello-moved.txt

# 변경된 파일 이름을 확인한다
ls -l backup
```

디렉터리를 복사하려면 `-r` 옵션을 사용한다.

```bash
# docs 디렉터리를 docs-copy로 재귀 복사한다
cp -r docs docs-copy

# 복사된 디렉터리 안의 일반 파일을 확인한다
find docs-copy -maxdepth 1 -type f
```

## 삭제

삭제는 되돌리기 어렵다. 실습에서는 항상 수업용 디렉터리 안에서만 삭제한다.

```bash
# 삭제 전 확인 질문을 받으며 파일을 삭제한다
rm -i backup/hello-moved.txt

# 비어 있는 logs 디렉터리를 삭제한다
rmdir logs

# 내용이 있는 docs-copy 디렉터리를 삭제한다
rm -r docs-copy
```

`rm -i`는 삭제 전에 확인 질문을 한다. 빈 디렉터리는 `rmdir`로 삭제할 수 있고, 내용이 있는 디렉터리는 `rm -r`이 필요하다.

## 파일 이름과 와일드카드

```bash
# 여러 실습 파일을 만든다
touch report1.txt report2.txt report-final.md image.png

# .txt로 끝나는 파일만 출력한다
ls *.txt

# report 뒤에 글자 하나가 있는 .txt 파일을 출력한다
ls report?.txt

# report로 시작하는 모든 파일을 출력한다
ls report*
```

공백이 있는 파일명은 따옴표로 감싼다.

```bash
# 공백이 있는 파일 이름은 따옴표로 감싸 만든다
touch "class note.txt"

# 공백이 있는 파일 정보를 확인한다
ls -l "class note.txt"
```

## 링크

심볼릭 링크는 Windows의 바로가기와 비슷하게 원본 경로를 가리킨다.

```bash
# docs/hello.txt를 가리키는 심볼릭 링크를 만든다
ln -s docs/hello.txt hello-link.txt

# 심볼릭 링크가 어디를 가리키는지 확인한다
ls -l hello-link.txt

# 심볼릭 링크를 통해 원본 파일 내용을 읽는다
cat hello-link.txt
```

하드 링크는 같은 파일 내용을 가리키는 또 다른 이름이다.

```bash
# docs/hello.txt의 하드 링크를 만든다
ln docs/hello.txt hello-hard.txt

# inode 번호를 확인해 두 이름이 같은 파일 데이터를 가리키는지 본다
ls -li docs/hello.txt hello-hard.txt
```

`ls -li`에서 inode 번호가 같으면 같은 파일 데이터를 가리킨다.

## WSL 경로 주의

Windows 파일은 `/mnt/c` 아래에서 접근할 수 있다.

```bash
# WSL에서 Windows 사용자 폴더 목록을 확인한다
ls /mnt/c/Users
```

리눅스 도구로 많이 다루는 수업 파일은 `~/linux-class`처럼 Linux 홈 디렉터리 아래에 두는 것이 좋다. Windows 드라이브(`/mnt/c`)에서 대량 파일 작업을 하면 느릴 수 있다.

## 확인 과제

1. `~/linux-class/file-lab/practice` 디렉터리를 만든다.
2. 그 안에 `a.txt`, `b.txt`, `memo.md` 파일을 만든다.
3. `*.txt` 파일만 `backup` 디렉터리로 복사한다.
4. `memo.md`의 심볼릭 링크 `memo-link.md`를 만든다.
5. `find`로 전체 구조를 확인한다.

<details>
<summary>정답 예시</summary>

```bash
# 파일 실습 디렉터리로 이동한다
cd ~/linux-class/file-lab

# 과제용 practice와 backup 디렉터리를 만든다
mkdir -p practice backup

# 과제용 파일 3개를 만든다
touch practice/a.txt practice/b.txt practice/memo.md

# practice 안의 .txt 파일만 backup으로 복사한다
cp practice/*.txt backup/

# memo.md를 가리키는 심볼릭 링크를 만든다
ln -s practice/memo.md memo-link.md

# 현재 구조를 2단계 깊이까지 확인한다
find . -maxdepth 2 -print
```

`backup` 디렉터리에는 `a.txt`, `b.txt`만 있어야 한다.

```bash
# backup 디렉터리에 복사된 파일을 확인한다
ls backup
```

심볼릭 링크는 `ls -l`로 확인한다.

```bash
# 심볼릭 링크가 가리키는 대상을 확인한다
ls -l memo-link.md
```

출력에 `memo-link.md -> practice/memo.md` 형태가 보이면 정상이다.

</details>
