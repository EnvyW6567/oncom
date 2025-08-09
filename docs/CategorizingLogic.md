# 거래 내역 자동 분류 로직 설계 및 확장 방안

## 현재 분류 로직

### rules.json 구조

```json
{
  "companies": [
    {
      "company_id": "com_1",
      "company_name": "A 커머스",
      "categories": [
        {
          "category_id": "cat_101",
          "category_name": "매출",
          "keywords": [
            "네이버페이",
            "쿠팡"
          ]
        }
      ]
    }
  ]
}
```

### 분류 알고리즘

1. 거래 내역의 `적요(description)` 필드를 소문자로 변환
2. 각 회사의 카테고리를 순차적으로 검사
3. 키워드가 적요에 포함되어 있으면 해당 카테고리로 분류
4. 첫 번째 매칭되는 규칙에서 분류 완료 (early return)
5. 매칭되는 규칙이 없으면 미분류 처리

```python
# accounting-processor/app/entity/transaction.py
def classify(self, rules: dict) -> None:
    # 1. 거래 내역의 `적요(description)` 필드를 소문자로 변환
    description_lower = self.description.lower()

    # 2. 각 회사의 카테고리를 순차적으로 검사
    for company in rules.get('companies', []):
        company_id = company['company_id']

        # 3. 키워드가 적요에 포함되어 있으면 해당 카테고리로 분류
        for category in company.get('categories', []):
            keywords = category.get('keywords', [])

            # 4. 첫 번째 매칭되는 규칙에서 분류 완료 (early return)
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    self.company_id = company_id
                    self.category_id = category['category_id']
                    return

    # 5. 매칭되는 규칙이 없으면 미분류 처리
    self.company_id = None
    self.category_id = None


```

### 현재 알고리즘의 한계점

**기능적 한계**

- 확장 조건 미지원
    - 금액 조건
    - 날짜 조건

**성능적 한계**

- 순차 검색으로 인한 O(n) 복잡도
    - 대용량 파일 분류 시 높은 부하
- 정규표현식 미지원
- 캐싱 메커니즘 부재
    - 중복 데이터에 대한 대응 고려 X

## 확장된 분류 규칙 설계

### 아이디어

- 확장 조건들은 기존의 키워드 매칭 방식과 달리 전혀 다른 로직을 가지게 됨
- 대소 비교의 경우 문자열 매칭 방식이 아닌 타입 변환(정수)과 대소 비교 로직이 필요
- 모든 확장조건에 대해 동적으로 대응하는 것은 불가능할 것으로 보임

그렇다면 확장 조건을 어떻게 유연하게 추가할 수 있는지를 고려해야할 것입니다.

### 확장 rules.json 구조 (예상)

#### conditions

- 분류에 필요한 복수 개의 조건을 가지는 key
- `include_keywords`, `exclude_keywords`, `amount_range` 와 같이 확장된 조건을 value로 가질 수 있음

```json
{
  "version": "1.1",
  "companies": [
    {
      "company_id": "com_1",
      "company_name": "A 커머스",
      "categories": [
        {
          "category_id": "cat_101",
          "category_name": "매출",
          "priority": 1,
          "conditions": {
            "include_keywords": [
              "네이버페이",
              "쿠팡",
              "11번가"
            ],
            "exclude_keywords": [
              "취소",
              "환불",
              "반품",
              "철회"
            ],
            "amount_range": {
              "min_amount": 1000,
              "max_amount": null,
              "field": "amount_in"
            }
          }
        },
        {
          "category_id": "cat_102",
          "category_name": "식비",
          "priority": 2,
          "conditions": {
            "include_keywords": [
              "배달의민족",
              "김밥천국",
              "맘스터치"
            ],
            "exclude_keywords": [
              "취소",
              "환불"
            ],
            "amount_range": {
              "min_amount": 3000,
              "max_amount": 50000,
              "field": "amount_out"
            }
          }
        }
      ]
    }
  ]
}
```

### 인터페이스 정의

#### Filter 클래스

- condition_type 에 따라 세부적인 필터링 구현 클래스를 정의하기 위한 인터페이스

```python
class Filter(ABC):
    """필터 기본 인터페이스"""

    def __init__(self, condition_type: str, config: Dict[str, Any]):
        """
        필터 초기화
        
        Args:
            condition_type: 조건 타입 (예: "include_keywords", "exclude_keywords", "amount_range")
            config: 조건 설정 정보
        """
        self.__condition_type = condition_type
        self.config = config

    @abstractmethod
    def filter(self, transaction: Transaction) -> bool:
        """
        필터 동작 수행
        
        Args:
            transaction: 검사할 거래 내역
            
        Returns:
            bool: 필터를 통과하면 True, 실패하면 False
        """
        pass

```

#### Filter 구현 클래스

- `condition_type` 에 맞는 `filter 메서드`를 구현한 세부 구현 클래스
- `exclude_keywords`, `amount`와 조건에 따라 다른 클래스 구현 가능

```python
class ExcludeKeywordsFilter(Filter):
    """제외 키워드 필터 인터페이스"""

    def __init__(self, keywords: List[str]):
        """
        제외 키워드 필터 초기화
        
        Args:
            keywords: 제외되어야 할 키워드 목록
        """
        super().__init__("exclude_keywords", {"keywords": keywords})

    def filter(self, transaction: Transaction) -> bool:
        """키워드 제외 여부 검사 (구현 필요)"""
        pass


class AmountRangeFilter(Filter):
    """금액 범위 필터 인터페이스"""

    def __init__(self, min_amount: Optional[int] = None,
                 max_amount: Optional[int] = None,
                 field: str = "amount_out"):
        """
        금액 범위 필터 초기화
        
        Args:
            min_amount: 최소 금액
            max_amount: 최대 금액
            field: 검사할 금액 필드 ("amount_in" 또는 "amount_out")
        """
        config = {
            "min_amount": min_amount,
            "max_amount": max_amount,
            "field": field
        }
        super().__init__("amount_range", config)

    def filter(self, transaction: Transaction) -> bool:
        """금액 범위 검사 (구현 필요)"""
        pass
```

#### FilterChain 클래스

- Filter 클래스를 등록하고 순차적인 분류 흐름을 생성하기 위한 클래스
- Filter 의 응답이 하나라도 False면 실패

```python

class FilterChain:
    """필터 체인 - 여러 필터를 순서대로 실행"""

    def __init__(self):
        """필터 체인 초기화"""
        self._filters: List[Filter] = []

    def add_filter(self, filter_obj: Filter) -> 'FilterChain':
        """
        필터를 체인에 추가
        
        Args:
            filter_obj: 추가할 필터 객체
            
        Returns:
            FilterChain: 메서드 체이닝을 위한 self 반환
        """
        pass

    def execute(self, transaction: Transaction) -> bool:
        """
        등록된 순서대로 모든 필터 실행
        
        Args:
            transaction: 검사할 거래 내역
            
        Returns:
            bool: 모든 필터를 통과하면 True, 하나라도 실패하면 False
        """
        pass
```
