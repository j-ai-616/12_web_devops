# 최종 통합과 AWS 자원 정리

## 학습 목표

- 전체 요청과 배포 경로를 설명할 수 있다.
- 서비스별 정상 상태를 증빙할 수 있다.
- 의존 관계를 고려해 AWS 실습 자원을 삭제할 수 있다.
- 삭제 후 남은 비용 발생 자원을 확인할 수 있다.

## 1. 최종 아키텍처

```text
[사용자 브라우저]
        |
        v
[EC2 Nginx]
        |
        v
[Django Docker 컨테이너]
    |        |        |
    v        v        v
  [HTML]   [RDS]    [S3]


[Windows 로컬 Git push]
    -> [GitHub Actions 테스트]
    -> [OIDC IAM Role]
    -> [ECR]
    -> [SSM Run Command]
    -> [EC2 Docker Compose]
```

## 2. 최종 결과 증빙

자원을 삭제하기 전에 다음 결과를 캡처하거나 기록한다. 비밀번호, 토큰, 개인키는 캡처하지 않는다.

| 항목 | 확인 결과 |
| --- | --- |
| 브라우저 `/` 응답 | Cloud Class 메인 화면 |
| 브라우저 `/health/` 응답 | `status=ok` |
| 브라우저 `/api/info/` 응답 | `version=<Git 커밋 SHA>` |
| GitHub Actions | test, build-and-push, deploy 성공 |
| ECR | latest와 커밋 SHA 태그 |
| EC2 | Compose web 컨테이너 healthy |
| RDS | Django 마이그레이션 테이블 |
| S3 | CLI와 boto3 업로드 객체 |

EC2에서 마지막 상태를 확인한다.

```bash
# 데이터베이스 연결 정보를 현재 셸 환경으로 다시 불러온다.
set -a
source /etc/cloud-class.env
set +a

# 삭제 전 확인할 실제 수업 버킷 이름을 지정한다.
export BUCKET_NAME=<BUCKET_NAME>

# Nginx를 거친 메인 화면 응답 헤더를 확인한다.
curl -I http://127.0.0.1/

# Nginx를 거친 상태 확인 API를 호출한다.
curl http://127.0.0.1/health/

# 배포된 실행 환경과 커밋 SHA를 확인한다.
curl http://127.0.0.1/api/info/

# RDS 네트워크 응답을 확인한다.
pg_isready -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME"

# 수업 S3 버킷의 객체 목록을 확인한다.
aws s3 ls "s3://$BUCKET_NAME" --recursive
```

## 3. 삭제 원칙

삭제는 의존하는 쪽에서 의존받는 쪽 순서로 진행한다.

```text
이벤트와 배포 자동화
  -> 애플리케이션 실행 자원
  -> 데이터 자원
  -> 이미지 저장소
  -> 권한과 보안 그룹
  -> 로그와 잔여 자원
```

삭제 전에 자원 이름, 리전, 계정 ID를 다시 확인한다. 다른 프로젝트의 자원을 이름이 비슷하다는 이유로 삭제하지 않는다.

## 4. S3 버킷 비우고 삭제

버킷 이름을 다시 확인한다.

```bash
# 삭제 대상 버킷 이름을 화면에 출력해 확인한다.
printf 'Bucket to remove: %s\n' "$BUCKET_NAME"

# 버킷의 현재 객체 목록을 마지막으로 확인한다.
aws s3 ls "s3://$BUCKET_NAME" --recursive

# 수업 버킷의 모든 객체를 삭제한다.
aws s3 rm "s3://$BUCKET_NAME" --recursive

```

객체를 비운 뒤 S3 콘솔에서 버킷 이름을 다시 확인하고 버킷을 삭제한다. EC2 역할은 객체 관리에 필요한 권한만 가지며 버킷 자체 삭제 권한은 갖지 않는다.

버전 관리를 활성화했다면 현재 객체만 삭제해서는 버킷이 비워지지 않는다. 객체 버전과 삭제 마커를 별도로 제거해야 한다.

## 5. RDS 삭제

1. RDS 콘솔에서 `cloud-class-db`를 선택한다.
2. 삭제를 선택한다.
3. 수업 데이터를 보관할 필요가 없다면 최종 스냅샷을 만들지 않는다.
4. 자동 백업 보존 여부를 확인한다.
5. 삭제 확인 문구를 입력한다.
6. DB 상태가 `Deleting`을 거쳐 목록에서 사라지는지 확인한다.
7. `Snapshots`와 `Automated backups`에 수업 DB의 잔여 항목이 있는지 확인한다.

스냅샷은 DB 인스턴스를 삭제해도 저장 비용이 발생할 수 있다.

## 6. ECR 저장소 삭제

ECR 콘솔에서 저장소 이름 `cloud-class-app`과 이미지 목록을 확인한 뒤 저장소를 삭제한다. EC2 역할은 이미지 pull 권한만 가지므로 저장소 자체 삭제는 콘솔에서 수행한다.

```bash
# 수업 ECR 저장소의 이미지 태그와 digest를 확인한다.
aws ecr describe-images \
  --repository-name cloud-class-app \
  --region ap-northeast-2 \
  --output table
```

1. ECR 콘솔에서 `cloud-class-app`을 선택한다.
2. 저장소 삭제를 선택한다.
3. 내부 이미지까지 삭제된다는 경고를 확인한다.
4. 저장소 이름을 입력해 삭제한다.

## 7. EC2와 연결 자원 삭제

1. EC2 콘솔에서 `cloud-class-ec2`를 선택한다.
2. 인스턴스 ID와 태그를 확인한다.
3. 인스턴스를 종료한다.
4. 상태가 `Terminated`가 되는지 확인한다.
5. `Volumes`에서 연결이 끊긴 수업용 EBS 볼륨이 남았는지 확인한다.
6. `Elastic IP addresses`에서 미연결 주소가 남았는지 확인한다.
7. 키 페어 `cloud-class-key`를 삭제한다.

Windows에 저장한 개인키도 더 이상 사용하지 않으면 삭제한다. 다음 명령은 VS Code의 CMD 터미널에서 실행한다.

```bat
REM Windows Downloads의 수업용 개인키 경로를 확인한다.
dir "%USERPROFILE%\Downloads\cloud-class-key.pem"

REM EC2 종료를 확인한 뒤 Windows에 남은 개인키를 삭제한다.
del "%USERPROFILE%\Downloads\cloud-class-key.pem"
```

개인키를 다른 Windows 폴더로 옮겼다면 실제 저장 경로를 확인한 뒤 해당 파일을 삭제한다. Windows의 SSH 설정 파일에 `cloud-class` Host를 추가했다면 `%USERPROFILE%\.ssh\config`에서도 해당 블록을 제거한다.

## 8. IAM 자원 정리

다음 순서로 정리한다.

1. `cloud-class-github-role`의 인라인 정책을 삭제한다.
2. `cloud-class-github-role`을 삭제한다.
3. `cloud-class-ec2-role`의 인라인·관리형 정책을 분리한다.
4. `cloud-class-ec2-role`과 연결된 인스턴스 프로파일을 삭제한다.
5. `cloud-class-ec2-role`을 삭제한다.
6. 다른 프로젝트가 사용하지 않는 경우에만 GitHub OIDC 공급자를 삭제한다.

OIDC 공급자는 같은 AWS 계정의 다른 GitHub 저장소도 사용할 수 있다. 삭제 전에 역할의 신뢰 정책을 검색한다.

## 9. 보안 그룹 정리

EC2와 RDS가 완전히 삭제된 뒤 다음 보안 그룹을 삭제한다.

- `cloud-class-rds-sg`
- `cloud-class-ec2-sg`

다른 보안 그룹이 참조하거나 네트워크 인터페이스가 사용 중이면 삭제할 수 없다. 오류 메시지의 연결 자원을 먼저 찾는다.

## 10. GitHub 설정 정리

GitHub 저장소의 Actions Variables에서 다음 값을 제거한다.

- `AWS_ROLE_ARN`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `EC2_INSTANCE_ID`

저장소를 학습 결과물로 보관할 수 있지만 Workflow를 다시 실행해도 삭제된 AWS 역할을 맡을 수 없게 된다.

## 11. 최종 잔여 자원 확인

AWS 콘솔에서 리전을 서울로 맞추고 `Project=cloud-class` 태그로 자원을 검색한다. 다음 서비스도 직접 확인한다.

- EC2 인스턴스, 볼륨, Elastic IP, 보안 그룹
- RDS 데이터베이스, 스냅샷, 자동 백업
- S3 버킷
- ECR 저장소
- Lambda 함수
- CloudWatch 로그 그룹
- IAM 역할과 정책
- Systems Manager Run Command 기록

Billing 화면의 Cost Explorer는 반영에 시간이 걸릴 수 있다. Budget 알림은 당분간 유지해 예상하지 않은 비용을 감시한다.

## 12. 최종 회고 질문

1. 수동 배포에서 가장 오류가 나기 쉬웠던 단계는 무엇이었는가?
2. Docker가 해결한 문제와 해결하지 못한 문제는 무엇인가?
3. GitHub Actions가 EC2에 접근할 때 사용한 두 가지 보안 기술은 무엇인가?

<details>
<summary>정답 예시</summary>

1. 환경 변수, 프로세스 실행 경로, Nginx 프록시 설정처럼 여러 계층이 연결되는 단계에서 오류가 자주 발생할 수 있다.
2. Docker는 실행 환경과 배포 단위를 표준화하지만 데이터베이스 운영, 비밀값 관리, 네트워크 보안과 비용 관리를 대신하지 않는다.
3. GitHub OIDC로 임시 AWS 자격 증명을 얻고 SSM으로 SSH 개인키 없이 명령을 전달했다.

</details>
