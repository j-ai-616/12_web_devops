# 디자인 패턴

## 학습 목표

- 디자인 패턴의 목적과 구성 요소를 설명할 수 있다.
- 생성, 구조와 행위 패턴을 구분할 수 있다.
- 대표적인 패턴이 해결하는 문제와 장단점을 설명할 수 있다.
- 문제의 복잡도에 맞게 패턴 적용 여부를 판단할 수 있다.

## 1. 디자인 패턴이란 무엇인가

디자인 패턴은 객체지향 설계에서 반복해서 나타나는 문제와 검증된 해결 방향에 이름을 붙인 것이다. 완성된 코드를 그대로 복사하는 방법이 아니라 객체와 책임을 배치하는 일반적인 설계 지식이다.

패턴 이름은 설계 의도를 전달하는 공통 언어가 된다.

```text
"할인 종류마다 조건문을 추가한다"
보다
"할인 정책을 Strategy로 분리한다"
라고 표현하면 변경 의도와 구조를 함께 전달할 수 있다.
```

패턴은 목표가 아니라 도구이다. 해결할 문제가 분명하지 않은데 패턴부터 적용하면 클래스, 인터페이스와 호출 단계만 늘어날 수 있다.

## 2. 패턴의 기본 요소

패턴을 다음 요소로 설명하면 이름만 외우는 것을 피할 수 있다.

| 요소 | 설명 |
| --- | --- |
| 이름 | 문제와 해결 방향을 부르는 공통 용어 |
| 상황 | 패턴을 고려할 수 있는 환경과 조건 |
| 문제 | 반복해서 발생하는 설계상의 어려움 |
| 해결 | 객체와 책임을 배치하는 일반적인 구조 |
| 결과 | 장점, 단점과 새로 생기는 복잡성 |

패턴 설명에 포함된 클래스 이름보다 각 객체가 담당하는 책임과 의존 방향이 중요하다.

## 3. 패턴의 분류

| 분류 | 핵심 질문 | 대표 패턴 |
| --- | --- | --- |
| 생성 패턴 | 객체를 어떻게 만들 것인가 | Factory Method, Abstract Factory, Builder, Singleton |
| 구조 패턴 | 객체를 어떻게 조합할 것인가 | Adapter, Decorator, Facade, Composite, Proxy |
| 행위 패턴 | 객체가 어떻게 협력할 것인가 | Strategy, Observer, Command, State, Template Method |

하나의 설계에 여러 패턴을 함께 사용할 수 있다. Factory로 Strategy 객체를 만들고 Decorator로 부가 기능을 추가하는 구조도 가능하다.

## 4. 패턴을 적용하기 전 확인할 질문

- 현재 반복되는 설계 문제가 실제로 존재하는가
- 무엇이 자주 바뀌고 무엇이 유지되는가
- 단순한 함수나 조건문으로 충분하지 않은가
- 패턴으로 테스트와 변경이 쉬워지는가
- 새로 생기는 클래스와 간접 호출을 감당할 수 있는가
- 패턴의 의도를 팀이 공통으로 이해할 수 있는가

패턴 적용 여부는 코드의 크기보다 변화의 종류와 빈도를 기준으로 판단한다.

## 5. 생성 패턴

### Factory Method

Factory Method는 구체적인 객체 생성 책임을 사용하는 코드에서 분리한다.

### 문제 상황

실행 환경에 따라 이메일, 문자 또는 메신저 알림 객체를 만들어야 한다. 객체 생성 조건이 여러 곳에 반복되면 새 알림 방식을 추가할 때 여러 파일을 수정해야 한다.

### 구조 예시

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass


class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"email: {message}")


class SmsNotification(Notification):
    def send(self, message: str) -> None:
        print(f"sms: {message}")


def create_notification(kind: str) -> Notification:
    # 생성 조건을 한곳에서 관리한다.
    if kind == "email":
        return EmailNotification()
    if kind == "sms":
        return SmsNotification()
    raise ValueError("지원하지 않는 알림 방식이다")
```

### 장점

- 객체 생성 규칙을 한곳에서 관리할 수 있다.
- 사용하는 코드는 구체적인 클래스 이름을 덜 알게 된다.
- 생성 과정이 복잡할 때 이를 숨길 수 있다.

### 단점

- 생성 규칙이 단순하면 함수나 클래스가 불필요한 간접 단계가 된다.
- 제품 종류가 늘면 Factory 구조도 함께 복잡해질 수 있다.

### Abstract Factory

Abstract Factory는 서로 관련된 객체의 집합을 구체적인 클래스에 의존하지 않고 생성한다.

예를 들어 운영체제별 UI를 만든다고 가정한다.

```text
WindowsUIFactory
  -> WindowsButton
  -> WindowsDialog

MacUIFactory
  -> MacButton
  -> MacDialog
```

같은 제품군의 객체가 서로 호환되어야 할 때 유용하다. 객체 하나만 선택하면 되는 문제에는 Factory Method가 더 단순할 수 있다.

### Builder

Builder는 여러 단계와 선택 옵션을 가진 복잡한 객체의 생성 과정을 분리한다.

```python
class ReportBuilder:
    def __init__(self):
        self._title = ""
        self._sections = []
        self._include_summary = False

    def title(self, value: str):
        self._title = value
        return self

    def add_section(self, value: str):
        self._sections.append(value)
        return self

    def include_summary(self):
        self._include_summary = True
        return self

    def build(self):
        # 수집한 옵션을 최종 보고서 객체로 변환한다.
        return Report(
            title=self._title,
            sections=self._sections,
            include_summary=self._include_summary,
        )
```

생성자 매개변수가 많고 선택 옵션 조합이 다양할 때 읽기 쉬운 생성 코드를 만들 수 있다. 단순한 데이터 객체에는 기본 생성자나 이름 있는 생성 함수가 더 적합할 수 있다.

### Singleton

Singleton은 프로그램 안에서 특정 클래스의 인스턴스가 하나만 존재하도록 제한한다.

설정 관리자나 공유 자원 관리자에 사용되는 경우가 있지만 다음 문제가 있다.

- 전역 상태가 생겨 의존성이 숨겨진다.
- 테스트 사이에 상태가 공유될 수 있다.
- 객체를 대체하기 어렵다.
- 동시성 환경에서 안전한 생성 처리가 필요하다.

언어의 모듈, 애플리케이션 컨테이너와 의존성 주입 도구가 이미 생명주기를 관리한다면 직접 Singleton을 구현할 필요가 적다.

## 6. 구조 패턴

### Adapter

Adapter는 기존 객체의 인터페이스를 현재 코드가 기대하는 형태로 변환한다.

### 문제 상황

내부 코드는 `save(name, data)`를 기대하지만 외부 라이브러리는 `upload_file(path, body)`를 제공한다.

```python
class LegacyStorage:
    def upload_file(self, path: str, body: bytes) -> str:
        return f"uploaded: {path}"


class StorageAdapter:
    def __init__(self, legacy_storage: LegacyStorage):
        self.legacy_storage = legacy_storage

    def save(self, name: str, data: bytes) -> str:
        # 외부 라이브러리의 메서드를 내부 인터페이스로 변환한다.
        return self.legacy_storage.upload_file(name, data)
```

### 장점

- 기존 코드와 외부 라이브러리를 직접 수정하지 않고 연결할 수 있다.
- 인터페이스 차이를 한곳에서 관리할 수 있다.

### 단점

- 변환 계층이 추가된다.
- Adapter 안에 업무 규칙까지 넣으면 책임이 불명확해진다.

### Decorator

Decorator는 원래 객체의 인터페이스를 유지하면서 기능을 감싸 추가한다.

```python
class FileStorage:
    def save(self, name: str, data: bytes) -> str:
        return f"files/{name}"


class LoggingStorage:
    def __init__(self, storage):
        self.storage = storage

    def save(self, name: str, data: bytes) -> str:
        # 실제 저장 전후에 로그 기능을 추가한다.
        print(f"save started: {name}")
        result = self.storage.save(name, data)
        print(f"save completed: {result}")
        return result
```

로그, 캐시, 권한 검사와 재시도 같은 부가 기능을 조합할 때 유용하다. Decorator가 여러 겹이면 실제 실행 순서를 파악하기 어려울 수 있다.

Python의 `@decorator` 문법은 비슷한 목적을 쉽게 구현하도록 돕지만 GoF Decorator 패턴과 항상 같은 구조를 뜻하지는 않는다.

### Facade

Facade는 복잡한 하위 시스템을 사용하기 위한 단순한 인터페이스를 제공한다.

```python
class OrderFacade:
    def __init__(self, inventory, payment, delivery):
        self.inventory = inventory
        self.payment = payment
        self.delivery = delivery

    def place_order(self, order):
        # 여러 하위 시스템의 호출 순서를 하나의 기능으로 제공한다.
        self.inventory.reserve(order.items)
        self.payment.pay(order.total_amount)
        self.delivery.schedule(order)
```

사용하는 쪽이 하위 시스템의 세부 호출 순서를 몰라도 된다는 장점이 있다. Facade가 모든 업무를 담당하는 거대한 클래스가 되지 않도록 책임 범위를 제한해야 한다.

### Composite

Composite는 개별 객체와 객체의 묶음을 같은 방식으로 다룬다.

```text
Folder
  - File
  - File
  - Folder
      - File
```

파일과 폴더, 메뉴와 하위 메뉴, 조직과 하위 조직처럼 트리 구조를 표현할 때 유용하다.

```python
class File:
    def size(self) -> int:
        return 100


class Folder:
    def __init__(self, children):
        self.children = children

    def size(self) -> int:
        # 파일과 하위 폴더를 같은 인터페이스로 계산한다.
        return sum(child.size() for child in self.children)
```

### Proxy

Proxy는 실제 객체를 대신해 접근을 제어한다.

사용 목적은 다음과 같다.

- 실제 객체를 필요한 시점까지 늦게 생성한다.
- 원격 객체 호출을 로컬 객체처럼 감싼다.
- 권한을 검사한다.
- 결과를 캐시한다.

Proxy와 Decorator는 실제 객체를 감싸는 구조가 비슷하다. Proxy는 접근 제어와 대리 역할이 중심이고, Decorator는 기능을 조합해 추가하는 것이 중심이다.

## 7. 행위 패턴

### Strategy

Strategy는 교체 가능한 알고리즘이나 정책을 별도 객체로 분리한다.

### 문제 상황

회원 등급마다 할인 계산 방식이 다르고 새로운 정책이 추가될 수 있다.

```python
from abc import ABC, abstractmethod
from decimal import Decimal


class DiscountStrategy(ABC):
    @abstractmethod
    def discount(self, amount: Decimal) -> Decimal:
        pass


class NoDiscount(DiscountStrategy):
    def discount(self, amount: Decimal) -> Decimal:
        return Decimal("0")


class RateDiscount(DiscountStrategy):
    def __init__(self, rate: Decimal):
        self.rate = rate

    def discount(self, amount: Decimal) -> Decimal:
        return amount * self.rate


class PriceCalculator:
    def __init__(self, strategy: DiscountStrategy):
        # 할인 정책을 외부에서 전달받아 교체할 수 있게 한다.
        self.strategy = strategy

    def final_price(self, amount: Decimal) -> Decimal:
        return amount - self.strategy.discount(amount)
```

### 장점

- 긴 조건문을 독립적인 정책으로 분리할 수 있다.
- 정책을 개별적으로 테스트하고 실행 중 교체할 수 있다.

### 단점

- 정책이 적고 변경되지 않으면 클래스 수만 늘어날 수 있다.
- 사용하는 쪽이 적절한 Strategy를 선택해야 한다.

### Observer

Observer는 한 객체의 상태 변화나 사건을 여러 객체에 알린다.

```text
주문 완료 이벤트
  -> 이메일 알림
  -> 재고 통계 갱신
  -> 포인트 적립
```

발행자는 구독자의 구체적인 동작을 몰라도 되므로 결합도를 낮출 수 있다. 반면 실행 순서가 숨겨지고 한 구독자의 실패를 어떻게 처리할지 결정해야 한다.

이벤트가 중복 전달될 수 있는 환경에서는 같은 이벤트를 여러 번 처리해도 결과가 달라지지 않는 멱등성을 고려한다.

### Command

Command는 실행할 작업을 객체로 표현한다.

```python
class CancelOrderCommand:
    def __init__(self, order_id: int):
        self.order_id = order_id

    def execute(self, service):
        # 명령 객체가 실행에 필요한 데이터를 보관한다.
        return service.cancel(self.order_id)
```

다음 상황에 유용하다.

- 작업을 대기열에 넣는다.
- 실행 이력을 남긴다.
- 실패한 작업을 재시도한다.
- 실행 취소 기능을 제공한다.

단순한 함수 호출에 이력과 재시도가 필요하지 않다면 별도 Command 객체가 과할 수 있다.

### State

State는 객체의 상태에 따라 달라지는 행동을 상태 객체로 분리한다.

```text
주문 상태
  생성 -> 결제 완료 -> 배송 중 -> 완료
             |
             -> 취소
```

상태별 조건문이 여러 메서드에 반복되면 State 패턴을 고려할 수 있다. 상태 전이와 상태별 행동이 각 객체에 모인다는 장점이 있다. 상태가 두세 개이고 규칙이 단순하면 열거형과 조건문이 더 명확할 수 있다.

### Template Method

Template Method는 알고리즘의 전체 순서를 상위 클래스에 정의하고 일부 단계를 하위 클래스가 구현하게 한다.

```python
from abc import ABC, abstractmethod


class DataImporter(ABC):
    def import_data(self, source):
        # 전체 처리 순서는 유지하고 세부 단계만 하위 클래스가 구현한다.
        raw = self.read(source)
        validated = self.validate(raw)
        return self.save(validated)

    @abstractmethod
    def read(self, source):
        pass

    def validate(self, data):
        return data

    @abstractmethod
    def save(self, data):
        pass
```

처리 순서는 같고 일부 단계만 달라질 때 유용하다. 상속 결합이 강해질 수 있으므로 단계 자체를 객체로 교체해야 한다면 Strategy를 검토한다.

## 8. 패턴 비교

### Factory와 Strategy

- Factory는 어떤 객체를 생성할지를 결정한다.
- Strategy는 생성된 객체의 알고리즘이나 정책을 교체한다.

### Adapter와 Facade

- Adapter는 기존 인터페이스를 필요한 인터페이스로 변환한다.
- Facade는 복잡한 여러 인터페이스를 단순한 하나의 인터페이스로 제공한다.

### Decorator와 Proxy

- Decorator는 같은 인터페이스를 유지하며 기능을 추가한다.
- Proxy는 실제 객체에 대한 접근을 통제하거나 대신한다.

### Strategy와 State

- Strategy는 사용하는 쪽이 알고리즘을 선택하는 경우가 많다.
- State는 객체의 내부 상태가 바뀌면서 행동이 함께 바뀐다.

## 9. 패턴 오용

### 문제보다 패턴을 먼저 정한다

패턴을 사용하기 위해 문제를 끼워 맞추면 구조가 복잡해진다. 먼저 변경과 중복의 원인을 설명해야 한다.

### 인터페이스를 무조건 만든다

구현이 하나이고 교체나 독립 테스트의 필요가 없다면 인터페이스가 의미 없는 계층이 될 수 있다.

### 이름만 패턴을 사용한다

클래스 이름에 `Factory`나 `Strategy`를 붙여도 책임과 의존 구조가 맞지 않으면 해당 패턴이라고 보기 어렵다.

### 패턴의 비용을 기록하지 않는다

패턴은 유연성과 함께 클래스 수, 간접 호출과 학습 비용을 늘린다. 선택한 이유와 받아들인 단점을 기록한다.

## 10. 패턴 선택 절차

1. 반복되거나 변경하기 어려운 문제를 한 문장으로 정의한다.
2. 변하는 부분과 유지되는 부분을 구분한다.
3. 단순한 코드로 해결할 수 있는지 먼저 확인한다.
4. 후보 패턴이 책임과 의존성을 어떻게 바꾸는지 그린다.
5. 적용 전후의 테스트 가능성과 변경 범위를 비교한다.
6. 새로 생기는 복잡성이 이점보다 큰지 판단한다.
7. 선택 이유와 적용하지 않은 대안을 기록한다.

## 핵심 정리

- 디자인 패턴은 반복되는 설계 문제와 해결 방향에 붙인 공통 이름이다.
- 생성 패턴은 객체 생성, 구조 패턴은 객체 조합, 행위 패턴은 객체 협력을 다룬다.
- 패턴은 장점과 함께 클래스 수와 간접 호출이라는 비용을 만든다.
- 패턴의 이름보다 상황, 책임, 의존 방향과 결과를 이해해야 한다.
- 단순한 코드가 충분하다면 패턴을 적용하지 않는 선택이 더 좋은 설계일 수 있다.

## 확인 문제

1. Factory와 Strategy의 목적 차이를 설명한다.
2. Adapter와 Facade의 차이를 설명한다.
3. Decorator가 적합한 상황을 한 가지 작성한다.
4. 패턴을 적용하지 않는 편이 나은 상황을 설명한다.

<details>
<summary>정답 예시</summary>

1. Factory는 어떤 구체 객체를 생성할지 결정하는 책임을 분리하고, Strategy는 같은 목적을 수행하는 여러 알고리즘이나 정책을 교체한다.
2. Adapter는 호환되지 않는 기존 인터페이스를 필요한 형태로 변환하고, Facade는 복잡한 여러 하위 인터페이스를 단순한 하나의 진입점으로 제공한다.
3. 저장 기능은 그대로 유지하면서 로그, 캐시 또는 권한 검사 기능을 선택적으로 감싸 추가해야 하는 상황이다.
4. 구현이 하나뿐이고 변경 가능성이 낮으며 단순한 함수나 조건문이 더 쉽게 이해되는 상황이다.

</details>
