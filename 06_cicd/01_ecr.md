# Amazon ECR과 이미지 배포

## 학습 목표

- 컨테이너 레지스트리가 필요한 이유를 설명할 수 있다.
- ECR 저장소, 이미지, 태그와 다이제스트를 구분할 수 있다.
- ECR 저장소를 만들고 EC2에 이미지 pull 권한을 부여할 수 있다.
- 로컬 이미지가 GitHub Actions를 거쳐 EC2에 배포되는 경로를 설명할 수 있다.

## 1. 로컬 이미지의 한계

`cloud-class-app:local` 이미지는 현재 PC의 Docker Engine에만 저장되어 있다. EC2와 GitHub Actions는 이 이미지를 직접 볼 수 없다. 다른 컴퓨터가 같은 이미지를 사용하려면 공통 저장소인 컨테이너 레지스트리가 필요하다.

```text
로컬 소스 코드
  -> GitHub Actions가 이미지 빌드
  -> ECR에 이미지 push
  -> EC2가 ECR에서 이미지 pull
  -> Compose로 컨테이너 실행
```

Amazon ECR은 AWS의 관리형 컨테이너 레지스트리이다. IAM으로 push와 pull 권한을 나눌 수 있고 저장된 이미지의 취약점 검사 결과도 확인할 수 있다.

## 2. ECR 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Registry | AWS 계정과 리전에 속한 이미지 저장 영역이다. |
| Repository | 같은 애플리케이션의 이미지들을 모아 두는 저장소이다. |
| Image | 애플리케이션 코드와 실행 환경을 담은 배포 단위이다. |
| Tag | `latest`, Git 커밋 SHA처럼 이미지에 붙이는 읽기 쉬운 이름이다. |
| Digest | 이미지 내용으로 계산한 변경되지 않는 식별값이다. |

태그는 같은 이름이 다른 이미지를 가리키도록 바뀔 수 있지만 다이제스트는 이미지 내용이 같을 때만 같다. 운영 배포와 롤백에서는 `latest`만 사용하기보다 Git 커밋 SHA 태그를 함께 남긴다.

```text
123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/cloud-class-app:a1b2c3d
|________________________________________________________| |________|
                      저장소 URI                             이미지 태그
```

## 3. ECR 저장소 만들기

1. AWS 콘솔에서 `Elastic Container Registry`를 연다.
2. `Repositories`에서 `Create repository`를 선택한다.
3. 저장소 유형은 Private을 선택한다.
4. 저장소 이름에 `cloud-class-app`을 입력한다.
5. 태그 변경 가능성은 Mutable을 선택한다.
6. 이미지 스캔 설정을 활성화한다.
7. 암호화 기본값을 유지한다.
8. 태그 `Project=cloud-class`를 추가한다.
9. 저장소를 생성한다.

저장소 URI를 기록한다.

```text
<AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/cloud-class-app
```

## 4. push와 pull 권한 분리

이미지를 만드는 주체와 실행하는 주체는 다르다.

| 주체 | 필요한 권한 |
| --- | --- |
| GitHub Actions | 테스트를 통과한 이미지를 ECR에 push한다. |
| EC2 | ECR 이미지를 pull해 실행한다. |
| 로컬 개발 PC | 코드를 작성하고 테스트하지만 ECR 장기 자격 증명을 저장하지 않는다. |

GitHub Actions의 push 권한은 다음 단계에서 OIDC 역할에 부여한다. EC2에는 pull 권한만 부여한다.

## 5. EC2 역할에 ECR pull 권한 추가

IAM의 `cloud-class-ec2-role`에 인라인 정책을 추가한다. `<AWS_ACCOUNT_ID>`를 실제 계정 ID로 바꾼다. 정책 이름은 `cloud-class-ecr-pull-policy`로 지정한다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GetEcrLoginToken",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "PullCloudClassImage",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchCheckLayerAvailability",
        "ecr:DescribeImages"
      ],
      "Resource": "arn:aws:ecr:ap-northeast-2:<AWS_ACCOUNT_ID>:repository/cloud-class-app"
    }
  ]
}
```

`ecr:GetAuthorizationToken`은 ECR 로그인용 임시 토큰을 받는 권한이고, 나머지 작업은 특정 저장소의 이미지 계층과 메타데이터를 내려받는 권한이다.

## 6. 로컬 이미지와 배포 대상 확인

VS Code에서 `cloud-class-app` 폴더를 열고 CMD 터미널에서 실행한다.

```bat
REM 현재 터미널이 프로젝트 루트에 있는지 확인한다.
cd

REM 앞에서 만든 로컬 Django 이미지를 확인한다.
docker image ls cloud-class-app

REM 로컬 이미지의 운영체제와 CPU 아키텍처를 확인한다.
docker image inspect cloud-class-app:local ^
  --format "OS={{.Os}} Architecture={{.Architecture}}"

REM 현재 Git 커밋의 짧은 SHA를 확인한다.
git rev-parse --short HEAD
```

로컬 PC와 EC2의 CPU 아키텍처가 다를 수 있다. 로컬 이미지를 직접 EC2에 복사하지 않고 GitHub Actions의 AMD64 Linux Runner에서 소스를 다시 빌드한다. 빌드 결과와 소스 버전은 Git 커밋 SHA 태그로 연결한다.

## 7. 이미지 태그 전략

GitHub Actions는 한 번의 빌드 결과에 두 태그를 붙인다.

```text
cloud-class-app:<전체 Git 커밋 SHA>
cloud-class-app:latest
```

- 커밋 SHA 태그는 어떤 소스에서 만든 이미지인지 추적하고 이전 버전으로 롤백할 때 사용한다.
- `latest`는 가장 최근에 성공한 main 브랜치 이미지를 가리키는 편의용 태그이다.
- 테스트에 실패한 커밋은 이미지를 만들거나 ECR에 올리지 않는다.

## 8. 이미지 스캔의 의미

ECR 이미지 스캔은 운영체제 패키지와 일부 애플리케이션 패키지에서 알려진 취약점을 찾는다. 스캔 결과가 없다고 이미지가 완전히 안전하다는 뜻은 아니다.

다음 항목은 별도로 확인해야 한다.

- 이미지에 비밀번호와 개인키가 포함되지 않았는가
- 컨테이너가 root가 아닌 사용자로 실행되는가
- 불필요한 패키지가 설치되지 않았는가
- 애플리케이션 테스트가 통과했는가
- 사용한 기본 이미지와 패키지 버전을 추적할 수 있는가

## 9. 다음 단계에서 확인할 결과

현재 ECR 저장소는 비어 있다. 다음 단계에서 GitHub Actions Workflow를 실행한 뒤 ECR 콘솔에서 다음 항목을 확인한다.

1. `latest` 태그가 생겼는가
2. Git 커밋 SHA 태그가 생겼는가
3. 두 태그의 이미지 다이제스트가 같은가
4. 이미지 아키텍처가 EC2에서 실행 가능한 AMD64인가
5. 이미지 스캔이 완료되었는가

## 확인 과제

1. 로컬 Docker 이미지가 EC2에서 바로 보이지 않는 이유를 적는다.
2. GitHub Actions와 EC2에 서로 다른 ECR 권한을 부여하는 이유를 적는다.
3. `latest` 외에 커밋 SHA 태그를 함께 만드는 이유를 적는다.

<details>
<summary>정답 예시</summary>

1. 이미지는 현재 로컬 Docker Engine의 저장소에만 존재하며 EC2와 공유되지 않기 때문이다.
2. GitHub Actions는 이미지를 올려야 하므로 push 권한이 필요하지만 EC2는 검증된 이미지를 내려받기만 하면 되기 때문이다.
3. 배포된 이미지와 소스 커밋을 연결하고 이전 버전으로 정확히 롤백하기 위해서이다.

</details>
