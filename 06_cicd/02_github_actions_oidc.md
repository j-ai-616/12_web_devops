# GitHub Actions와 AWS OIDC

## 학습 목표

- CI, Continuous Delivery와 Continuous Deployment를 구분할 수 있다.
- 제공 프로젝트의 GitHub Actions Workflow 구조를 설명할 수 있다.
- 테스트 성공 후에만 ECR 이미지를 만드는 품질 게이트를 확인할 수 있다.
- GitHub OIDC로 임시 AWS 권한을 받아 ECR에 이미지를 push할 수 있다.

## 1. CI/CD란 무엇인가

### CI

Continuous Integration은 코드 변경을 자주 합치고 자동 검사와 테스트로 문제를 빠르게 찾는 과정이다. GitHub에 코드를 올리는 행위 자체보다 변경된 코드가 기존 기능을 깨뜨리지 않았는지 자동으로 확인하는 것이 핵심이다.

### Continuous Delivery

테스트를 통과한 결과물을 언제든 배포할 수 있는 상태로 만드는 과정이다. 실제 배포 시작은 사람이 결정할 수 있다.

### Continuous Deployment

테스트와 빌드가 성공하면 운영 환경 배포까지 자동으로 진행하는 과정이다. 제공 프로젝트의 최종 Workflow는 main 브랜치의 변경을 EC2까지 자동 배포할 수 있게 준비되어 있다.

```text
코드 변경
  -> Django 검사와 테스트
  -> 컨테이너 테스트
  -> 이미지 빌드
  -> ECR push
  -> SSM 기반 EC2 배포
```

앞 단계가 실패하면 뒤 단계는 실행하지 않는다. 이 경계를 품질 게이트라고 한다.

## 2. GitHub Actions 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Workflow | `.github/workflows/*.yml`에 정의한 자동화 전체이다. |
| Event | push, pull request처럼 Workflow를 시작하는 사건이다. |
| Job | 하나의 Runner에서 실행되는 Step 묶음이다. |
| Step | 명령이나 Action을 실행하는 한 단계이다. |
| Action | 여러 Workflow에서 재사용하는 자동화 기능이다. |
| Runner | Workflow 명령을 실제로 실행하는 가상 머신이다. |

Job은 서로 다른 Runner에서 실행될 수 있다. `needs`를 사용하면 앞 Job이 성공한 경우에만 다음 Job을 시작한다.

로컬 개발 명령은 VS Code의 CMD 터미널에서 실행하지만 제공 Workflow의 Runner는 Ubuntu Linux이다. Workflow 파일의 `run`에 적힌 Bash 명령은 학생의 Windows가 아니라 GitHub가 만든 Linux Runner에서 실행된다.

## 3. 로컬 프로젝트와 Workflow 확인

```bat
REM 현재 터미널이 프로젝트 루트에 있는지 확인한다.
cd

REM 현재 브랜치와 변경 파일을 확인한다.
git status

REM 로컬 Django 설정과 테스트를 다시 실행한다.
python manage.py check
python manage.py test

REM 제공된 GitHub Actions Workflow를 VS Code로 연다.
code .github/workflows/deploy.yml
```

Workflow에는 세 Job이 들어 있다.

| Job | 실행 조건 | 역할 |
| --- | --- | --- |
| `test` | Pull Request와 main push | Python 검사, Django 테스트와 컨테이너 테스트를 실행한다. |
| `build-and-push` | main push, `test` 성공 | AMD64 이미지를 만들어 ECR에 push한다. |
| `deploy` | `build-and-push` 성공, `EC2_INSTANCE_ID` 존재 | SSM으로 EC2 배포 스크립트를 실행한다. |

현재는 GitHub에 `EC2_INSTANCE_ID`를 등록하지 않았으므로 첫 push에서 `deploy` Job은 건너뛴다. 다음 문서에서 EC2 배포를 준비한 뒤 변수와 권한을 추가하면 같은 Workflow의 deploy Job이 활성화된다.

## 4. GitHub 저장소 만들기

1. GitHub에서 새 비공개 저장소 `cloud-class-app`을 만든다.
2. README, `.gitignore`, License 자동 생성은 선택하지 않는다.
3. 저장소 소유자 이름과 URL을 기록한다.

```bat
REM GitHub 저장소를 origin 원격으로 등록한다.
git remote add origin https://github.com/<GITHUB_OWNER>/cloud-class-app.git

REM 등록한 원격 저장소 주소를 확인한다.
git remote -v
```

아직 push하지 않는다. AWS 역할과 GitHub 변수를 먼저 준비한다.

## 5. 장기 Access Key를 저장하지 않는 이유

GitHub Actions가 ECR에 이미지를 올리려면 AWS 권한이 필요하다. Access Key와 Secret Key를 GitHub Secrets에 저장하면 키가 유출되거나 교체되지 않았을 때 오랫동안 사용할 수 있다는 문제가 있다.

OIDC는 GitHub가 현재 Workflow를 증명하는 짧은 수명의 토큰을 발급하고 AWS가 토큰을 확인한 뒤 IAM Role의 임시 자격 증명을 제공하는 방식이다.

```text
GitHub Actions
  -> OIDC 토큰 발급
  -> AWS가 저장소와 브랜치 확인
  -> IAM Role 임시 자격 증명 발급
  -> ECR push
```

## 6. GitHub OIDC 공급자 등록

AWS IAM에 `token.actions.githubusercontent.com` 공급자가 이미 있으면 다시 만들지 않는다.

1. AWS IAM에서 `Identity providers`를 연다.
2. `Add provider`를 선택한다.
3. 유형은 OpenID Connect를 선택한다.
4. Provider URL에 `https://token.actions.githubusercontent.com`을 입력한다.
5. Audience에 `sts.amazonaws.com`을 입력한다.
6. 설정을 확인하고 공급자를 추가한다.

OIDC 공급자는 GitHub 토큰을 AWS가 신뢰할 수 있는지 검증한다. 이 단계만으로 GitHub에 AWS 권한이 생기는 것은 아니다.

## 7. GitHub Actions용 IAM Role 만들기

IAM 역할 이름은 `cloud-class-github-role`로 한다. 신뢰 정책의 `<AWS_ACCOUNT_ID>`와 `<GITHUB_OWNER>`를 실제 값으로 바꾼다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_OWNER>/cloud-class-app:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

`aud` 조건은 토큰이 AWS STS를 대상으로 발급되었는지 확인한다. `sub` 조건은 지정한 저장소의 main 브랜치 Workflow만 역할을 맡도록 제한한다.

역할을 만든 뒤 ARN을 기록한다.

```text
arn:aws:iam::<AWS_ACCOUNT_ID>:role/cloud-class-github-role
```

## 8. GitHub 역할에 ECR push 권한 추가

`cloud-class-github-role`에 `cloud-class-github-ecr-policy` 인라인 정책을 추가한다. `<AWS_ACCOUNT_ID>`를 실제 값으로 바꾼다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:CompleteLayerUpload",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": "arn:aws:ecr:ap-northeast-2:<AWS_ACCOUNT_ID>:repository/cloud-class-app"
    }
  ]
}
```

`ecr:BatchGetImage`과 `ecr:GetDownloadUrlForLayer`는 Buildx가 저장소의 기존 이미지와 레이어를 확인할 때 사용한다. 이미지 업로드 권한만 있고 이 조회 권한이 없으면 ECR 로그인은 성공해도 이미지 push 단계에서 거부될 수 있다.

이 역할은 지정한 ECR 저장소에 이미지를 push할 수 있지만 EC2나 RDS를 생성·삭제할 수는 없다.

## 9. GitHub Repository Variables 등록

GitHub 저장소의 `Settings -> Secrets and variables -> Actions -> Variables`에서 다음 변수를 만든다.

| 변수 | 값 |
| --- | --- |
| `AWS_ROLE_ARN` | `cloud-class-github-role`의 ARN |
| `AWS_REGION` | `ap-northeast-2` |
| `ECR_REPOSITORY` | `cloud-class-app` |

`EC2_INSTANCE_ID`는 아직 만들지 않는다. 이 변수가 없으면 제공 Workflow의 deploy Job은 자동으로 건너뛴다.

## 10. 품질 게이트 확인

Workflow의 다음 연결을 찾는다.

```text
test
  -> needs: test
build-and-push
  -> needs: build-and-push
deploy
```

`test` Job은 다음 검사를 수행한다.

1. Python 패키지를 설치한다.
2. `python manage.py check`를 실행한다.
3. `python manage.py test`를 실행한다.
4. `linux/amd64` 테스트 이미지를 만든다.
5. 이미지 내부에서 Django 테스트를 다시 실행한다.

`build-and-push`는 이 Job이 성공한 경우에만 시작한다. Pull Request에서는 테스트만 실행하고 ECR push와 배포는 수행하지 않는다.

## 11. 첫 push와 Workflow 실행

```bat
REM 포함 프로젝트의 모든 파일이 커밋되었는지 확인한다.
git status

REM main 브랜치를 GitHub에 처음 올린다.
git push -u origin main
```

GitHub Actions에서 `test`, `build-and-push`가 성공하고 `deploy`는 Skipped인지 확인한다.

## 12. ECR 결과 확인

ECR의 `cloud-class-app` 저장소에서 다음 항목을 확인한다.

- `latest` 태그가 있다.
- 현재 Git 커밋의 전체 SHA 태그가 있다.
- 두 태그가 같은 이미지 다이제스트를 가리킨다.
- 이미지가 AMD64 Linux에서 실행 가능한 형태이다.
- 이미지 스캔 상태가 표시된다.

## 13. 테스트 실패가 배포를 막는지 확인

로컬에서 `core/tests.py`의 기대 문자열을 임시로 다른 값으로 바꾸고 테스트를 실행한다.

```bat
REM 의도적으로 실패하게 만든 테스트를 실행한다.
python manage.py test
```

실패 메시지를 확인한 뒤 원래 값으로 되돌리고 다시 실행한다.

```bat
REM 수정한 테스트가 다시 성공하는지 확인한다.
python manage.py test

REM 실수로 변경한 파일이 남지 않았는지 확인한다.
git diff
```

실패 상태를 main에 push하지 않는다. 이 단계는 테스트 실패 메시지를 읽는 연습이다.

## 문제 해결

### Django 테스트가 실패한다

- 실패한 테스트 이름과 예상값, 실제값을 확인한다.
- 로컬에서 같은 `python manage.py test`를 실행한다.
- `requirements.txt`와 커밋된 소스가 최신인지 확인한다.

### OIDC 역할을 맡지 못한다

- `build-and-push` Job에 `id-token: write` 권한이 있는지 확인한다.
- Role ARN과 AWS 계정 ID를 확인한다.
- 신뢰 정책의 GitHub 소유자, 저장소와 브랜치 대소문자를 확인한다.
- OIDC Audience가 `sts.amazonaws.com`인지 확인한다.

### ECR push가 거부된다

- 역할 정책의 ECR 저장소 ARN을 확인한다.
- ECR 저장소와 Workflow 리전이 같은지 확인한다.
- `ecr:GetAuthorizationToken` 권한이 있는지 확인한다.

## 확인 과제

1. `test`와 `build-and-push` Job을 분리한 이유를 적는다.
2. 첫 push에서 deploy Job이 Skipped가 되는 이유를 적는다.
3. OIDC가 장기 Access Key보다 안전한 이유를 적는다.

<details>
<summary>정답 예시</summary>

1. 테스트가 실패한 코드가 AWS 인증과 이미지 push 단계로 넘어가지 않게 하기 위해서이다.
2. 아직 `EC2_INSTANCE_ID` 변수가 없어서 자동 배포 조건을 충족하지 않기 때문이다.
3. 장기 AWS 키를 저장하지 않고 저장소와 브랜치가 확인된 Workflow에 짧은 수명의 임시 권한만 제공하기 때문이다.

</details>
