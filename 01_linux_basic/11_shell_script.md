# 11. 쉘 스크립트

## 학습 목표

- Bash 스크립트 파일을 만들고 실행한다.
- shebang, 실행 권한, 종료 상태를 이해한다.
- 변수, 인자, 조건문, 반복문, 함수를 사용한다.
- 자주 쓰는 명령어 묶음을 자동화한다.

## 스크립트란?

쉘 스크립트는 셸 명령어를 파일에 순서대로 적어 실행하는 자동화 파일이다. 반복 작업, 점검 명령, 파일 정리 작업에 자주 사용한다.

## 첫 스크립트

```bash
# 스크립트 실습 디렉터리를 만든다
mkdir -p ~/linux-class/script-lab

# 스크립트 실습 디렉터리로 이동한다
cd ~/linux-class/script-lab

# hello.sh 스크립트 파일을 작성한다
cat > hello.sh <<'EOF'
#!/usr/bin/env bash

echo "Hello, Linux"
echo "Current user: $USER"
echo "Current directory: $PWD"
EOF
```

실행 권한을 추가하고 실행한다.

```bash
# hello.sh에 실행 권한을 추가한다
chmod +x hello.sh

# 현재 디렉터리의 hello.sh를 실행한다
./hello.sh
```

첫 줄의 `#!/usr/bin/env bash`는 이 파일을 Bash로 실행하라는 뜻이다. 이를 shebang이라고 부른다.

## 실행 방법 차이

```bash
# Bash에 hello.sh 파일을 넘겨 실행한다
bash hello.sh

# 실행 권한이 있는 hello.sh 파일을 직접 실행한다
./hello.sh
```

`bash hello.sh`는 실행 권한이 없어도 Bash에 파일을 넘겨 실행한다. `./hello.sh`는 파일 자체를 실행하므로 실행 권한이 필요하다.

## 종료 상태

리눅스 명령은 실행 후 종료 상태를 남긴다. 보통 `0`은 성공, 0이 아닌 값은 실패이다.

```bash
# 존재하는 파일을 조회한다
ls hello.sh

# 직전 명령의 종료 상태를 확인한다
echo "$?"

# 없는 파일을 조회해 실패를 발생시킨다
ls missing-file

# 실패한 명령의 종료 상태를 확인한다
echo "$?"
```

## 인자 사용

```bash
# 인자를 사용하는 greet.sh 스크립트를 작성한다
cat > greet.sh <<'EOF'
#!/usr/bin/env bash

name="$1"
echo "Hello, $name"
echo "Script name: $0"
echo "Argument count: $#"
EOF

# greet.sh에 실행 권한을 추가한다
chmod +x greet.sh

# Kim을 첫 번째 인자로 전달해 실행한다
./greet.sh Kim
```

| 표현 | 의미 |
| --- | --- |
| `$0` | 스크립트 이름 |
| `$1`, `$2` | 첫 번째, 두 번째 인자 |
| `$#` | 인자 개수 |
| `$@` | 모든 인자 |
| `$?` | 직전 명령의 종료 상태 |

## 조건문

```bash
# 파일 존재 여부를 검사하는 스크립트를 작성한다
cat > check-file.sh <<'EOF'
#!/usr/bin/env bash

target="$1"

if [ -f "$target" ]; then
  echo "file exists: $target"
else
  echo "not a file: $target"
  exit 1
fi
EOF

# check-file.sh에 실행 권한을 추가한다
chmod +x check-file.sh

# 존재하는 파일을 인자로 넘겨 실행한다
./check-file.sh hello.sh

# 없는 파일을 인자로 넘겨 실행한다
./check-file.sh missing.txt
```

자주 쓰는 테스트 조건이다.

| 조건 | 의미 |
| --- | --- |
| `-f` | 일반 파일이면 참 |
| `-d` | 디렉터리면 참 |
| `-e` | 존재하면 참 |
| `-r` | 읽을 수 있으면 참 |
| `-x` | 실행할 수 있으면 참 |

## 반복문

```bash
# 여러 인자를 반복 처리하는 스크립트를 작성한다
cat > list-files.sh <<'EOF'
#!/usr/bin/env bash

for file in "$@"; do
  if [ -e "$file" ]; then
    ls -lh "$file"
  else
    echo "missing: $file"
  fi
done
EOF

# list-files.sh에 실행 권한을 추가한다
chmod +x list-files.sh

# 여러 파일명을 인자로 넘겨 실행한다
./list-files.sh hello.sh greet.sh missing.txt
```

## 함수

```bash
# 함수로 파일 백업을 처리하는 스크립트를 작성한다
cat > backup-one.sh <<'EOF'
#!/usr/bin/env bash

backup_file() {
  local src="$1"
  local dest="${src}.bak"
  cp "$src" "$dest"
  echo "created: $dest"
}

if [ $# -eq 0 ]; then
  echo "usage: $0 FILE..."
  exit 1
fi

for file in "$@"; do
  if [ -f "$file" ]; then
    backup_file "$file"
  else
    echo "skip: $file"
  fi
done
EOF

# backup-one.sh에 실행 권한을 추가한다
chmod +x backup-one.sh

# hello.sh와 greet.sh를 백업한다
./backup-one.sh hello.sh greet.sh

# 생성된 백업 파일을 확인한다
ls -lh *.bak
```

## 스크립트 작성 습관

- 변수는 큰따옴표로 감싼다: `"$name"`
- 실패할 수 있는 명령 뒤에는 결과를 확인한다.
- 위험한 삭제 명령은 먼저 `echo`로 대상 목록을 확인한다.
- 스크립트는 작은 기능부터 만들고 실행해 본다.

## 확인 과제

1. 이름을 인자로 받아 인사하는 스크립트를 만든다.
2. 파일 경로를 인자로 받아 파일인지 디렉터리인지 출력한다.
3. 여러 파일을 인자로 받아 크기를 출력하는 스크립트를 만든다.
4. `.txt` 파일만 `.bak`으로 복사하는 스크립트를 작성한다.
5. 인자가 없으면 사용법을 출력하고 종료 상태 1로 끝내게 만든다.

<details>
<summary>정답 예시</summary>

```bash
# 스크립트 실습 디렉터리로 이동한다
cd ~/linux-class/script-lab
```

이름을 인자로 받아 인사하는 스크립트이다.

```bash
# 이름을 인자로 받아 인사하는 스크립트를 작성한다
cat > answer-greet.sh <<'EOF'
#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  echo "usage: $0 NAME"
  exit 1
fi

echo "Hello, $1"
EOF

# 실행 권한을 추가한다
chmod +x answer-greet.sh

# Kim을 인자로 전달해 실행한다
./answer-greet.sh Kim
```

파일인지 디렉터리인지 출력하는 스크립트이다.

```bash
# 경로가 파일인지 디렉터리인지 검사하는 스크립트를 작성한다
cat > answer-type.sh <<'EOF'
#!/usr/bin/env bash

target="$1"

if [ $# -eq 0 ]; then
  echo "usage: $0 PATH"
  exit 1
elif [ -f "$target" ]; then
  echo "file: $target"
elif [ -d "$target" ]; then
  echo "directory: $target"
else
  echo "not found: $target"
  exit 1
fi
EOF

# 실행 권한을 추가한다
chmod +x answer-type.sh

# hello.sh가 파일인지 확인한다
./answer-type.sh hello.sh

# 현재 디렉터리가 디렉터리인지 확인한다
./answer-type.sh .
```

여러 파일의 크기를 출력하는 스크립트이다.

```bash
# 여러 파일의 크기를 출력하는 스크립트를 작성한다
cat > answer-size.sh <<'EOF'
#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  echo "usage: $0 FILE..."
  exit 1
fi

for file in "$@"; do
  if [ -f "$file" ]; then
    ls -lh "$file"
  else
    echo "skip: $file"
  fi
done
EOF

# 실행 권한을 추가한다
chmod +x answer-size.sh

# 여러 파일명을 인자로 넘겨 실행한다
./answer-size.sh hello.sh greet.sh missing.txt
```

`.txt` 파일만 `.bak`으로 복사하는 스크립트이다.

```bash
# .txt 파일만 백업하는 스크립트를 작성한다
cat > answer-backup-txt.sh <<'EOF'
#!/usr/bin/env bash

if [ $# -eq 0 ]; then
  echo "usage: $0 FILE..."
  exit 1
fi

for file in "$@"; do
  case "$file" in
    *.txt)
      if [ -f "$file" ]; then
        cp "$file" "$file.bak"
        echo "created: $file.bak"
      fi
      ;;
    *)
      echo "skip: $file"
      ;;
  esac
done
EOF

# 실행 권한을 추가한다
chmod +x answer-backup-txt.sh

# 테스트용 txt 파일과 md 파일을 만든다
touch a.txt b.md

# txt 파일만 백업되는지 확인한다
./answer-backup-txt.sh a.txt b.md

# 생성된 백업 파일을 확인한다
ls -l a.txt.bak
```

각 스크립트는 인자가 없으면 사용법을 출력하고 `exit 1`로 종료한다.

</details>
