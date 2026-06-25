# S3와 EC2 IAM Role

## 학습 목표

- 객체 저장소와 파일 시스템의 차이를 설명할 수 있다.
- S3 버킷과 객체의 관계를 설명할 수 있다.
- EC2에 IAM Role을 연결해 장기 Access Key 없이 AWS API를 호출할 수 있다.
- AWS CLI와 boto3로 S3 객체를 업로드하고 내려받을 수 있다.

## 1. S3가 필요한 이유

EC2 디스크에 업로드 파일을 저장하면 인스턴스를 교체하거나 여러 대로 확장할 때 파일 관리가 어려워진다. S3는 애플리케이션 서버와 데이터를 분리해 객체 단위로 저장한다.

| 구분 | EC2/EBS 파일 시스템 | S3 객체 저장소 |
| --- | --- | --- |
| 접근 방법 | 파일 경로 | 버킷, 키, API |
| 디렉터리 | 실제 디렉터리 구조 | 키 이름의 접두사처럼 표현 |
| 서버 교체 | 볼륨 연결을 관리해야 한다. | 새 서버도 같은 버킷에 접근한다. |
| 대표 용도 | 운영체제, 실행 파일 | 업로드 파일, 백업, 정적 자산 |

S3의 객체는 파일 데이터, 객체 키, 메타데이터로 구성된다. `images/profile.png`는 디렉터리가 아니라 슬래시가 포함된 하나의 키 이름이다.

```text
버킷: 객체를 담는 최상위 공간
객체: 저장한 데이터 한 개
키: 버킷 안에서 객체를 식별하는 이름
메타데이터: 콘텐츠 유형, 크기처럼 객체를 설명하는 정보
```

파일 시스템의 `C:\images\profile.png`나 `/home/user/profile.png`는 운영체제가 해석하는 경로이다. S3의 `images/profile.png`는 API 요청에 전달하는 객체 키이다. S3 객체는 `open()`으로 직접 여는 대신 AWS API로 업로드하고 내려받는다.

## 2. 버킷 이름 정하기

S3 버킷 이름은 모든 AWS 계정에 걸쳐 전역으로 고유해야 한다. 다음 규칙으로 자신의 값을 만든다.

```text
cloud-class-<AWS_ACCOUNT_ID>-<영문이름>
```

예시는 다음과 같다.

```text
cloud-class-123456789012-gildong
```

문서의 `<BUCKET_NAME>`을 실제 버킷 이름으로 바꿔 사용한다.

## 3. S3 버킷 만들기

1. AWS 콘솔에서 `S3`를 연다.
2. `Create bucket`을 선택한다.
3. 버킷 이름을 입력한다.
4. 리전은 서울 `ap-northeast-2`를 선택한다.
5. `Block all public access`를 활성화한 상태로 유지한다.
6. 버킷 버전 관리는 이번 실습에서 비활성화한다.
7. 기본 암호화 설정을 유지한다.
8. 태그 `Project=cloud-class`를 추가한다.
9. 버킷을 생성한다.

웹에서 파일을 보여 준다는 이유로 버킷 전체를 공개하지 않는다. 애플리케이션은 IAM 권한이나 제한된 시간의 미리 서명된 URL로 객체에 접근할 수 있다.

## 4. EC2용 IAM Role 만들기

EC2에서 S3 API를 호출하려면 AWS가 "이 요청을 누가 보냈는가"를 확인할 수 있어야 한다. Access Key를 서버 파일에 저장하는 대신 EC2에 IAM Role을 연결하면 AWS가 짧은 수명의 임시 자격 증명을 자동으로 제공한다.

```text
EC2 인스턴스
  -> 연결된 IAM Role 확인
  -> 임시 자격 증명 발급
  -> IAM 정책 범위 안에서 S3 API 호출
```

역할은 신뢰 정책과 권한 정책을 함께 가진다. 신뢰 정책은 EC2가 이 역할을 맡을 수 있는지 정하고, 권한 정책은 역할을 맡은 EC2가 S3에서 어떤 작업을 할 수 있는지 정한다.

1. AWS 콘솔에서 `IAM`을 연다.
2. `Roles`에서 `Create role`을 선택한다.
3. 신뢰할 엔터티 유형으로 `AWS service`를 선택한다.
4. 사용 사례로 `EC2`를 선택한다.
5. 정책 선택 단계는 건너뛸 수 있다.
6. 역할 이름에 `cloud-class-ec2-role`을 입력한다.
7. 태그 `Project=cloud-class`를 추가한다.
8. 역할을 생성한다.

역할 상세 화면에서 `Permissions`의 인라인 정책 생성을 선택하고 JSON 편집기에 다음 정책을 입력한다. 두 위치의 `<BUCKET_NAME>`을 실제 버킷 이름으로 바꾼다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListClassBucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::<BUCKET_NAME>"
    },
    {
      "Sid": "ManageClassBucketObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::<BUCKET_NAME>/*"
    }
  ]
}
```

정책 이름은 `cloud-class-s3-policy`로 지정한다.

## 5. IAM Role을 EC2에 연결하기

1. EC2 콘솔에서 `cloud-class-ec2`를 선택한다.
2. `Actions`에서 보안 또는 IAM 역할 수정 메뉴를 연다.
3. IAM 인스턴스 프로파일로 `cloud-class-ec2-role`을 선택한다.
4. 변경 내용을 저장한다.

EC2를 재부팅할 필요는 없다. 역할이 연결되면 인스턴스 메타데이터를 통해 임시 자격 증명을 받을 수 있다.

## 6. AWS CLI v2 설치

EC2에 SSH 접속하고 다음을 실행한다.

AWS CLI는 터미널에서 AWS API를 호출하는 프로그램이다. 브라우저 콘솔에서 버튼으로 하던 작업을 명령으로 실행할 수 있어 결과를 재현하고 자동화하기 쉽다. 설치 후 `aws 서비스 작업` 형태로 사용한다.

```text
aws s3 cp ...
    |  |  |
    |  |  +-- 작업에 필요한 인자
    |  +----- 실행할 작업
    +-------- AWS 서비스
```

```bash
# AWS CLI 설치 파일을 내려받는 데 필요한 패키지를 설치한다.
sudo apt update
sudo apt install -y curl unzip

# x86_64 Linux용 AWS CLI v2 설치 압축 파일을 내려받는다.
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip

# 설치 파일을 임시 디렉터리에 압축 해제한다.
unzip -q /tmp/awscliv2.zip -d /tmp

# AWS CLI v2를 시스템 경로에 설치한다.
sudo /tmp/aws/install

# 설치된 AWS CLI 버전을 확인한다.
aws --version
```

`aws configure`를 실행하거나 Access Key를 입력하지 않는다. EC2 IAM Role이 자격 증명을 제공한다.

## 7. 현재 역할 확인

```bash
# EC2가 사용 중인 AWS 계정과 IAM Role 주체를 확인한다.
aws sts get-caller-identity

# 기본 리전을 현재 셸 변수로 지정한다.
export AWS_REGION=ap-northeast-2

# 실습 버킷 이름을 현재 셸 변수로 지정한다.
export BUCKET_NAME=<BUCKET_NAME>
```

`Arn`에 `cloud-class-ec2-role`과 관련된 이름이 보이면 역할 인증이 정상이다.

## 8. AWS CLI로 객체 다루기

```bash
# 업로드할 간단한 텍스트 파일을 만든다.
echo "hello from cloud class" > ~/s3-test.txt

# 로컬 파일을 S3 버킷의 uploads/s3-test.txt 키로 업로드한다.
aws s3 cp ~/s3-test.txt "s3://$BUCKET_NAME/uploads/s3-test.txt"

# 버킷의 모든 객체 키와 크기를 재귀적으로 확인한다.
aws s3 ls "s3://$BUCKET_NAME" --recursive

# S3 객체를 다른 로컬 파일 이름으로 내려받는다.
aws s3 cp "s3://$BUCKET_NAME/uploads/s3-test.txt" ~/s3-downloaded.txt

# 내려받은 파일 내용을 확인한다.
cat ~/s3-downloaded.txt
```

S3 콘솔에서도 `uploads/s3-test.txt` 객체가 보이는지 확인한다.

## 9. 객체 메타데이터 확인

```bash
# 지정한 객체의 크기, 수정 시각, 콘텐츠 유형 같은 메타데이터를 확인한다.
aws s3api head-object \
  --bucket "$BUCKET_NAME" \
  --key uploads/s3-test.txt
```

ETag는 객체의 식별값이다. 경우에 따라 MD5 체크섬과 같을 수 있지만,
멀티파트 업로드나 암호화 방식에 따라 MD5와 달라질 수 있으므로
항상 파일 검증용 MD5라고 가정하지 않는다.

## 10. boto3로 S3 사용하기

Django가 사용하는 Conda 환경에 AWS SDK를 설치한다.

SDK는 애플리케이션 코드에서 AWS API를 호출하도록 돕는 라이브러리이다. `boto3`는 Python용 AWS SDK이며, CLI와 같은 자격 증명 체계를 사용한다. EC2 IAM Role이 연결되어 있으면 Python 코드에도 Access Key를 직접 적지 않는다.

```bash
# Django 프로젝트의 Conda 환경을 활성화한다.
conda activate cloud-class

# Python용 AWS SDK boto3를 설치한다.
pip install boto3

# 변경된 패키지 버전을 requirements.txt에 다시 기록한다.
cd ~/cloud-class-app
pip freeze > requirements.txt
```

`~/cloud-class-app/s3_example.py`를 만든다.

```python
import os

import boto3


# 환경 변수에서 수업 버킷 이름을 읽는다.
bucket_name = os.environ["BUCKET_NAME"]

# EC2 IAM Role의 임시 자격 증명을 자동으로 사용하는 S3 클라이언트이다.
s3 = boto3.client("s3", region_name="ap-northeast-2")

# 메모리의 문자열 데이터를 S3 객체로 업로드한다.
s3.put_object(
    Bucket=bucket_name,
    Key="python/hello.txt",
    Body="uploaded with boto3".encode("utf-8"),
    ContentType="text/plain; charset=utf-8",
)

# 업로드한 객체를 내려받아 본문을 출력한다.
response = s3.get_object(Bucket=bucket_name, Key="python/hello.txt")
print(response["Body"].read().decode("utf-8"))
```

```bash
# Python 예제가 읽을 버킷 이름을 환경 변수로 지정한다.
export BUCKET_NAME=<BUCKET_NAME>

# boto3로 객체를 업로드하고 다시 읽는 예제를 실행한다.
python ~/cloud-class-app/s3_example.py
```

## 11. 미리 서명된 URL 이해하기

비공개 객체를 일정 시간만 내려받게 하려면 미리 서명된 URL을 사용할 수 있다.

```bash
# 지정한 S3 객체에 5분 동안 접근할 수 있는 서명 URL을 만든다.
aws s3 presign "s3://$BUCKET_NAME/uploads/s3-test.txt" --expires-in 300
```

출력 URL에는 임시 서명이 포함되어 있으므로 공개 채널에 공유하지 않는다. 5분이 지나면 같은 URL은 사용할 수 없다.

## 12. 문제 해결

### `Unable to locate credentials`가 나온다

- EC2에 `cloud-class-ec2-role`이 연결되어 있는지 확인한다.
- `aws sts get-caller-identity`를 실행한다.
- EC2 인스턴스 메타데이터 설정이 비활성화되어 있지 않은지 확인한다.

### `AccessDenied`가 나온다

- 정책의 버킷 이름과 실제 버킷 이름을 비교한다.
- 버킷 ARN과 객체 ARN 끝의 `/*`를 구분한다.
- 요청한 작업이 정책의 `Action`에 포함되어 있는지 확인한다.

### 버킷 이름이 이미 사용 중이다

AWS 계정 ID와 영문 이름 뒤에 짧은 숫자를 추가해 전역에서 고유한 이름을 만든다.

## 확인 과제

1. EC2에 Access Key 파일을 저장하지 않아도 S3를 사용할 수 있는 이유를 적는다.
2. 버킷 ARN과 객체 ARN의 차이를 정책 예시에서 찾는다.
3. 60초 동안만 유효한 미리 서명된 URL을 생성한다.

<details>
<summary>정답 예시</summary>

1. EC2에 연결한 IAM Role이 인스턴스 메타데이터를 통해 자동으로 갱신되는 임시 자격 증명을 제공하기 때문이다.
2. 버킷 ARN은 `arn:aws:s3:::버킷이름`이고 객체 ARN은 `arn:aws:s3:::버킷이름/*`이다.
3. `aws s3 presign "s3://$BUCKET_NAME/uploads/s3-test.txt" --expires-in 60`을 실행한다.

</details>
