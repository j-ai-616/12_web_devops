# 07. 표준 입출력과 텍스트 처리

## 학습 목표

- 표준 입력, 표준 출력, 표준 오류를 구분한다.
- 리디렉션과 파이프를 사용해 명령어를 조합한다.
- 텍스트 처리 명령어로 필요한 데이터만 추출한다.
- 작은 명령어를 이어 붙여 자동화의 기본 감각을 익힌다.

## 표준 스트림

리눅스 프로그램은 기본적으로 세 가지 통로를 사용한다.

| 이름 | 번호 | 의미 |
| --- | --- | --- |
| 표준 입력 | `0` | 키보드나 이전 명령의 입력 |
| 표준 출력 | `1` | 정상 결과 출력 |
| 표준 오류 | `2` | 오류 메시지 출력 |

## 실습 준비

```bash
# 텍스트 처리 실습 디렉터리를 만든다
mkdir -p ~/linux-class/text-lab

# 텍스트 처리 실습 디렉터리로 이동한다
cd ~/linux-class/text-lab

# CSV 예제 파일을 만든다
printf "name,team,score\nkim,red,90\nlee,blue,75\npark,red,88\nchoi,blue,91\n" > scores.csv

# 중복 단어가 있는 예제 파일을 만든다
printf "apple\nbanana\napple\ncarrot\nbanana\n" > words.txt
```

## 출력 리디렉션

`>`는 파일을 새로 쓰고, `>>`는 파일 뒤에 추가한다.

```bash
# out.txt를 새로 만들고 hello를 저장한다
echo "hello" > out.txt

# out.txt 내용을 확인한다
cat out.txt

# out.txt 뒤에 linux를 추가한다
echo "linux" >> out.txt

# 추가된 내용을 확인한다
cat out.txt
```

기존 파일을 덮어쓸 수 있으므로 `>` 사용 전 파일명을 확인한다.

## 오류 리디렉션

없는 파일을 읽으면 오류가 표준 오류로 출력된다.

```bash
# 없는 파일을 읽어 오류 메시지를 발생시킨다
cat missing.txt

# 오류 메시지를 error.log 파일로 저장한다
cat missing.txt 2> error.log

# 저장된 오류 메시지를 확인한다
cat error.log
```

정상 출력과 오류를 분리한다.

```bash
# 정상 출력은 ok.log로, 오류 출력은 fail.log로 분리한다
ls scores.csv missing.txt > ok.log 2> fail.log

# 정상 출력 내용을 확인한다
cat ok.log

# 오류 출력 내용을 확인한다
cat fail.log
```

## 파이프

파이프 `|`는 앞 명령의 표준 출력을 뒤 명령의 표준 입력으로 보낸다.

```bash
# scores.csv의 전체 줄 수를 센다
cat scores.csv | wc -l

# red가 포함된 줄만 출력한다
cat scores.csv | grep red

# red가 포함된 줄 수를 센다
cat scores.csv | grep red | wc -l
```

`cat 파일 | 명령` 형태는 이해하기 쉽지만, 많은 명령은 파일을 직접 받을 수 있다.

```bash
# 파일을 직접 넘겨 red가 포함된 줄을 검색한다
grep red scores.csv
```

## tee

`tee`는 화면에 출력하면서 동시에 파일에도 저장한다.

```bash
# blue 팀 줄을 화면에 출력하면서 blue-team.txt에도 저장한다
grep blue scores.csv | tee blue-team.txt

# 저장된 파일 내용을 확인한다
cat blue-team.txt
```

## 정렬과 중복 제거

```bash
# 단어를 알파벳순으로 정렬한다
sort words.txt

# 정렬 후 중복된 단어를 제거한다
sort words.txt | uniq

# 정렬 후 단어별 등장 횟수를 센다
sort words.txt | uniq -c
```

`uniq`는 인접한 중복만 처리하므로 보통 `sort`와 함께 쓴다.

## cut과 tr

CSV에서 특정 열만 추출한다.

```bash
# 쉼표를 기준으로 첫 번째 열만 출력한다
cut -d',' -f1 scores.csv

# 쉼표를 기준으로 두 번째와 세 번째 열을 출력한다
cut -d',' -f2,3 scores.csv
```

문자를 바꾼다.

```bash
# 소문자를 대문자로 변환한다
echo "hello linux" | tr 'a-z' 'A-Z'

# 콜론을 줄바꿈으로 변환한다
echo "a:b:c" | tr ':' '\n'
```

## sed

`sed`는 줄 단위 텍스트를 바꾸거나 골라낸다.

```bash
# 각 줄에서 첫 번째 red를 RED로 바꿔 출력한다
sed 's/red/RED/' scores.csv

# 1번 줄부터 3번 줄까지만 출력한다
sed -n '1,3p' scores.csv

# blue가 포함된 줄을 제외하고 출력한다
sed '/blue/d' scores.csv
```

원본 파일을 바로 바꾸기 전에는 먼저 화면 출력으로 결과를 확인한다.

## awk

`awk`는 열 단위 텍스트 처리에 강하다.

```bash
# 쉼표를 기준으로 1열과 3열을 출력한다
awk -F',' '{print $1, $3}' scores.csv

# 헤더를 제외하고 점수가 90 이상인 행의 이름과 점수를 출력한다
awk -F',' 'NR > 1 && $3 >= 90 {print $1, $3}' scores.csv

# 헤더를 제외하고 점수 평균을 계산한다
awk -F',' 'NR > 1 {sum += $3; count++} END {print sum / count}' scores.csv
```

## 확인 과제

1. `scores.csv`에서 `red` 팀만 골라 `red-team.txt`에 저장한다.
2. `words.txt`에서 단어별 등장 횟수를 출력한다.
3. `scores.csv`에서 이름 열만 추출한다.
4. 점수가 90점 이상인 사람만 출력한다.
5. 없는 파일을 읽는 오류 메시지를 `error.log`에 저장한다.

<details>
<summary>정답 예시</summary>

```bash
# 텍스트 처리 실습 디렉터리로 이동한다
cd ~/linux-class/text-lab
```

`red` 팀만 골라 파일로 저장한다.

```bash
# red 팀 줄만 red-team.txt에 저장한다
grep "red" scores.csv > red-team.txt

# 저장된 파일 내용을 확인한다
cat red-team.txt
```

단어별 등장 횟수를 출력한다.

```bash
# 단어를 정렬한 뒤 중복 개수를 센다
sort words.txt | uniq -c
```

이름 열만 추출한다.

```bash
# CSV의 첫 번째 열만 출력한다
cut -d',' -f1 scores.csv
```

점수가 90점 이상인 사람만 출력한다.

```bash
# 점수가 90 이상인 사람의 이름과 점수를 출력한다
awk -F',' 'NR > 1 && $3 >= 90 {print $1, $3}' scores.csv
```

없는 파일을 읽는 오류 메시지를 저장한다.

```bash
# 없는 파일의 오류 메시지를 error.log에 저장한다
cat missing.txt 2> error.log

# 저장된 오류 메시지를 확인한다
cat error.log
```

</details>
