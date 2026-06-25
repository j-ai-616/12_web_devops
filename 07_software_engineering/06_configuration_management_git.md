# 형상관리와 Git

## 학습 목표

- 형상관리의 목적과 주요 활동을 설명할 수 있다.
- Git 저장소를 만들고 파일의 변경 이력을 기록할 수 있다.
- 커밋을 조회하고 안전하게 작업을 되돌릴 수 있다.
- 브랜치를 생성, 병합하고 관리할 수 있다.
- GitHub 원격 저장소에 백업하고 여러 환경에서 동기화할 수 있다.
- 브랜치와 Pull Request를 이용한 협업 흐름을 설명할 수 있다.
- README와 기여 문서를 이용해 프로젝트 정보를 전달할 수 있다.

## 1. 형상관리란 무엇인가

형상관리는 소프트웨어를 구성하는 항목과 변경 이력을 식별하고 통제하는 활동이다. 소스 코드 버전관리보다 넓은 개념이다.

형상관리 대상에는 다음 항목이 포함될 수 있다.

- 요구사항과 설계 문서
- 소스 코드와 테스트 코드
- 데이터베이스 스키마
- 빌드와 배포 스크립트
- 환경 설정 파일
- 외부 라이브러리 버전
- 사용자 문서와 운영 절차

형상관리가 필요한 이유는 다음 질문에 답하기 위해서이다.

- 현재 배포된 버전은 무엇인가
- 누가 언제 무엇을 왜 변경했는가
- 변경 전후의 차이는 무엇인가
- 특정 버전의 파일을 다시 가져올 수 있는가
- 동시에 작업한 변경을 어떻게 합칠 것인가
- 승인되지 않은 변경이 포함되지 않았는가

## 2. 형상관리의 주요 활동

### 형상 식별

관리할 항목과 버전을 정한다. 파일, 디렉터리, 외부 패키지와 실행 이미지를 식별 가능한 이름으로 관리한다.

### 변경 통제

변경 요청을 검토하고 영향 범위와 승인 여부를 관리한다. 모든 변경을 막는 것이 아니라 변경의 이유와 결과를 알 수 있게 한다.

### 형상 상태 기록

어떤 변경이 어느 버전에 포함되었고 현재 상태가 무엇인지 기록한다.

### 형상 감사

승인된 요구사항과 설계, 코드, 테스트와 배포 결과가 서로 일치하는지 확인한다.

### 기준선

기준선은 검토와 승인을 거쳐 특정 단계의 기준으로 확정한 형상 항목의 집합이다. Git에서는 특정 커밋이나 태그를 기준선으로 사용할 수 있다.

## 3. Git과 GitHub

Git은 분산 버전관리 시스템이다. 각 저장소가 전체 변경 이력을 가지므로 네트워크가 없어도 커밋, 조회와 브랜치 작업을 할 수 있다.

GitHub는 Git 저장소를 인터넷에서 보관하고 협업 기능을 제공하는 서비스이다.

| 구분 | Git | GitHub |
| --- | --- | --- |
| 종류 | 버전관리 도구 | 원격 저장소 서비스 |
| 주요 기능 | 커밋, 브랜치, 병합, 이력 조회 | 저장소 호스팅, Issue, Pull Request, Review |
| 네트워크 | 로컬 작업은 필요하지 않다 | 원격 동기화에 필요하다 |
| 대안 | Git 자체를 사용한다 | GitLab, Bitbucket 등이 있다 |

Git을 사용한다고 GitHub가 반드시 필요한 것은 아니며, GitHub를 사용하려면 로컬에서 Git의 기본 개념을 이해해야 한다.

## 4. 명령 예시 사용 방법

명령 예시는 Git Bash, macOS와 Linux 셸에서 실행할 수 있는 형식이다. `#`으로 시작하는 줄은 명령의 의미를 설명하는 주석이다. Windows CMD에서는 `#` 주석 줄을 입력하지 않고 명령 줄만 실행한다. Git 명령 자체는 CMD와 PowerShell에서도 동일하다.

## 5. Git 시작하기

### Git 설치

### Windows

Git 공식 설치 프로그램인 Git for Windows를 설치하거나 Windows Package Manager를 사용할 수 있다.

```bash
# Windows Package Manager에서 Git 패키지를 설치한다.
winget install --id Git.Git -e --source winget

# 새 터미널을 연 뒤 설치된 Git 버전을 확인한다.
git --version
```

설치 프로그램을 사용하는 경우 기본 편집기, 기본 브랜치 이름과 줄바꿈 처리 방식을 선택할 수 있다. 설정은 설치 후에도 `git config`로 변경할 수 있다.

### macOS

```bash
# Git 설치 여부와 버전을 확인한다.
git --version

# Homebrew를 사용하는 경우 최신 Git 패키지를 설치한다.
brew install git
```

`git --version` 실행 시 Command Line Tools 설치 안내가 표시되면 안내에 따라 설치할 수 있다.

### Ubuntu와 Debian 계열

```bash
# 패키지 목록을 갱신한다.
sudo apt update

# Git 패키지를 설치한다.
sudo apt install -y git

# 설치된 Git 버전을 확인한다.
git --version
```

### Fedora 계열

```bash
# DNF 패키지 관리자로 Git을 설치한다.
sudo dnf install -y git

# 설치된 Git 버전을 확인한다.
git --version
```

### 사용자 정보 설정

커밋에는 작성자 이름과 이메일이 기록된다.

```bash
# 모든 로컬 저장소에서 사용할 작성자 이름을 설정한다.
git config --global user.name "사용자 이름"

# 모든 로컬 저장소에서 사용할 작성자 이메일을 설정한다.
git config --global user.email "user@example.com"

# 새 저장소의 기본 브랜치 이름을 main으로 설정한다.
git config --global init.defaultBranch main

# 전역 Git 설정과 설정 출처를 확인한다.
git config --global --list --show-origin
```

회사와 개인 저장소에서 다른 이메일을 사용하려면 특정 저장소 안에서 `--global`을 빼고 설정한다.

```bash
# 현재 저장소에서만 사용할 이메일을 설정한다.
git config user.email "work@example.com"

# 현재 저장소에 적용되는 작성자 정보를 확인한다.
git config user.name
git config user.email
```

### 줄바꿈 설정

Windows는 일반적으로 CRLF, macOS와 Linux는 LF 줄바꿈을 사용한다. Git 설정과 `.gitattributes`를 이용해 저장소에 기록할 형식을 통일할 수 있다.

```bash
# Windows에서 체크아웃 시 CRLF, 커밋 시 LF로 변환한다.
git config --global core.autocrlf true

# macOS와 Linux에서 커밋 시 CRLF를 LF로 변환한다.
git config --global core.autocrlf input
```

팀 저장소에서는 개인 설정에만 의존하지 않고 `.gitattributes`에 파일별 줄바꿈 규칙을 기록하는 편이 명확하다.

```gitattributes
# 일반 텍스트 파일의 줄바꿈을 저장소에서 LF로 정규화한다.
* text=auto eol=lf

# Windows 배치 파일은 CRLF로 체크아웃한다.
*.bat text eol=crlf
```

### 기본 셸 명령

Git은 현재 디렉터리를 기준으로 동작하므로 파일과 경로를 확인하는 명령을 알아야 한다.

```bash
# 현재 작업 중인 디렉터리의 절대 경로를 출력한다.
pwd

# 현재 디렉터리의 숨김 파일을 포함한 목록을 자세히 출력한다.
ls -la

# project 디렉터리로 이동한다.
cd project

# 상위 디렉터리로 이동한다.
cd ..

# example-project 디렉터리를 새로 만든다.
mkdir example-project

# 빈 README.md 파일을 만든다.
touch README.md

# README.md를 docs 디렉터리에 복사한다.
cp README.md docs/README.md

# old.txt의 이름을 new.txt로 변경한다.
mv old.txt new.txt
```

`rm`은 운영체제의 휴지통을 거치지 않고 파일을 삭제할 수 있다. 삭제 전에 현재 경로와 대상을 확인한다.

```bash
# 삭제 전에 현재 위치와 대상 파일을 확인한다.
pwd
ls -l temporary.txt

# 확인한 temporary.txt 파일을 삭제한다.
rm temporary.txt
```

## 6. Git으로 버전관리하기

### Git 저장소 만들기

Git 저장소는 프로젝트 파일과 변경 이력을 관리하는 디렉터리이다. 저장소 최상위에는 숨김 디렉터리인 `.git`이 만들어진다.

```bash
# 버전관리할 프로젝트 디렉터리를 만든다.
mkdir version-guide

# 만든 프로젝트 디렉터리로 이동한다.
cd version-guide

# 현재 디렉터리를 main 브랜치의 Git 저장소로 초기화한다.
git init -b main

# 저장소의 현재 파일 상태를 확인한다.
git status

# 저장소 최상위 경로를 확인한다.
git rev-parse --show-toplevel
```

`.git` 디렉터리에는 커밋, 브랜치와 설정 정보가 들어 있다. 이 디렉터리를 삭제하면 일반 파일은 남지만 Git 변경 이력과 저장소 정보는 사라진다.

### Git의 세 영역

Git은 파일 상태를 세 영역으로 나누어 관리한다.

```text
작업 디렉터리
  -> git add
스테이징 영역
  -> git commit
저장소
```

- 작업 디렉터리는 실제로 파일을 수정하는 공간이다.
- 스테이징 영역은 다음 커밋에 포함할 변경을 선택하는 공간이다.
- 저장소는 확정된 커밋 이력을 보관하는 공간이다.

### 파일 상태

| 상태 | 의미 |
| --- | --- |
| Untracked | Git이 아직 관리하지 않는 새 파일이다 |
| Unmodified | 마지막 커밋과 내용이 같다 |
| Modified | 추적 중인 파일이 수정되었다 |
| Staged | 다음 커밋에 포함하도록 선택되었다 |
| Committed | 변경이 로컬 저장소에 기록되었다 |

```bash
# 현재 파일의 상태를 자세히 확인한다.
git status

# 상태를 짧은 두 글자 형식으로 확인한다.
git status --short
```

`git status --short`에서 왼쪽 열은 스테이징 영역, 오른쪽 열은 작업 디렉터리 상태를 나타낸다.

### 첫 버전 만들기

```bash
# README.md 파일을 스테이징 영역에 추가한다.
git add README.md

# 스테이징 영역에 포함된 변경 내용을 확인한다.
git diff --staged

# 스테이징된 변경을 설명하는 메시지와 함께 커밋한다.
git commit -m "docs: add project introduction"

# 커밋 이력을 한 줄 형식으로 확인한다.
git log --oneline
```

`git add .`은 현재 디렉터리 아래의 모든 변경을 스테이징한다. 비밀값과 불필요한 파일이 포함되지 않았는지 `git status`와 `git diff --staged`로 먼저 확인한다.

```bash
# 현재 디렉터리 아래의 모든 변경을 스테이징한다.
git add .

# 커밋하기 전에 포함될 파일과 상태를 다시 확인한다.
git status

# 스테이징된 실제 변경 내용을 확인한다.
git diff --staged
```

### 좋은 커밋

좋은 커밋은 하나의 목적을 가진 변경을 완결된 단위로 기록한다.

- 관련 없는 변경을 한 커밋에 섞지 않는다.
- 가능한 한 실행과 테스트가 가능한 상태로 기록한다.
- 무엇을 했는지보다 왜 변경했는지를 메시지에 드러낸다.
- 생성 파일, 비밀값과 개인 설정을 포함하지 않는다.

메시지 예시는 다음과 같다.

```text
feat: add password reset endpoint
fix: reject orders with zero quantity
test: add boundary cases for shipping fee
docs: explain local setup
refactor: separate payment gateway adapter
```

### 커밋 내용 확인하기

```bash
# 커밋 이력을 작성자와 날짜를 포함해 확인한다.
git log

# 커밋 그래프와 브랜치를 한 줄 형식으로 확인한다.
git log --oneline --graph --decorate --all

# 가장 최근 커밋의 메타데이터와 변경 내용을 확인한다.
git show HEAD

# 지정한 커밋의 변경 내용을 확인한다.
git show <COMMIT_HASH>

# 최근 커밋에 포함된 파일 이름과 상태만 확인한다.
git show --name-status --oneline HEAD
```

`HEAD`는 현재 체크아웃한 커밋을 가리킨다. `HEAD~1`은 현재 커밋의 첫 번째 부모, 즉 일반적인 경우 바로 이전 커밋을 가리킨다.

### 버전마다 파일 상태 확인하기

```bash
# 작업 디렉터리의 수정 내용과 스테이징 전 차이를 확인한다.
git diff

# 스테이징 영역과 마지막 커밋의 차이를 확인한다.
git diff --staged

# 두 커밋 사이의 전체 차이를 확인한다.
git diff <OLD_COMMIT> <NEW_COMMIT>

# 특정 커밋 시점의 README.md 내용을 출력한다.
git show <COMMIT_HASH>:README.md

# 특정 파일의 변경 이력을 확인한다.
git log --follow -- README.md
```

`--follow`는 이름이 변경된 파일의 이전 이력까지 추적할 때 사용한다.

### `.gitignore`

Git으로 관리하지 않을 파일과 디렉터리 패턴을 `.gitignore`에 기록한다.

```gitignore
# Python 캐시와 가상환경
__pycache__/
*.pyc
.venv/

# 로컬 환경 변수와 비밀값
.env
.env.*
!.env.example

# 편집기와 운영체제 파일
.vscode/
.DS_Store

# 빌드 결과
dist/
build/
```

이미 커밋한 파일은 `.gitignore`에 추가해도 자동으로 추적이 중지되지 않는다.

```bash
# 파일은 로컬에 남기고 Git의 추적 대상에서만 제거한다.
git rm --cached .env

# 추적 제거 내용을 커밋한다.
git commit -m "chore: stop tracking local environment file"
```

비밀값이 이미 커밋되었다면 추적 제거만으로 과거 이력에서 사라지지 않는다. 해당 키와 비밀번호를 먼저 폐기하고 새 값으로 교체해야 한다.

### 작업 되돌리기

되돌리기 전에 현재 상태와 잃게 될 변경을 확인한다.

### 스테이징하지 않은 수정 취소

```bash
# 취소 전에 README.md의 현재 수정 내용을 확인한다.
git diff -- README.md

# README.md를 마지막 커밋 상태로 되돌린다.
# 커밋하지 않은 수정 내용은 사라지므로 주의한다.
git restore README.md
```

### 스테이징 취소

```bash
# README.md를 다음 커밋 대상에서 제외하고 수정 내용은 유지한다.
git restore --staged README.md

# 작업 디렉터리에 수정 내용이 남았는지 확인한다.
git status
```

### 마지막 커밋 수정

```bash
# 빠진 변경을 스테이징한다.
git add README.md

# 새 커밋을 만들지 않고 마지막 커밋을 다시 작성한다.
# 이미 공유한 커밋에는 사용하지 않는 편이 안전하다.
git commit --amend
```

### 공유한 커밋 되돌리기

```bash
# 지정한 커밋의 반대 변경을 담은 새 커밋을 만든다.
git revert <COMMIT_HASH>
```

`git revert`는 기존 이력을 지우지 않으므로 이미 원격 저장소에 공유한 변경을 취소할 때 적합하다.

`git reset --hard`는 커밋 위치와 작업 디렉터리를 함께 바꾸며 커밋하지 않은 변경을 잃을 수 있다. 사용 전 복구해야 할 변경과 공유 여부를 반드시 확인한다.

## 7. Git과 브랜치

### 브랜치란 무엇인가

브랜치는 특정 커밋을 가리키는 이동 가능한 이름이다. 독립된 작업 공간 전체를 복사하는 것이 아니라 커밋 이력의 한 지점을 가리킨다.

```text
A---B---C  main
     \
      D---E  feature/login
```

기능 개발, 오류 수정과 실험을 기본 브랜치와 분리해 진행할 수 있다.

### 브랜치 만들기

```bash
# 현재 브랜치와 로컬 브랜치 목록을 확인한다.
git branch

# feature/login 브랜치를 만들고 바로 전환한다.
git switch -c feature/login

# 현재 브랜치 이름을 확인한다.
git branch --show-current

# 모든 브랜치의 최근 커밋을 확인한다.
git branch -v
```

`git switch -c`는 브랜치 생성과 전환을 함께 수행한다. 기존 브랜치로 이동할 때는 `git switch <BRANCH_NAME>`을 사용한다.

### 브랜치에서 작업하기

```bash
# 현재 브랜치의 변경 상태를 확인한다.
git status

# 기능 변경 파일을 스테이징한다.
git add src/login.py tests/test_login.py

# 관련 기능과 테스트를 하나의 커밋으로 기록한다.
git commit -m "feat: add login validation"

# 브랜치가 나뉜 모습을 그래프로 확인한다.
git log --oneline --graph --decorate --all
```

브랜치를 바꾸기 전에 작업 디렉터리를 커밋하거나 임시 저장해 현재 변경이 다른 브랜치와 섞이지 않게 한다.

### 브랜치 병합하기

```bash
# 병합 결과를 받을 main 브랜치로 전환한다.
git switch main

# feature/login 브랜치의 변경을 현재 main에 병합한다.
git merge feature/login

# 병합 후 커밋 그래프를 확인한다.
git log --oneline --graph --decorate --all
```

### Fast-forward 병합

기본 브랜치에 새 커밋이 없다면 브랜치 포인터만 앞으로 이동한다.

### 삼방향 병합(3-way merge)

두 브랜치 모두 새 커밋이 있다면 공통 조상과 두 브랜치의 변경을 비교해 병합 커밋을 만들 수 있다.

### 병합 충돌

같은 파일의 같은 부분을 서로 다르게 수정하면 Git이 자동으로 선택하지 못하고 충돌을 표시한다.

```text
<<<<<<< HEAD
현재 브랜치의 내용
=======
병합할 브랜치의 내용
>>>>>>> feature/login
```

충돌 해결 순서는 다음과 같다.

1. `git status`로 충돌 파일을 확인한다.
2. 두 변경의 의도를 이해한다.
3. 최종으로 남길 내용을 직접 작성한다.
4. 충돌 표시를 모두 제거한다.
5. 테스트를 실행한다.
6. 해결한 파일을 `git add`로 표시한다.
7. 병합 커밋을 완료한다.

```bash
# 충돌 파일과 병합 상태를 확인한다.
git status

# 해결한 파일을 스테이징해 충돌 해결을 표시한다.
git add src/login.py

# 모든 충돌을 해결한 뒤 병합 커밋을 완료한다.
git commit
```

병합 전체를 취소하고 시작 전 상태로 돌아갈 수도 있다.

```bash
# 아직 병합 커밋을 완료하지 않은 병합 작업을 취소한다.
git merge --abort
```

### 브랜치 관리

```bash
# 이미 병합한 feature/login 로컬 브랜치를 삭제한다.
git branch -d feature/login

# 병합 여부와 관계없이 브랜치를 강제로 삭제한다.
# 포함된 커밋을 잃을 수 있으므로 사용 전 이력을 확인한다.
git branch -D feature/login

# 병합된 로컬 브랜치 목록을 확인한다.
git branch --merged

# 아직 병합되지 않은 로컬 브랜치 목록을 확인한다.
git branch --no-merged
```

브랜치를 삭제해도 해당 커밋이 다른 브랜치나 태그에서 참조되면 커밋은 사라지지 않는다.

## 8. GitHub로 백업하기

### 원격 저장소

원격 저장소는 네트워크를 통해 접근하는 Git 저장소이다. `origin`은 복제하거나 처음 연결한 원격 저장소에 일반적으로 사용하는 별칭이다.

```bash
# 현재 등록된 원격 저장소의 이름과 주소를 확인한다.
git remote -v

# origin이라는 이름으로 GitHub 저장소 주소를 등록한다.
git remote add origin git@github.com:<OWNER>/<REPOSITORY>.git

# origin의 상세 주소와 추적 정보를 확인한다.
git remote show origin
```

`<OWNER>`와 `<REPOSITORY>`는 실제 GitHub 계정 또는 Organization과 저장소 이름으로 바꾼다.

### 원격 저장소에 올리고 내려받기

```bash
# 로컬 main 브랜치를 origin에 처음 올리고 추적 관계를 설정한다.
git push -u origin main

# 이후 현재 브랜치의 새 커밋을 추적 중인 원격 브랜치에 올린다.
git push

# 원격 저장소의 새 커밋과 브랜치 정보를 가져오되 자동 병합하지 않는다.
git fetch origin

# 가져온 origin/main과 로컬 main의 차이를 확인한다.
git log --oneline --left-right main...origin/main

# 원격 변경을 가져와 현재 브랜치에 통합한다.
git pull
```

`git pull`은 일반적으로 `fetch` 후 설정된 방식으로 merge 또는 rebase를 수행한다. 원격 변경을 먼저 살펴보려면 `git fetch`와 `git log`를 나누어 사용한다.

### GitHub SSH 연결

SSH 키는 공개키와 개인키 한 쌍으로 인증한다. 공개키는 GitHub에 등록하고 개인키는 로컬 장치에만 보관한다.

```bash
# Ed25519 방식의 새 SSH 키를 만든다.
# 이메일은 키를 구분하는 설명으로 기록된다.
ssh-keygen -t ed25519 -C "user@example.com"

# 현재 셸에서 SSH Agent를 시작한다.
eval "$(ssh-agent -s)"

# 생성한 개인키를 SSH Agent에 등록한다.
ssh-add ~/.ssh/id_ed25519

# GitHub에 등록할 공개키 내용을 출력한다.
cat ~/.ssh/id_ed25519.pub
```

출력한 공개키를 GitHub의 `Settings -> SSH and GPG keys -> New SSH key`에 등록한다. `id_ed25519`는 개인키이고 `id_ed25519.pub`는 공개키이다. 개인키 내용은 GitHub나 저장소에 올리지 않는다.

```bash
# SSH로 GitHub 인증이 되는지 확인한다.
ssh -T git@github.com
```

최초 연결에서는 GitHub 호스트 키를 신뢰할지 묻는 메시지가 표시될 수 있다. 표시된 지문이 GitHub가 공개한 지문과 일치하는지 확인한 뒤 등록한다.

### 원격 주소 변경

```bash
# origin 주소를 HTTPS에서 SSH 주소로 변경한다.
git remote set-url origin git@github.com:<OWNER>/<REPOSITORY>.git

# 변경된 원격 주소를 확인한다.
git remote -v
```

### 저장소 복제

```bash
# GitHub 저장소의 전체 이력을 로컬 디렉터리로 복제한다.
git clone git@github.com:<OWNER>/<REPOSITORY>.git

# 복제된 저장소 디렉터리로 이동한다.
cd <REPOSITORY>

# 로컬과 원격 브랜치 목록을 확인한다.
git branch -a
```

`git clone`은 파일 다운로드뿐 아니라 `.git` 이력과 `origin` 원격 주소를 함께 설정한다.

## 9. GitHub로 협업하기

### 여러 컴퓨터에서 저장소 사용하기

첫 번째 컴퓨터에서 커밋을 GitHub에 push한 뒤 다른 컴퓨터에서 clone하거나 pull할 수 있다.

```bash
# 새 컴퓨터에서 저장소 전체를 처음 가져온다.
git clone git@github.com:<OWNER>/<REPOSITORY>.git

# 이미 복제한 저장소에서는 원격의 새 정보를 가져온다.
git fetch origin

# 현재 브랜치와 원격 추적 상태를 확인한다.
git status

# 현재 브랜치에 원격 변경을 통합한다.
git pull
```

작업을 시작하기 전에 원격 변경을 가져오고, 커밋을 push한 뒤 다른 장치에서 작업한다. 같은 브랜치에 서로 다른 커밋이 생기면 먼저 원격 변경을 통합해야 한다.

### 원격 브랜치 정보 가져오기

```bash
# 원격의 최신 커밋, 브랜치와 태그 정보를 가져온다.
git fetch origin

# 원격 브랜치 목록을 확인한다.
git branch -r

# 모든 로컬 브랜치의 원격 추적 관계를 확인한다.
git branch -vv

# origin의 feature/search를 추적하는 로컬 브랜치를 만든다.
git switch --track origin/feature/search

# 원격에서 삭제된 브랜치 참조를 로컬에서도 정리한다.
git fetch --prune origin
```

`fetch`는 작업 파일을 자동으로 바꾸지 않으므로 원격 변경을 안전하게 확인하는 데 적합하다.

### 협업의 기본 흐름

```text
Issue 또는 작업 확인
  -> 최신 main 가져오기
  -> 작업 브랜치 생성
  -> 작은 단위로 구현과 테스트
  -> 커밋
  -> 원격 브랜치 push
  -> Pull Request 생성
  -> 코드 리뷰와 수정
  -> 테스트 성공
  -> main에 병합
  -> 작업 브랜치 정리
```

작업 시작 명령은 다음과 같다.

```bash
# main 브랜치로 이동한다.
git switch main

# 원격 main의 최신 변경을 가져와 통합한다.
git pull origin main

# 작업 목적을 나타내는 새 브랜치를 만들고 이동한다.
git switch -c feature/search-filter
```

작업 완료 후 원격에 올린다.

```bash
# 변경 파일과 스테이징 상태를 확인한다.
git status

# 관련 변경을 선택해 스테이징한다.
git add src/search.py tests/test_search.py

# 하나의 목적을 설명하는 커밋을 만든다.
git commit -m "feat: add category search filter"

# 새 브랜치를 origin에 올리고 추적 관계를 설정한다.
git push -u origin feature/search-filter
```

GitHub에서 `feature/search-filter`를 `main`으로 병합하는 Pull Request를 만든다.

### 협업에서 브랜치 사용하기

브랜치 이름은 목적을 드러내도록 작성한다.

```text
feature/password-reset
fix/order-total
docs/api-guide
refactor/payment-adapter
```

브랜치 운영 원칙의 예시는 다음과 같다.

- `main`은 배포 가능한 상태로 유지한다.
- 작업은 목적별 브랜치에서 진행한다.
- Pull Request 전에 테스트를 실행한다.
- 큰 변경을 작은 Pull Request로 나눈다.
- 리뷰가 끝난 브랜치를 병합한다.
- 병합한 작업 브랜치는 정리한다.

### 작업 중 main 변경 반영하기

작업하는 동안 `main`에 새 커밋이 생길 수 있다.

```bash
# 원격의 최신 정보를 가져온다.
git fetch origin

# 작업 브랜치에 원격 main의 변경을 병합한다.
git merge origin/main

# 충돌을 해결하고 테스트한 뒤 작업 브랜치를 다시 올린다.
git push
```

팀이 rebase 방식을 사용한다면 정해진 규칙을 따른다. 이미 공유한 브랜치의 이력을 다시 작성한 뒤 강제 push하면 다른 작업자의 이력과 충돌할 수 있다.

### Pull Request

Pull Request는 브랜치 변경을 기본 브랜치에 병합하기 전에 설명, 자동 테스트와 리뷰를 모으는 공간이다.

좋은 Pull Request에는 다음 내용이 포함된다.

- 해결하려는 문제와 관련 Issue
- 주요 변경 내용
- 선택한 구현 방법과 이유
- 테스트 방법과 결과
- 화면 변경이 있으면 비교 자료
- 알려진 제약과 후속 작업

제목과 본문은 변경된 파일 목록보다 변경의 목적을 설명해야 한다.

### 코드 리뷰

코드 리뷰는 오류 찾기뿐 아니라 설계 의도와 지식을 공유하는 활동이다.

검토할 항목은 다음과 같다.

- 요구사항과 인수 조건을 만족하는가
- 코드의 책임과 이름이 명확한가
- 오류와 경계 조건을 처리하는가
- 보안과 개인정보 문제가 없는가
- 테스트가 핵심 동작을 검증하는가
- 불필요하게 복잡한 구조가 없는가
- 문서와 설정 변경이 함께 반영되었는가

리뷰 의견은 사람보다 코드와 영향에 집중한다.

```text
"이 코드는 이상하다"
보다
"빈 목록에서 index 오류가 발생할 수 있다. 빈 입력 테스트와 예외 처리가 필요하다"
처럼 관찰 가능한 근거를 작성한다.
```

### Fork를 이용한 협업

원본 저장소에 직접 push 권한이 없을 때 자신의 계정으로 Fork한 뒤 Pull Request를 만들 수 있다.

```text
원본 저장소 upstream
  -> 개인 계정으로 Fork
  -> 개인 저장소 origin을 clone
  -> 작업 브랜치에서 변경
  -> origin에 push
  -> upstream으로 Pull Request
```

원본 저장소를 `upstream`이라는 이름으로 등록할 수 있다.

```bash
# 원본 프로젝트 저장소를 upstream으로 등록한다.
git remote add upstream git@github.com:<ORIGINAL_OWNER>/<REPOSITORY>.git

# origin과 upstream 주소를 함께 확인한다.
git remote -v

# 원본 저장소의 최신 변경을 가져온다.
git fetch upstream

# 로컬 main에 원본 main의 변경을 통합한다.
git switch main
git merge upstream/main
```

## 10. GitHub에서 개발자와 소통하기

### GitHub 프로필 관리

GitHub 프로필은 활동과 관심 분야를 보여 주는 공간이다.

사용자 이름과 같은 이름의 공개 저장소를 만들고 루트에 `README.md`를 두면 프로필 README로 표시할 수 있다.

프로필에 포함할 수 있는 내용은 다음과 같다.

- 소개와 관심 분야
- 사용하는 기술
- 대표 프로젝트
- 연락 방법
- 현재 학습하거나 기여하는 주제

이메일, 전화번호와 토큰 같은 민감한 정보는 공개 저장소에 기록하지 않는다.

### README 파일 작성하기

README는 저장소를 처음 방문한 사람이 프로젝트의 목적과 사용 방법을 이해하도록 돕는 문서이다.

### 기본 구성

```markdown
# 프로젝트 이름

프로젝트가 해결하는 문제와 주요 기능을 설명한다.

## 주요 기능

- 기능 A
- 기능 B

## 실행 환경

- Python 3.12
- PostgreSQL 16

## 설치

설치 명령과 필요한 환경 변수를 설명한다.

## 실행

개발 서버와 테스트 실행 방법을 설명한다.

## 프로젝트 구조

주요 디렉터리와 책임을 설명한다.

## 기여 방법

Issue, 브랜치, 테스트와 Pull Request 규칙을 설명한다.

## 라이선스

사용과 배포 조건을 설명한다.
```

README에는 실제로 확인한 명령을 기록한다. 운영체제나 버전에 따라 절차가 다르면 구분해서 설명한다.

### Issue로 소통하기

Issue는 오류, 기능 요청, 질문과 작업을 기록하는 공간이다.

좋은 오류 Issue에는 다음 내용이 필요하다.

- 문제를 한 문장으로 설명한 제목
- 재현 절차
- 예상 결과와 실제 결과
- 실행 환경과 버전
- 오류 메시지와 필요한 로그
- 민감한 정보가 제거된 화면이나 예제

기능 요청에는 해결하려는 문제, 사용자 가치, 범위와 완료 기준을 기록한다.

### 오픈소스 프로젝트에 기여하기

기여 전에 저장소의 다음 파일을 확인한다.

- `README.md`: 프로젝트의 목적과 실행 방법이다.
- `CONTRIBUTING.md`: 기여 절차와 코딩 규칙이다.
- `CODE_OF_CONDUCT.md`: 커뮤니티 행동 기준이다.
- `LICENSE`: 코드의 사용과 배포 조건이다.
- Issue와 Pull Request 템플릿: 필요한 작성 형식이다.

일반적인 기여 흐름은 다음과 같다.

1. 기존 Issue와 Pull Request에서 같은 문제가 있는지 검색한다.
2. 기여 지침과 개발 환경을 확인한다.
3. 큰 변경은 구현 전에 Issue에서 방향을 논의한다.
4. 저장소를 Fork하고 작업 브랜치를 만든다.
5. 작은 범위로 변경하고 관련 테스트를 추가한다.
6. 프로젝트의 전체 테스트와 검사 도구를 실행한다.
7. 변경 이유와 테스트 결과를 설명한 Pull Request를 만든다.
8. 리뷰 의견을 반영하고 필요한 토론을 진행한다.

### 저장소에 올리면 안 되는 정보

- Access Key와 Secret Key
- 비밀번호와 개인키
- 실제 서비스의 `.env` 파일
- 개인정보와 운영 데이터
- 라이선스를 확인하지 않은 자료
- 불필요하게 큰 생성 파일

비밀값이 커밋되었다면 파일을 삭제하는 것만으로 충분하지 않다. 과거 커밋에서 확인할 수 있으므로 해당 자격 증명을 즉시 폐기하고 교체해야 한다.

### 자주 사용하는 상태 확인 명령

```bash
# 현재 브랜치와 파일 상태를 확인한다.
git status

# 작업 디렉터리의 수정 내용을 확인한다.
git diff

# 스테이징된 변경을 확인한다.
git diff --staged

# 모든 브랜치의 커밋 흐름을 그래프로 확인한다.
git log --oneline --graph --decorate --all

# 로컬과 원격 브랜치의 추적 관계를 확인한다.
git branch -vv

# 등록된 원격 저장소 주소를 확인한다.
git remote -v
```

문제가 생겼을 때 바로 되돌리기 명령을 실행하기보다 `status`, `diff`, `log`로 현재 상태를 먼저 확인한다.

### 기본 작업 흐름 요약

### 개인 작업

```bash
# 변경 전 현재 브랜치와 상태를 확인한다.
git status

# 작업 내용을 수정한 뒤 차이를 확인한다.
git diff

# 커밋할 변경만 선택한다.
git add <FILE>

# 스테이징된 최종 변경을 확인한다.
git diff --staged

# 변경 목적을 설명하는 커밋을 만든다.
git commit -m "type: describe the change"

# 커밋 이력을 확인한다.
git log --oneline
```

### 협업 작업

```bash
# 기본 브랜치의 최신 변경을 가져온다.
git switch main
git pull origin main

# 작업용 브랜치를 만든다.
git switch -c feature/example

# 변경을 커밋한다.
git add <FILE>
git commit -m "feat: add example feature"

# 원격에 작업 브랜치를 올린다.
git push -u origin feature/example
```

그다음 GitHub에서 Pull Request를 만들고 자동 테스트와 코드 리뷰를 거쳐 병합한다.

## 핵심 정리

- 형상관리는 소스 코드뿐 아니라 요구사항, 설정, 빌드와 배포 결과의 변경을 통제한다.
- Git은 작업 디렉터리, 스테이징 영역과 저장소를 구분한다.
- 커밋은 하나의 목적을 가진 검토 가능한 변경 단위로 만든다.
- 브랜치는 독립적인 변경 흐름을 만들고 병합으로 결과를 통합한다.
- 원격 저장소는 협업과 백업에 사용하며 SSH 키의 개인키는 공개하지 않는다.
- GitHub 협업은 Issue, 브랜치, Pull Request, 리뷰와 자동 테스트를 중심으로 진행한다.

## 확인 문제

1. Git과 GitHub의 차이를 설명한다.
2. 작업 디렉터리, 스테이징 영역과 저장소의 역할을 설명한다.
3. 이미 공유한 커밋을 취소할 때 `git revert`가 적합한 이유를 설명한다.
4. `git fetch`와 `git pull`의 차이를 설명한다.
5. Pull Request에 테스트 방법과 결과를 기록해야 하는 이유를 설명한다.

<details>
<summary>정답 예시</summary>

1. Git은 로컬에서도 사용할 수 있는 분산 버전관리 도구이고, GitHub는 Git 저장소 호스팅과 Issue, Pull Request, 리뷰 같은 협업 기능을 제공하는 서비스이다.
2. 작업 디렉터리는 실제 파일을 수정하는 공간이고, 스테이징 영역은 다음 커밋에 포함할 변경을 선택하는 공간이며, 저장소는 확정된 커밋 이력을 보관한다.
3. 기존 이력을 삭제하거나 다시 작성하지 않고 해당 변경의 반대 내용을 새 커밋으로 남기므로 다른 작업자와 공유한 이력을 유지할 수 있기 때문이다.
4. `git fetch`는 원격 이력과 브랜치 정보만 가져오고 현재 작업 파일을 바꾸지 않는다. `git pull`은 원격 정보를 가져온 뒤 현재 브랜치에 merge 또는 rebase로 통합한다.
5. 변경이 어떤 조건에서 검증되었는지 리뷰어가 확인하고, 병합 후 회귀 위험과 재현 방법을 판단할 수 있기 때문이다.

</details>
