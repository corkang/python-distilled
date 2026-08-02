# Python Distilled × `minisearch` 필수 실습 로드맵

> **한 줄 목표:** *Python Distilled* 1~10장을 읽으며 Python의 핵심 문법과 표준 라이브러리를 직접 사용해, 텍스트 문서를 색인하고 검색하는 CLI 도구 `minisearch`를 완성한다.

이 로드맵은 Python 자체를 익히는 데 집중한다. 책에 등장하는 모든 고급 기능을 하나의 제품에 억지로 넣지 않고, 문자열·컨테이너·제어 흐름·함수·객체·제너레이터·모듈·I/O·표준 라이브러리를 반복해서 사용하는 필수 경로만 남겼다.

---

## 문서와 디렉터리의 역할

- [`README.md`](README.md): 저장소의 목적과 전체 학습 방법
- [`Python Distilled.md`](Python%20Distilled.md): 책의 장·절별 독서 진행 상황
- `project.md`: Minisearch의 Task별 구현·검증 계약
- `project/`: Minisearch 제품 코드와 테스트
- `Book/`: 개인 학습용 로컬 자료. 저작권 보호를 위해 Git에 올리지 않는다.

모든 명령은 별도 안내가 없다면 **저장소 루트**에서 실행한다. 현재 학습 환경은 Python 3.13이지만, 구현할 때 사용한 최소 Python 버전은 Task 26의 `requires-python`에 명시한다.

## 최종 결과물

```bash
$ minisearch index ./corpus --output .minisearch-index.json
Indexed 42 documents (8,413 terms)

$ minisearch search "machine learning" --index .minisearch-index.json --limit 2
1. doc_042.txt   score=3.84  ...machine learning is...
2. doc_007.txt   score=2.61  ...

$ minisearch stats --index .minisearch-index.json
documents=42 vocab=8413 avg_length=612.4
```

인덱스 경로를 생략하면 현재 디렉터리의 `.minisearch-index.json`을 사용한다. 점수는 정규화된 확률이 아니라 TF-IDF 합계이므로 1보다 클 수 있다.

---

## Task 학습 사이클

각 Task에서 다음 순서를 반복한다.

1. **읽기** — `읽고 시작`에 적힌 절을 읽는다.
2. **확인·연습** — 책의 예제는 로컬에서 실행하고, 결과를 예상한 뒤 확인한다.
3. **RED** — 검증 계약을 `unittest` 코드로 옮기고 예상한 이유로 실패하는지 확인한다.
4. **GREEN** — 요구사항을 만족하는 최소 코드를 작성한다.
5. **리팩터링** — 중복과 이름을 정리한 뒤 현재 Task와 전체 회귀 테스트를 다시 실행한다.
6. **기록** — 학습한 점과 설계 결정을 짧게 기록하고 Task 완료 상태를 커밋한다.

Git 태그는 사용하지 않는다. Task 시작 전 불필요한 빈 커밋도 만들지 않는다.

```bash
# 이전 작업이 기록되어 있는지 확인
git status --short

# 현재 Task 테스트: RED 확인 후 구현하고 다시 실행
python3 -m unittest discover -s project/tests \
  -p 'test_task_03.py' -v

# 현재까지의 전체 회귀 테스트
python3 -m unittest discover -s project/tests \
  -p 'test_task_*.py' -v

# 완료 상태 기록
git add project project.md
git commit -m "Complete Task 03: separate text processing functions"
```

커밋은 실행 가능한 체크포인트를 남기기 위한 것이다. 같은 기능의 옛 코드를 주석 처리하거나 `minisearch_v2.py`, `minisearch_final.py` 같은 사본으로 남기지 않는다. 이전 버전은 Git 기록에서 확인한다.

```bash
git log --oneline -- project
git show HEAD~1:project/minisearch.py
git diff HEAD~1..HEAD -- project
```

---

## 테스트 작성·실행 방법

### 기본 구조

Task 1에서 다음 구조로 시작한다.

```text
project/
├── minisearch.py
├── sample.txt
└── tests/
    └── test_task_01.py
```

현재처럼 `project/tests`를 탐색 시작 디렉터리로 직접 지정하고 테스트 파일을 한 단계에만 두는 동안에는 `tests/__init__.py`가 필요하지 않다. 나중에 테스트 하위 디렉터리를 패키지로 탐색하거나 dotted import를 사용할 때만 추가한다.

Task 24에서 `project/minisearch/` 패키지로 이동한 뒤에도 테스트에서는 계속 `import minisearch`를 사용한다. 패키지의 `__init__.py`가 지원할 공개 API를 다시 내보낸다.

### CLI 테스트 템플릿

종료 코드, 표준 출력, 표준 오류를 검사하는 Task는 별도 Python 프로세스를 실행한다.

```python
from pathlib import Path
import subprocess
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_DIR / "minisearch.py"


class Task01Tests(unittest.TestCase):
    def test_prints_sorted_word_counts(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.splitlines(),
            ["list: 1", "python: 3", "tuple: 1"],
        )


if __name__ == "__main__":
    unittest.main()
```

`sys.executable`은 테스트를 실행한 것과 같은 Python interpreter를 사용한다. `cwd=PROJECT_DIR`은 상대 경로의 기준을 고정한다.

### 함수 테스트 템플릿

패키징 전에는 `project/`를 import 경로에 추가한다.

```python
from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

import minisearch


class TaskXXTests(unittest.TestCase):
    def test_observable_behavior(self):
        result = minisearch.count_words(["a", "b", "a"])

        self.assertEqual(result, {"a": 2, "b": 1})


if __name__ == "__main__":
    unittest.main()
```

테스트는 내부 줄 수나 지역 변수 이름이 아니라 반환값, 예외, 파일, CLI 출력처럼 사용자가 관찰할 수 있는 동작을 검사한다.

### 실행 명령

```bash
# 현재 Task만 실행
python3 -m unittest discover -s project/tests \
  -p 'test_task_07.py' -v

# Task 체크포인트 전체 실행
python3 -m unittest discover -s project/tests \
  -p 'test_task_*.py' -v

# Task 33에서 책임별 테스트로 정리한 뒤 전체 실행
python3 -m unittest discover -s project/tests -v
```

- `-s project/tests`: 테스트 탐색 시작 디렉터리
- `-p 'test_task_07.py'`: 실행할 파일 이름 패턴
- `-v`: 테스트 이름과 결과를 자세히 출력

`\`는 shell의 줄 연속 문자다. `\` 바로 뒤에 Enter를 누르면 다음 줄을 이어서 입력할 수 있으며, 다음처럼 한 줄로 입력해도 같다.

```bash
python3 -m unittest discover -s project/tests -p 'test_task_07.py' -v
```

`OK`처럼 보여도 `Ran 0 tests`이면 성공이 아니다. 현재 Task에서 의도한 테스트가 적어도 하나 실행됐는지 확인한다.

### 자동 테스트와 코드 검토의 경계

자동 테스트는 외부 동작을 검증한다. `with` 사용, 중간 리스트 생성 여부, 모듈 의존 방향처럼 동작만으로 판별하기 어려운 항목은 테스트를 통과한 뒤 diff를 별도로 검토한다.

```text
project.md의 Task NN 요구사항과 현재 git diff를 함께 검토해줘.
동작 변경, 중복 책임, 불필요한 추상화, 책에서 아직 배우지 않은 문법을 찾아라.
각 지적은 파일 위치, 실패한 요구사항, 최소 수정안으로 설명해줘.
```

LLM 검토는 테스트를 대신하지 않는다.

---

## 미리 알아둘 최소 검색 개념

- **토큰화:** 텍스트를 검색 단위로 나누는 것
- **역색인:** 단어에서 문서와 해당 문서의 단어 빈도로 가는 매핑. 예: `{"python": {"d1": 3, "d7": 1}}`
- **TF:** 한 문서 안에서 단어가 등장한 횟수
- **IDF:** 전체 문서에서 희귀한 단어에 더 큰 가중치를 주는 값
- **TF-IDF:** 문서별 TF와 전체 코퍼스의 IDF를 결합한 순위 점수

---

## 장별 로드맵 (Task 1~35)

### 1장 · 파이썬 기초 — 하드코딩에서 함수가 있는 스크립트로 (§1.1–1.22)

#### Task 1 · 문자열 하나의 단어 빈도 세기

- **읽고 시작:** §1.3–1.6, §1.8–1.12
- **목표:** 하드코딩한 `TEXT = "Python python PYTHON! list, tuple."`을 `split()`하고 dict로 단어별 횟수를 센다.
- **요구사항:** 소문자화 후 `.,!?;:()`를 토큰 양끝에서 제거한다. 빈 토큰은 세지 않고 단어 오름차순으로 `word: count`를 출력한다. 함수와 명령행 인수는 아직 만들지 않는다.
- **산출물:** `project/minisearch.py`, `project/tests/test_task_01.py`
- **완료 조건:** 대소문자, 중복 횟수, 출력 순서가 모두 맞는다.
- **검증 계약:** 인자 없이 스크립트를 실행해 종료 코드 0, 빈 stderr, 정확한 세 출력 줄을 검사한다.

#### Task 2 · 파일 읽기와 파일 오류 처리

- **읽고 시작:** §1.7, §1.14–1.15
- **목표:** 하드코딩 문자열 대신 `python3 project/minisearch.py FILE`로 받은 UTF-8 파일을 센다.
- **요구사항:** `with open(path, encoding="utf-8")`를 사용한다. `FileNotFoundError`만 잡아 `File not found: PATH`를 stderr에 출력하고 코드 1로 종료한다.
- **산출물:** 수정된 `minisearch.py`, `test_task_02.py`, 짧은 자체 작성 `sample.txt`
- **완료 조건:** 정상 파일과 없는 파일 모두 traceback 없이 정의된 결과를 낸다.
- **검증 계약:** `TemporaryDirectory()`에서 정상·없는 파일을 만들고 정확한 stdout, stderr, 종료 코드를 검사한다.

#### Task 3 · 순수 함수로 경계 나누기

- **읽고 시작:** §1.9–1.13
- **목표:** 읽기, 토큰화, 집계, 결과 선택을 독립 함수로 분리한다.
- **요구사항:** `read_text(path) -> str`, `tokenize(text) -> list[str]`, `count_words(tokens) -> dict[str, int]`, `top_words(counts, limit) -> list[tuple[str, int]]`를 만든다. `top_words`는 횟수 내림차순, 동률 단어 오름차순이며 음수 limit은 `ValueError`다. 불용어 처리는 아직 하지 않는다.
- **산출물:** 네 함수와 `test_task_03.py`
- **완료 조건:** 함수가 전역 상태와 `print()`에 의존하지 않는다.
- **검증 계약:** UTF-8 읽기, 토큰 정규화, 중복 집계, 동률 정렬, limit 0·큰 값·음수를 검사한다.

#### Task 4 · `main(argv)`와 스크립트 진입점

- **읽고 시작:** §1.15, §1.17–1.20
- **목표:** import 가능한 모듈과 실행 가능한 스크립트의 역할을 분리한다.
- **요구사항:** `main(argv) -> int`와 `if __name__ == "__main__": raise SystemExit(main(sys.argv[1:]))`를 사용한다. 저장소 루트 기준 문법은 `python3 project/minisearch.py FILE [LIMIT]`, 기본 LIMIT는 10이다.
- **산출물:** CLI 계약과 `test_task_04.py`
- **완료 조건:** import 시 출력·종료가 없고 잘못된 인수는 usage와 코드 2를 낸다.
- **검증 계약:** 정상 실행, 인자 없음·과다·숫자가 아닌 LIMIT·음수 LIMIT를 subprocess로 검사한다. Task 1~2의 옛 CLI 기대값은 새 계약으로 교체한다.

### 2장 · 연산자·표현식·데이터 조작 — 정보를 잃지 않는 변환 (§2.1–2.19)

#### Task 5 · 컴프리헨션으로 불용어 제거

- **읽고 시작:** §2.12–2.14
- **목표:** 집합 조회와 리스트 컴프리헨션을 사용해 불용어를 제거한다.
- **요구사항:** `filter_stopwords(tokens, stopwords) -> list[str]`는 남은 토큰의 순서와 중복을 보존하며 입력을 수정하지 않는다.
- **산출물:** 함수와 `test_task_05.py`
- **완료 조건:** `tokens - stopwords`처럼 순서와 중복을 잃는 구현을 사용하지 않는다.
- **검증 계약:** 중복, 빈 입력, 전부 제거, 입력 불변성을 검사한다.

#### Task 6 · 정규화와 결과 슬라이싱

- **읽고 시작:** §2.9–2.11
- **목표:** 문자열 정제와 시퀀스 슬라이싱을 분명한 역할에 사용한다.
- **요구사항:** `normalize_token(token) -> str`는 `lower()`와 `strip(".,!?;:()[]{}\"'")`를 사용한다. `top_words`는 정렬한 결과에 `[:limit]`을 적용한다.
- **산출물:** 정규화 함수, 수정된 `tokenize`, `test_task_06.py`
- **완료 조건:** 구두점뿐인 토큰은 제외되고 limit 경계가 유지된다.
- **검증 계약:** 따옴표·괄호·구두점뿐인 입력과 limit 0·1·큰 값을 검사한다.

#### Task 7 · 명시적인 정렬 기준과 제너레이터 표현식

- **읽고 시작:** §2.15, §2.17–2.19
- **목표:** 정렬 규칙을 key 함수에 명시하고 일회성 합계에 제너레이터 표현식을 사용한다.
- **요구사항:** `sorted(items, key=lambda item: (-item[1], item[0]))`와 `sum(count for count in counts.values())`를 사용한다. Python 내장 동작 자체를 회귀 테스트하지 않는다.
- **산출물:** 결정론적 정렬, `total_tokens(counts)`, `test_task_07.py`
- **완료 조건:** dict 삽입 순서와 관계없이 결과가 같다.
- **검증 계약:** 서로 다른 삽입 순서, 빈 dict, 합계를 검사한다.

### 3장 · 프로그램 구조와 제어 흐름 — 실패 경계 다루기 (§3.1–3.7)

#### Task 8 · 여러 문서 처리와 내부 불변식

- **읽고 시작:** §3.1–3.3, §3.5–3.6
- **목표:** 여러 파일을 입력 순서대로 처리하고 `with`, `enumerate`, `assert`의 역할을 구분한다.
- **요구사항:** `process_documents(paths) -> list[tuple[str, dict[str, int]]]`와 `count_document_tokens(tokens)`를 만든다. 후자는 `materialized = tuple(tokens)`로 한 번만 구체화한 뒤 `assert all(materialized)`를 검사하고 같은 tuple을 집계한다. 사용자 입력 검증에는 `assert`를 쓰지 않는다.
- **산출물:** 여러 문서 처리 함수와 `test_task_08.py`
- **완료 조건:** 입력·결과 순서가 같고 파일이 닫히며 후속 제너레이터 전환에도 안전한 경계가 있다.
- **검증 계약:** 두 파일의 순서·빈도와 빈 토큰 내부 오류를 검사한다.

#### Task 9 · 디렉터리 수집과 좁은 예외 처리

- **읽고 시작:** §3.3–3.5
- **목표:** 디렉터리 바로 아래의 `.txt` 파일을 정렬해 읽고 파일별 실패를 격리한다.
- **요구사항:** `collect_documents(directory)`는 성공한 `(path, text)`와 실패한 `(path, error)` 목록을 반환한다. `UnicodeDecodeError`, `OSError`만 처리하고 다른 확장자는 무시한다.
- **산출물:** 수집 함수와 `test_task_09.py`
- **완료 조건:** 한 파일의 실패가 다른 파일을 막지 않는다.
- **검증 계약:** 정상 txt, 다른 확장자, 잘못된 UTF-8, 정렬 순서를 검사한다.

### 4장 · 객체·타입·프로토콜 — 검색 데이터를 객체로 표현하기 (§4.1–4.18)

#### Task 10 · `Document` 값과 표현

- **읽고 시작:** §4.1–4.5, §4.9
- **목표:** 문서를 `Document(doc_id, path, text)` 객체로 표현한다.
- **요구사항:** `repr`에는 ID와 경로만 표시하고 긴 본문은 제외한다.
- **산출물:** `Document`, `test_task_10.py`
- **완료 조건:** 인스턴스끼리 상태를 공유하지 않는다.
- **검증 계약:** 속성 독립성과 repr 내용을 검사한다.

#### Task 11 · 문서 동등성과 해시

- **읽고 시작:** §4.2, §4.11
- **목표:** 같은 `doc_id`를 가진 문서를 같은 논리 문서로 취급한다.
- **요구사항:** `__eq__`, `__hash__`를 doc_id 기준으로 함께 구현하고 doc_id를 생성 뒤 변경하지 않는 계약을 문서화한다. 질의 순위용 `__lt__`는 만들지 않는다.
- **산출물:** 해시 가능한 `Document`, `test_task_11.py`
- **완료 조건:** 동등한 객체의 해시가 같다.
- **검증 계약:** 같은 ID, 다른 ID, 다른 타입, set 중복 제거를 검사한다.

#### Task 12 · `None`, 별칭, 토큰 캐시

- **읽고 시작:** §4.3–4.7
- **목표:** 미계산 상태와 계산된 빈 결과를 구분한다.
- **요구사항:** `_tokens` 초기값은 `None`이고 최초 접근에서 계산한 불변 tuple을 재사용한다.
- **산출물:** 지연 캐시와 `test_task_12.py`
- **완료 조건:** 빈 문서도 한 번만 계산하며 외부가 캐시를 변경할 수 없다.
- **검증 계약:** `None`→tuple 전환, 빈 tuple, 재계산 방지, 불변성을 검사한다.

#### Task 13 · 반복 가능한 `TokenStream`과 컨테이너 `Index`

- **읽고 시작:** §4.13–4.16
- **목표:** 반복·길이·조회·포함 프로토콜을 직접 구현한다.
- **요구사항:** `TokenStream.__iter__()`는 매번 새 iterator를 반환한다. `Index`는 doc_id 기준 `__len__`, `__getitem__`, `__contains__`를 제공한다.
- **산출물:** 두 클래스와 `test_task_13.py`
- **완료 조건:** Python 문법으로 프로토콜을 사용할 수 있다.
- **검증 계약:** 두 번 반복, 길이, 존재·부재 조회, 없는 키를 검사한다.

### 5장 · 함수 — 작은 처리 단계를 조합하기 (§5.1–5.24)

#### Task 14 · 토크나이저 호출 계약

- **읽고 시작:** §5.1–5.8
- **목표:** 위치 전용·키워드 전용 인수, 기본값, docstring, 타입 힌트로 API를 명확히 한다.
- **요구사항:** `tokenize(text, /, *, lowercase=True, stopwords=None)`를 사용하고 가변 기본값을 쓰지 않는다.
- **산출물:** 함수 서명과 `test_task_14.py`
- **완료 조건:** text는 위치로만, 옵션은 키워드로만 전달된다.
- **검증 계약:** `inspect.signature`, 잘못된 호출의 `TypeError`, 호출 간 상태 독립성을 검사한다.

#### Task 15 · 고차 함수·클로저·`partial`로 필터 조합

- **읽고 시작:** §5.12, §5.14–5.17
- **목표:** 작은 토큰 필터를 함수로 조합한다.
- **요구사항:** `pipe(*funcs)`, `min_length(n)` 클로저, `partial(drop_stopwords, stopwords=...)`를 구현한다. 제품에는 읽기 쉬운 함수 조합만 남긴다.
- **산출물:** 필터 함수와 `test_task_15.py`
- **완료 조건:** 파이프라인 인스턴스끼리 상태를 공유하지 않는다.
- **검증 계약:** 합성 순서, 길이 경계, 서로 다른 설정의 독립성을 검사한다.

#### Task 16 · 메타데이터를 보존하는 데코레이터

- **읽고 시작:** §5.18
- **목표:** 원래 함수의 계약을 바꾸지 않고 호출과 실행 시간을 관찰한다.
- **요구사항:** `timed(*, record)`와 `log_calls(*, record)` 데코레이터 팩토리를 만든다. record는 문자열 또는 측정값을 받는 함수이며 테스트에서는 list의 `append`를 주입한다. `functools.wraps`를 사용하고 원본 반환값·예외를 보존한다.
- **산출물:** 두 데코레이터와 `test_task_16.py`
- **완료 조건:** 시간 측정 때문에 함수 반환 타입이 바뀌지 않는다.
- **검증 계약:** 기록 1회, 메타데이터, 위치·키워드 인수, 반환값, 예외 전파를 검사하되 정확한 실행 시간은 비교하지 않는다.

### 6장 · 제너레이터 — 전체를 만들지 않고 흘려보내기 (§6.1–6.8)

#### Task 17 · 지연 토큰화

- **읽고 시작:** §6.1
- **목표:** `tokenize()`가 리스트 대신 토큰을 하나씩 yield한다.
- **요구사항:** 공개 반환 계약을 `Iterable[str]`로 유지하고 호출자가 필요할 때만 `list()`로 구체화한다.
- **산출물:** 제너레이터 토크나이저와 `test_task_17.py`
- **완료 조건:** 중간 결과 리스트 없이 이전 토큰 결과를 유지한다.
- **검증 계약:** generator 여부, 지연 실행, 정확한 결과, 빈 입력을 검사한다.

#### Task 18 · `yield from` 필터 파이프라인

- **읽고 시작:** §6.3–6.4
- **목표:** 소문자화·정규화·불용어 단계를 지연 연결한다.
- **요구사항:** 각 단계가 iterable을 받아 yield하고 바깥 파이프라인은 마지막 단계에 `yield from`을 사용한다.
- **산출물:** 지연 파이프라인과 `test_task_18.py`
- **완료 조건:** 순서·중복을 보존하고 중간 리스트를 만들지 않는다.
- **검증 계약:** 혼합 대소문자, 구두점, 불용어, 빈 입력, 중복을 검사한다.

#### Task 19 · 재시작 가능한 `Corpus`

- **읽고 시작:** §6.2, §6.4
- **목표:** 같은 코퍼스를 여러 번 순회할 수 있게 한다.
- **요구사항:** `Corpus(paths)`는 경로를 tuple로 보관하고 `__iter__()` 호출마다 새 Document 제너레이터를 반환한다. 미리보기에는 `itertools.islice`를 사용한다.
- **산출물:** `Corpus`, `test_task_19.py`
- **완료 조건:** 같은 객체를 두 번 순회해 동등한 문서를 얻는다.
- **검증 계약:** 두 번 순회, islice 경계, 빈 코퍼스를 검사한다.

### 7장 · 클래스와 객체지향 — 설정과 검색 상태 묶기 (§7.1–7.33)

#### Task 20 · 호출 가능한 `Tokenizer`

- **읽고 시작:** §7.1–7.6, §7.8–7.10
- **목표:** 토큰화 설정과 동작을 한 객체로 묶되 불필요한 상속 계층은 만들지 않는다.
- **요구사항:** `Tokenizer`는 설정을 보관하고 `__call__(text)`로 iterable을 반환한다. 기존 `tokenize()`는 기본 Tokenizer를 호출하는 호환 함수로 남긴다.
- **산출물:** `Tokenizer`, `test_task_20.py`
- **완료 조건:** 설정이 다른 인스턴스가 독립적이다.
- **검증 계약:** callable, 소문자화 on/off, 불용어 설정, 함수형 API와의 동등성을 검사한다.

#### Task 21 · 빈도를 보존하는 역색인과 불리언 질의

- **읽고 시작:** §7.12–7.17
- **목표:** 불리언 검색과 이후 TF-IDF가 함께 사용할 `InvertedIndex`를 만든다.
- **요구사항:** 내부 posting 계약은 `dict[str, dict[str, int]]`, 즉 `term -> doc_id -> raw term frequency`다. `add(document)`, `search_all(terms)`, `search_any(terms)`를 제공하고 검색 결과는 doc_id 오름차순이다. 같은 doc_id를 다시 추가하면 옛 posting을 제거한 뒤 새 내용으로 교체한다.
- **산출물:** 역색인과 `test_task_21.py`
- **완료 조건:** 빈도가 보존되고 재색인해도 낡은 단어가 남지 않는다.
- **검증 계약:** 단일어, AND, OR, 없는 단어, 빈 질의, 재색인 교체, 빈도를 검사한다.

#### Task 22 · 대안 생성자와 TF-IDF 순위 검색

- **읽고 시작:** §7.12–7.13, §7.17
- **목표:** 디렉터리에서 인덱스를 만들고 질의별 점수를 계산한다.
- **요구사항:** `InvertedIndex.from_directory(path)`와 `idf(total_docs, doc_frequency) = log((1 + total_docs) / (1 + doc_frequency)) + 1`을 만든다. `search_ranked(query, limit)`는 정규화한 중복 질의어를 한 번씩 사용하고 `sum(raw_tf * idf)`로 계산한다. 음수 limit은 `ValueError`, 점수 0 문서는 제외하며 점수 내림차순·동률 ID 오름차순이다.
- **산출물:** `SearchResult(doc_id, score)`, 생성자, 순위 검색, `test_task_22.py`
- **완료 조건:** `Document.__lt__` 없이 순위가 결정론적이다.
- **검증 계약:** 희귀어 IDF, 중복 질의어, 빈·없는 질의, limit, 동률, 임시 디렉터리를 검사한다.

### 8장 · 모듈과 패키지 — 설치 가능한 구조로 나누기 (§8.1–8.18)

#### Task 23 · 책임별 모듈 분리

- **읽고 시작:** §8.1–8.4
- **목표:** 한 파일을 `document.py`, `tokenizer.py`, `index.py`, `query.py`, `cli.py`로 분리한다.
- **요구사항:** 임시 단계에서는 파일을 `project/` 바로 아래에 두고 `minisearch.py`를 공개 API facade로 유지한다. 의존 방향은 값 객체 → 토큰화 → 인덱스 → 질의 → CLI이며 import 시 I/O가 없어야 한다.
- **산출물:** 모듈 파일, facade, `test_task_23.py`
- **완료 조건:** 기존 공개 테스트와 독립 모듈 import가 모두 성공한다.
- **검증 계약:** 각 모듈 import, 무부수효과, 기존 토큰화·검색 회귀를 검사한다.

#### Task 24 · 정규 패키지와 공개 API

- **읽고 시작:** §8.9–8.13
- **목표:** `project/minisearch/` 정규 패키지를 만들고 지원할 이름만 공개한다.
- **요구사항:** Task 23의 모듈을 패키지로 이동하고 루트 복제본을 삭제한다. `__init__.py`와 상대 import를 사용하며 `__all__`에는 지원할 공개 API만 둔다.
- **산출물:** 패키지와 `test_task_24.py`
- **완료 조건:** `from minisearch import ...`가 동작하고 전체 회귀 테스트가 유지된다.
- **검증 계약:** 공개 이름 import, `__all__` 일치, 내부 helper 비공개, 전체 회귀를 검사한다.

#### Task 25 · `python -m minisearch`와 패키지 데이터

- **읽고 시작:** §8.8, §8.11, §8.14–8.15, §8.17
- **목표:** 패키지를 모듈로 실행하고 기본 불용어 데이터를 안전하게 읽는다.
- **요구사항:** `__main__.py`는 `cli.main()`만 호출한다. `data/stopwords.txt`는 `importlib.resources`로 읽는다. argparse는 아직 도입하지 않았으므로 실행 계약은 `python3 -m minisearch FILE [LIMIT]`다.
- **산출물:** `__main__.py`, 리소스 로더, `test_task_25.py`
- **완료 조건:** 다른 cwd에서도 실행과 데이터 로드가 된다.
- **검증 계약:** subprocess의 `PYTHONPATH`에 `project/`를 넣고 임시 cwd에서 실제 임시 텍스트 파일을 전달해 코드 0과 출력을 검사한다. 이 단계에서는 `--help`를 요구하지 않는다.

#### Task 26 · `pyproject.toml`과 콘솔 명령

- **읽고 시작:** §8.16, [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- **목표:** editable install 가능한 패키지를 만든다.
- **요구사항:** `project/pyproject.toml`에 `[build-system]`, `[project]`, `[project.scripts]`, package data 설정을 작성하고 `requires-python = ">=3.11"`을 명시한다. 콘솔 진입점은 인수 없는 `minisearch.cli:main_cli`를 가리킨다. 배포용 설명은 `project/README.md`에 둔다.
- **산출물:** `project/pyproject.toml`, `project/README.md`, `main_cli()`
- **완료 조건:** 깨끗한 임시 가상환경에서 import, 모듈 실행, 콘솔 실행이 된다.
- **검증 계약:** 네트워크 가능성 때문에 일반 단위 테스트에 넣지 않고 아래 설치 통합 명령을 Task 완료 시 직접 실행한다.

```bash
minisearch_venv="$(mktemp -d)/venv"
python3 -m venv "$minisearch_venv"
"$minisearch_venv/bin/python" -m pip install -e ./project
"$minisearch_venv/bin/python" -c "import minisearch"
"$minisearch_venv/bin/minisearch" project/sample.txt 3
```

### 9장 · 입력과 출력 — CLI와 영속성 (§9.1–9.16)

#### Task 27 · JSON 인덱스 저장과 복원

- **읽고 시작:** §9.12–9.13, §9.15
- **목표:** 서로 다른 CLI 프로세스가 공유할 수 있도록 인덱스를 JSON으로 저장한다.
- **요구사항:** `save(path)`와 `load(path)`는 UTF-8, `with`, 스키마 버전을 사용한다. posting의 키를 정렬하고 `sort_keys=True`를 사용해 바이트 결과를 결정론적으로 만든다. 신뢰할 수 없는 Pickle은 사용하지 않는다.
- **산출물:** JSON 영속성과 `test_task_27.py`
- **완료 조건:** 저장→로드 후 문서 수, posting, 검색 결과가 같다.
- **검증 계약:** round trip, 두 번 저장한 바이트, 손상 JSON, 누락 필드, 미래 버전을 검사한다.

#### Task 28 · `argparse` 서브커맨드와 인덱스 경로

- **읽고 시작:** §9.4–9.5
- **목표:** 실제로 연결된 `index`, `search`, `stats` 명령을 제공한다.
- **요구사항:** `build_parser()`를 분리한다. 계약은 `index DIRECTORY [--output INDEX] [--stopwords FILE]`, `search QUERY [--index INDEX] [--limit N]`, `stats [--index INDEX]`이며 INDEX 기본값은 `.minisearch-index.json`이다. `MINISEARCH_STOPWORDS`는 선택적인 불용어 파일이고 `--stopwords`가 환경 변수보다 우선한다. 이 단계의 `stats`는 문서 수와 어휘 수를 출력하며 Task 31에서 길이 통계를 추가한다.
- **산출물:** argparse CLI와 `test_task_28.py`
- **완료 조건:** `index` 결과를 다음 프로세스의 `search`와 `stats`가 읽는다. 각 `--help`는 코드 0이다.
- **검증 계약:** parser 단위 테스트와 작은 코퍼스의 subprocess `index → search → stats` 흐름을 검사한다.

#### Task 29 · 인코딩 정책·출력 형식·로깅

- **읽고 시작:** §9.1–9.3, §9.8–9.11
- **목표:** 사용자 결과와 진단 메시지를 분리한다.
- **요구사항:** 기본 인코딩은 UTF-8이다. 파일을 읽는 `index`와 `analyze` 명령에 `--errors strict|replace`를 제공한다. 결과는 stdout, 경고는 `logging`을 통해 stderr로 보내며 점수는 고정 소수점으로 출력한다.
- **산출물:** I/O 정책과 `test_task_29.py`
- **완료 조건:** strict는 잘못된 바이트에서 실패하고 replace는 경고 후 계속 처리한다.
- **검증 계약:** 두 오류 정책, stdout/stderr 분리, 점수 형식을 검사한다.

### 10장 · 내장 함수와 표준 라이브러리 — 직접 짠 코드를 단순화하기 (§10.1–10.4)

#### Task 30 · `Counter`와 `defaultdict`로 집계 단순화

- **읽고 시작:** §10.1, §10.3.1
- **목표:** 수동 빈도·posting 초기화를 표준 컨테이너로 단순화한다.
- **요구사항:** 단어 빈도는 `Counter`, posting 구성은 필요할 때 `defaultdict(dict)`를 사용하되 공개 경계에서는 평범한 dict로 반환한다.
- **산출물:** 리팩터링과 `test_task_30.py`
- **완료 조건:** 외부 동작과 결정론적 저장 결과가 이전과 같다.
- **검증 계약:** Task 3·21·27의 표 기반 회귀와 없는 키 조회의 무부수효과를 검사한다.

#### Task 31 · `itertools`와 `statistics`로 코퍼스 통계

- **읽고 시작:** §10.1, §10.3.3, §10.3.10
- **목표:** 문서 길이 통계를 표준 라이브러리로 계산한다.
- **요구사항:** `statistics.mean`, `median`과 필요한 경우 `itertools.chain`, `islice`를 사용한다. 빈 코퍼스 결과는 `{"count": 0, "min": None, "max": None, "mean": None, "median": None}`다.
- **산출물:** `corpus_statistics(documents)`, `test_task_31.py`
- **완료 조건:** 홀수·짝수·빈 입력 결과가 정의돼 있다.
- **검증 계약:** 빈 입력, 단일 문서, 홀수·짝수 길이 목록을 검사한다.

#### Task 32 · 정규식 토큰화와 실행 시간 관찰

- **읽고 시작:** §10.3.8, §10.3.12
- **목표:** 기본 토크나이저와 Unicode 정규식 토크나이저를 비교한다.
- **요구사항:** `RegexTokenizer`는 사전 컴파일한 `re.compile(r"[^\W_]+", re.UNICODE)`를 사용한다. `time.perf_counter()`로 관찰하되 특정 속도 향상을 테스트 조건으로 삼지 않는다.
- **산출물:** 정규식 토크나이저와 `test_task_32.py`
- **완료 조건:** 옵션으로 선택 가능하고 기본 계약을 깨지 않는다.
- **검증 계약:** 구두점, 공백, Unicode, 숫자, 빈 입력과 0 이상인 측정값을 검사한다.

#### Task 33 · 책임별 회귀 테스트로 정리

- **읽고 시작:** §10.3.14
- **목표:** Task별 체크포인트를 공개 API 책임별 테스트로 정리한다.
- **요구사항:** `test_tokenizer.py`, `test_index.py`, `test_persistence.py`, `test_cli.py`를 만든다. 표 기반 경우는 `subTest`, 파일은 `TemporaryDirectory`를 사용한다. 동등한 책임별 테스트가 생긴 뒤에만 중복 Task 테스트를 삭제한다.
- **산출물:** 정리된 테스트 스위트
- **완료 조건:** 아래 전체 테스트 명령이 코드 0이며 핵심 assertion을 수동으로 반대로 바꾸면 실패한다.
- **검증 계약:** 전체 테스트 명령은 테스트 함수 안에서 subprocess로 호출하지 않고 shell에서 한 번 실행한다. 따라서 테스트가 자기 자신을 재귀 실행하지 않는다.

```bash
python3 -m unittest discover -s project/tests -v
```

#### Task 34 · `analyze`와 최종 사용자 문서

- **읽고 시작:** §10.4와 앞 장 전체 복습
- **목표:** 단일 파일 분석 명령과 처음 사용하는 사람을 위한 문서를 완성한다.
- **요구사항:** `analyze FILE`은 토큰 수, 고유 토큰 수, 상위 빈도를 출력한다. 저장소 안내는 루트 `README.md`, 설치·CLI 안내는 `project/README.md`에 둔다. 버전은 `pyproject.toml`의 `[project].version`에만 저장하고 코드에서 필요하면 `importlib.metadata.version()`으로 읽는다.
- **산출물:** `analyze`, 두 README, 버전 정보, `test_cli.py` 보강
- **완료 조건:** README만 보고 설치→index→search→stats→analyze→test를 재현할 수 있다.
- **검증 계약:** 작은 고정 코퍼스로 전체 CLI 흐름과 출력 필드를 검사한다.

#### Task 35 · 깨끗한 환경의 v1.0 검증

- **읽고 시작:** 전체 복습
- **목표:** 소스 경로 우연이나 기존 설치에 기대지 않고 최종 산출물을 검증한다.
- **요구사항:** 임시 가상환경에 editable install하고 임시 코퍼스에서 모든 CLI 명령과 전체 단위 테스트를 실행한다. 설치 통합 검증은 단위 테스트 파일 안에서 자기 자신을 실행하지 않는다.
- **산출물:** 검증 기록과 `v1.0.0` 버전
- **완료 조건:** 설치, import, 모듈 실행, 콘솔 명령, 전체 테스트가 모두 코드 0이다.
- **검증 계약:** Task 26의 가상환경 명령에 `index → search → stats → analyze`와 전체 테스트 실행을 추가해 shell에서 수행한다.

---

## 외부 텍스트 사용 원칙

처음 코퍼스에는 직접 작성한 `project/sample.txt`를 사용한다. Wikipedia나 다른 웹페이지의 텍스트를 사용하려면 원문 URL, 라이선스, 변경 여부를 함께 기록한다. 책 본문, 공식 예제 코드, 스캔·PDF는 공개 저장소에 넣지 않는다.

## 완료 체크리스트

- [ ] Task 1~35가 순서대로 실행 가능한 커밋으로 남아 있다.
- [ ] `python3 -m unittest discover -s project/tests -v`가 테스트 0개가 아닌 상태로 통과한다.
- [ ] `python -m minisearch --help`와 설치된 `minisearch --help`가 동작한다.
- [ ] `index`가 만든 명시적 JSON 파일을 별도 `search`·`stats` 프로세스가 읽는다.
- [ ] 같은 코퍼스를 다시 색인하면 결정론적인 JSON과 검색 결과가 나온다.
- [ ] 루트 README와 `project/README.md`의 명령을 깨끗한 환경에서 재현할 수 있다.
- [ ] 외부 자료의 출처와 라이선스를 기록했고 책 원문·공식 예제를 재배포하지 않는다.
