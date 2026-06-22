# 10. 아카이브와 압축

## 학습 목표

- 아카이브와 압축의 차이를 이해한다.
- `tar`로 여러 파일을 하나로 묶고 풀 수 있다.
- `gzip`, `xz`, `zip` 형식을 구분한다.
- 체크섬으로 파일 무결성을 확인한다.

## 아카이브와 압축

아카이브는 여러 파일을 하나의 파일로 묶는 것이다. 압축은 파일 크기를 줄이는 것이다. `tar`는 원래 아카이브 도구이고, `gzip`이나 `xz`와 함께 쓰면 묶으면서 압축할 수 있다.

| 확장자 | 의미 |
| --- | --- |
| `.tar` | tar 아카이브 |
| `.tar.gz`, `.tgz` | tar + gzip 압축 |
| `.tar.xz` | tar + xz 압축 |
| `.zip` | ZIP 압축 아카이브 |

## 실습 준비

```bash
# 아카이브 실습용 디렉터리 구조를 만든다
mkdir -p ~/linux-class/archive-lab/project/docs

# 아카이브 실습 디렉터리로 이동한다
cd ~/linux-class/archive-lab

# README.txt 예제 파일을 만든다
printf "hello\n" > project/README.txt

# manual.txt 예제 파일을 만든다
printf "manual\n" > project/docs/manual.txt

# project 아래 일반 파일을 확인한다
find project -type f
```

## tar로 묶기

```bash
# project 디렉터리를 project.tar로 묶는다
tar -cvf project.tar project

# 생성된 tar 파일 크기를 확인한다
ls -lh project.tar

# tar 파일 안의 목록을 확인한다
tar -tvf project.tar
```

옵션 의미는 다음과 같다.

| 옵션 | 의미 |
| --- | --- |
| `c` | create, 새 아카이브 생성 |
| `v` | verbose, 처리 파일 출력 |
| `f` | file, 아카이브 파일 이름 지정 |
| `t` | list, 내용 목록 보기 |
| `x` | extract, 풀기 |

## tar 풀기

```bash
# 압축을 풀 디렉터리를 만든다
mkdir extracted

# project.tar를 extracted 디렉터리에 푼다
tar -xvf project.tar -C extracted

# 풀린 파일 목록을 확인한다
find extracted -type f
```

## gzip 압축 tar

```bash
# project 디렉터리를 gzip 방식으로 압축한 tar 파일로 만든다
tar -czvf project.tar.gz project

# 생성된 압축 파일 크기를 확인한다
ls -lh project.tar.gz

# gzip 압축 tar 파일 안의 목록을 확인한다
tar -tzvf project.tar.gz
```

풀기:

```bash
# gzip 압축 tar 파일을 풀 디렉터리를 만든다
mkdir extracted-gz

# project.tar.gz를 extracted-gz 디렉터리에 푼다
tar -xzvf project.tar.gz -C extracted-gz
```

`z` 옵션은 gzip을 의미한다.

## xz 압축 tar

```bash
# project 디렉터리를 xz 방식으로 압축한 tar 파일로 만든다
tar -cJvf project.tar.xz project

# 생성된 압축 파일 크기를 확인한다
ls -lh project.tar.xz
```

`J` 옵션은 xz를 의미한다. xz는 압축률이 좋은 대신 시간이 더 걸릴 수 있다.

## gzip 단독 사용

```bash
# README.txt를 실습용 파일로 복사한다
cp project/README.txt README-copy.txt

# README-copy.txt를 gzip으로 압축한다
gzip README-copy.txt

# 압축된 파일 크기를 확인한다
ls -lh README-copy.txt.gz

# gzip 파일을 다시 푼다
gunzip README-copy.txt.gz

# 복원된 파일 내용을 확인한다
cat README-copy.txt
```

`gzip`은 기본적으로 원본 파일을 `.gz` 파일로 바꾼다.

## zip 사용

`zip`과 `unzip`이 없다면 설치한다.

```bash
# zip과 unzip 패키지를 설치한다
sudo apt install zip unzip
```

압축하고 푼다.

```bash
# project 디렉터리를 zip 파일로 압축한다
zip -r project.zip project

# zip 파일 안의 목록을 확인한다
unzip -l project.zip

# zip 파일을 풀 디렉터리를 만든다
mkdir extracted-zip

# project.zip을 extracted-zip 디렉터리에 푼다
unzip project.zip -d extracted-zip
```

## 체크섬 확인

파일이 변하지 않았는지 확인할 때 체크섬을 쓴다.

```bash
# 압축 파일의 SHA-256 체크섬을 출력한다
sha256sum project.tar.gz

# SHA-256 체크섬을 파일로 저장한다
sha256sum project.tar.gz > project.tar.gz.sha256

# 저장된 체크섬으로 파일 무결성을 검증한다
sha256sum -c project.tar.gz.sha256
```

## 확인 과제

1. `project` 디렉터리를 `backup.tar`로 묶는다.
2. `backup.tar` 안의 파일 목록을 출력한다.
3. `backup.tar.gz`를 만들고 크기를 비교한다.
4. `backup.tar.gz`를 새 디렉터리에 푼다.
5. 압축 파일의 SHA-256 체크섬을 저장하고 검증한다.

<details>
<summary>정답 예시</summary>

```bash
# 아카이브 실습 디렉터리로 이동한다
cd ~/linux-class/archive-lab
```

`project` 디렉터리를 `backup.tar`로 묶는다.

```bash
# project 디렉터리를 backup.tar로 묶는다
tar -cvf backup.tar project
```

아카이브 안의 파일 목록을 출력한다.

```bash
# backup.tar 안의 파일 목록을 출력한다
tar -tvf backup.tar
```

gzip 압축 파일을 만들고 크기를 비교한다.

```bash
# project 디렉터리를 gzip 압축 tar 파일로 만든다
tar -czvf backup.tar.gz project

# 압축 전후 파일 크기를 비교한다
ls -lh backup.tar backup.tar.gz
```

새 디렉터리에 압축을 푼다.

```bash
# 압축을 풀 디렉터리를 만든다
mkdir -p answer-extracted

# backup.tar.gz를 answer-extracted 디렉터리에 푼다
tar -xzvf backup.tar.gz -C answer-extracted

# 풀린 파일 목록을 확인한다
find answer-extracted -type f
```

SHA-256 체크섬을 저장하고 검증한다.

```bash
# backup.tar.gz의 체크섬을 저장한다
sha256sum backup.tar.gz > backup.tar.gz.sha256

# 저장된 체크섬으로 파일을 검증한다
sha256sum -c backup.tar.gz.sha256
```

`backup.tar.gz: OK`가 출력되면 정상이다.

</details>
