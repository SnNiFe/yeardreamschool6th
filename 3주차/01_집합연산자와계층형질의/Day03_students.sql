-- ============================================================
--  Day 03 학생 실습 SQL (student copy)
--  주제: 집합 연산자 / 집계 함수 / 서브쿼리 / 계층형 질의
--  데이터베이스: SQLite Chinook DB
--  참고: https://www.sqlitetutorial.net/sqlite-sample-database/
--        https://www.sqlitetutorial.net/sqlite-union/
--        https://www.sqlitetutorial.net/sqlite-except/
--        https://www.sqlitetutorial.net/sqlite-intersect/
--        https://www.sqlitetutorial.net/sqlite-aggregate-functions/
--        https://www.sqlitetutorial.net/sqlite-subquery/
--        https://www.sqlitetutorial.net/sqlite-exists/
-- ============================================================
--
--  Chinook DB 테이블 (11개)
--  ┌─────────────────┬──────────────────────────────────────┐
--  │ 테이블           │ 설명                                  │
--  ├─────────────────┼──────────────────────────────────────┤
--  │ employees       │ 직원 (ReportsTo → 계층형 구조)         │
--  │ customers       │ 고객 (SupportRepId → employees FK)    │
--  │ invoices        │ 청구서 헤더                            │
--  │ invoice_items   │ 청구서 라인 아이템                      │
--  │ artists         │ 아티스트                               │
--  │ albums          │ 앨범 (ArtistId FK)                    │
--  │ tracks          │ 트랙 (AlbumId / GenreId / MediaTypeId)│
--  │ genres          │ 장르                                  │
--  │ media_types     │ 미디어 타입                            │
--  │ playlists       │ 플레이리스트                           │
--  │ playlist_track  │ 플레이리스트-트랙 (M:N 중간 테이블)     │
--  └─────────────────┴──────────────────────────────────────┘
-- ============================================================


-- ============================================================
-- PART 1. 집계 함수 (Aggregate Functions)
-- ============================================================
-- 집계 함수는 여러 행(row)을 입력받아 단일 값을 반환한다
-- GROUP BY, HAVING 절과 함께 자주 사용
--
-- SQLite 제공 집계 함수
--   COUNT()        : 행 수
--   SUM()          : 합계
--   AVG()          : 평균
--   MAX()          : 최댓값
--   MIN()          : 최솟값
--   GROUP_CONCAT() : 문자열 연결 (separator 지정 가능)
--
-- 문법: aggregate_function([DISTINCT | ALL] expression)
--   DISTINCT → 중복 제외 후 집계
--   ALL      → 중복 포함 집계 (기본값)
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 1-1. COUNT() - 행 수 반환
-- ──────────────────────────────────────────────────────────

-- (a) 전체 트랙 수
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 앨범별 트랙 수 (내림차순)


-- (c) 국가별 고객 수

-- (d) DISTINCT - 중복 제거 후 COUNT
--     실제 청구서가 발생한 고유 고객 수

SELECT COUNT(DISTINCT CustomerId) AS 실제구매고객수
FROM invoices;



-- ──────────────────────────────────────────────────────────
-- 1-2. SUM() - 합계
-- ──────────────────────────────────────────────────────────

-- (a) 앨범별 총 재생 시간 (분 단위)
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 연도별 총 매출
SELECT 
    strftime('%Y', InvoiceDate) AS 연도
    , ROUND(SUM(Total), 1)      AS 연매출
FROM invoices
GROUP BY 연도
;

-- (c) 장르별 총 트랙 용량 (MB)


-- ──────────────────────────────────────────────────────────
-- 1-3. AVG() - 평균
-- ──────────────────────────────────────────────────────────

-- (a) 앨범별 평균 트랙 길이 (분)
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 고객 1인당 평균 청구 금액

-- (c) 미디어 타입별 평균 단가


-- ──────────────────────────────────────────────────────────
-- 1-4. MAX() / MIN() - 최댓값·최솟값
-- ──────────────────────────────────────────────────────────

-- (a) 가장 긴 트랙의 재생 시간 (분)
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 가장 짧은 트랙의 재생 시간 (분)


-- (c) 고객별 최대·최소 청구 금액


-- ──────────────────────────────────────────────────────────
-- 1-5. GROUP_CONCAT() - 문자열 연결
-- ──────────────────────────────────────────────────────────

-- (a) 앨범 ID = 1 의 트랙 이름 목록 (쉼표 구분)
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/
SELECT GROUP_CONCAT(Name) AS 트랙목록
FROM tracks
WHERE AlbumId = 1
;

-- (b) 구분자를 ' / ' 로 변경
SELECT GROUP_CONCAT(Name, ' / ') AS 트랙목록
FROM tracks
WHERE AlbumId = 1
;

-- (c) 장르별 미디어 타입 종류 나열
SELECT 
    g.Name                          AS 장르
    , GROUP_CONCAT(DISTINCT m.Name) AS 미디어타입목록
FROM tracks t
INNER JOIN genres g ON t.GenreId = g.GenreId
INNER JOIN media_types m ON t.MediaTypeId = m.MediaTypeId
GROUP BY g.Name
;

-- ──────────────────────────────────────────────────────────
-- 1-6. HAVING - 집계 결과 필터링
--      WHERE 는 집계 전 개별 행 필터
--      HAVING 은 집계 후 그룹 필터
-- ──────────────────────────────────────────────────────────

-- (a) 트랙이 15개 이상인 앨범

-- (b) 총 매출이 $40 이상인 고객

-- (c) 평균 트랙 단가가 $0.99 초과인 장르


-- ============================================================
-- PART 2. 서브쿼리 (Subquery)
-- ============================================================
-- 서브쿼리(내부 쿼리/중첩 쿼리): 다른 SQL 문 안에 포함된 SELECT
-- 위치에 따른 분류
--   WHERE 절  : 조건 비교에 활용 (가장 일반적)
--   FROM  절  : 인라인 뷰(Inline View) / 파생 테이블(Derived Table)
--   SELECT 절 : 스칼라 서브쿼리 (행마다 단일값 반환)
--
-- 연관성에 따른 분류
--   비연관(Non-Correlated) : 외부 쿼리와 독립적으로 실행
--   연관(Correlated)       : 외부 쿼리의 값을 참조, 행마다 재실행
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 2-1. WHERE 절 서브쿼리 (비연관)
-- ──────────────────────────────────────────────────────────

-- (a) 가장 긴 트랙 정보 조회
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 가장 짧은 트랙 정보 조회

-- (c) 평균 청구 금액보다 높은 청구서 목록
-- 테이블 invoices
-- 메인쿼리 : InvoiceId, CustomerId, 청구금액
SELECT InvoiceId, CustomerId, Total AS 청구금액 FROM invoices;

-- 서브쿼리 : 평균 청구 금액
SELECT AVG(Total) FROM invoices;

--메인쿼리 + 서브쿼리
SELECT InvoiceId, CustomerId, Total AS 청구금액
FROM invoices
WHERE Total > (SELECT AVG(Total) FROM invoices)
ORDER BY Total DESC
;

-- (d) IN 서브쿼리 - Rock 장르 트랙 조회

-- (e) NOT IN 서브쿼리 - 한 번도 판매되지 않은 트랙


-- ──────────────────────────────────────────────────────────
-- 2-2. FROM 절 서브쿼리 - 인라인 뷰 (Derived Table)
--      서브쿼리 결과를 임시 테이블처럼 사용
-- ──────────────────────────────────────────────────────────

-- (a) 고객별 총 매출 TOP 5
SELECT *
FROM (인라인 뷰)
JOIN customers ON
ORDER BY 
LIMIT 5
;

-- 총매출 구하기
-- 구체적으로 고객id, 고객이름, 총매출

SELECT 
    sub.CustomerId
    , c.FirstName || ' ' || c.LastName AS 고객명
    , sub.총매출
    FROM (
    SELECT CustomerId, SUM(Total) AS 총매출
    FROM invoices
    GROUP BY CustomerId
) AS sub
INNER JOIN customers c ON sub.CustomerId = c.CustomerId
ORDER BY 3 DESC
LIMIT 5
;


-- (b) 앨범별 트랙 수 평균보다 많은 앨범 조회

-- (c) 용량이 10MB 미만인 앨범 조회
-- ref: sqlitetutorial.net 서브쿼리 예제 패턴

-- 메인쿼리 : 앨범 조회 => AlbumId, Title



-- ──────────────────────────────────────────────────────────
-- 2-3. SELECT 절 서브쿼리 - 스칼라 서브쿼리
--      행마다 단일 값을 반환 (연관 서브쿼리)
-- ──────────────────────────────────────────────────────────

-- (a) 앨범별 트랙 수를 SELECT 절에서 계산
-- ref: https://www.sqlitetutorial.net/sqlite-aggregate-functions/

-- (b) 고객별 최근 청구 날짜를 SELECT 절에서 계산

-- (c) 트랙 이름과 해당 장르 이름을 스칼라 서브쿼리로 조회


-- ──────────────────────────────────────────────────────────
-- 2-4. 연관 서브쿼리 (Correlated Subquery)
--      외부 쿼리의 값을 참조 → 행마다 서브쿼리 재실행
--      ※ 대용량 데이터에서는 성능 주의
-- ──────────────────────────────────────────────────────────

-- (a) 자신이 속한 장르의 평균 단가보다 비싼 트랙

-- (b) 평균 트랙 수보다 많은 트랙을 가진 앨범


-- ──────────────────────────────────────────────────────────
-- 2-5. EXISTS / NOT EXISTS
--      서브쿼리가 행을 반환하면 TRUE, 없으면 FALSE
--      ※ 결과 집합이 클 때 IN 보다 빠른 경향
-- ──────────────────────────────────────────────────────────

-- (a) 청구서가 있는 고객 조회 (EXISTS)
-- ref: https://www.sqlitetutorial.net/sqlite-exists/

-- (b) 앨범이 없는 아티스트 조회 (NOT EXISTS)
-- ref: https://www.sqlitetutorial.net/sqlite-exists/

-- (c) 한 번도 판매된 적 없는 트랙 조회 (NOT EXISTS)


-- ──────────────────────────────────────────────────────────
-- 2-6. 서브쿼리 활용 종합 예제
-- ──────────────────────────────────────────────────────────

-- (a) 각 고객의 총 구매액이 전체 고객 평균 이상인 VIP 고객

-- (b) 가장 많이 팔린 장르 TOP 3

-- (c) 각 아티스트의 앨범 수 + 총 트랙 수 (서브쿼리 in FROM)


-- ============================================================
-- PART 3. 집합 연산자 (Set Operators)
-- ============================================================
--  연산자      | 중복제거 | 정렬발생 | 역할
--  ------------|----------|----------|-----------
--  UNION       |    O     |    O     | 합집합
--  UNION ALL   |    X     |    X     | 합집합(빠름)
--  INTERSECT   |    O     |    O     | 교집합
--  EXCEPT      |    O     |    O     | 차집합
--
--  공통 규칙
--   1) SELECT 컬럼 수가 동일해야 한다
--   2) 대응 컬럼의 데이터 타입이 호환되어야 한다
--   3) 첫 번째 쿼리의 컬럼명이 최종 결과셋 컬럼명
--   4) ORDER BY 는 최종 결합 결과에만 적용
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 3-1. UNION - 합집합 (중복 제거)
-- ──────────────────────────────────────────────────────────

-- (a) 직원 이름 + 고객 이름 통합 목록
-- ref: https://www.sqlitetutorial.net/sqlite-union/
SELECT FirstName, LastName, 'Employee' AS Type
FROM employees

UNION

SELECT FirstName, LastName, 'customer'
FROM customers

ORDER BY FirstName, LastName
;


-- (b) 구매 이력 유무별 고객 분류
-- 테이블명: customers, invoices
-- 출력 : CustomerId, FirstName + LastName 고객명 AS 고객명, 
--                      'Has Invoice' / 'No Invoice'
-- HINT : WHERE 절 Customer ID 활용해서 서브쿼리
SELECT CustomerId, FirstName || ' ' || LastName AS 고객명, 'Has Invoice' AS stat
FROM customers
WHERE CustomerId IN (SELECT DISTINCT CustomerId FROM invoices)

UNION

SELECT CustomerId, FirstName || ' ' || LastName AS 고객명, 'No Invoice'
FROM customers
WHERE CustomerId NOT IN (SELECT DISTINCT CustomerId FROM invoices)
;




-- ──────────────────────────────────────────────────────────
-- 3-2. UNION ALL - 합집합 (중복 포함, 더 빠름)
-- ──────────────────────────────────────────────────────────

-- (a) 연도별 매출 + 전체 합계 리포트 (소계 패턴)
SELECT 
    strftime('%Y', InvoiceDate) AS 연도
    , ROUND(SUM(Total), 2) AS 매출합계
FROM invoices
GROUP BY 연도

UNION ALL

SELECT '------전체합계'
    , ROUND(SUM(Total), 1)
FROM invoices
;


-- (b) 장르별 트랙 수 + 전체 합계
-- 테이블명 : genres, tracks
-- LEFT JOIN
SELECT 
    g.Name              AS 장르명
    , COUNT(t.TrackId)  AS 트랙수
FROM genres g
LEFT JOIN tracks t
    ON t.GenreId = g.GenreId
GROUP BY g.Name

UNION ALL

SELECT '------전체합계'
    , COUNT(*)
FROM tracks
;



-- ──────────────────────────────────────────────────────────
-- 3-3. INTERSECT - 교집합
-- ──────────────────────────────────────────────────────────

-- (a) 청구서가 있는 고객 (INTERSECT 방식)
-- ref: https://www.sqlitetutorial.net/sqlite-intersect/
-- 현재 문제점.. customers 59명, invoices 59명 모두 구매를 했음
-- 차집합을 하거나 할 때, 차이점이 존재하지 않는다.


-- (b) 2009년과 2010년 모두 구매한 고객 ID
-- 2009년에 구매한 고객 id
-- 테이블 : invoices
SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2009'

INTERSECT

SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2010'
;

-- 고객 이름 궁금함, 고객 id FirstName, LastName
SELECT c.CustomerId, c.FirstName, c.LastName
FROM customers c
INNER JOIN (
SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2009'

INTERSECT

SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2010'
) AS y
ON c.CustomerId = y.CustomerId
;



-- ──────────────────────────────────────────────────────────
-- 3-4. EXCEPT - 차집합
-- ──────────────────────────────────────────────────────────

-- (a) 청구서 없는 고객 (전체 - 청구서 있는 고객)
-- ref: https://www.sqlitetutorial.net/sqlite-except/


-- (b) 2009년 구매 고객 중 2010년에 구매 안 한 고객
SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2009'

EXCEPT

SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2010'
;

--
SELECT c.CustomerId, c.FirstName || ' ' || c.LastName AS Name, c.Email
FROM customers c
INNER JOIN (
SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2009'

EXCEPT

SELECT CustomerId
FROM invoices
WHERE strftime('%Y', InvoiceDate) = '2010'
) AS y
ON c.CustomerId = y.CustomerId
;


-- (c) 플레이리스트에 없는 트랙 (미포함 트랙)


-- ============================================================
-- PART 4. 집계 함수 + 서브쿼리 + 집합 연산자 복합 활용
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 4-1. 집계 + (서브쿼리)INNER JOIN + UNION ALL
--      장르별 매출 통계 리포트 (합계 행 포함)
-- ──────────────────────────────────────────────────────────
-- 테이블명 : invoice_items, tracks, genres
-- 집합연산자 : UNION ALL

SELECT 
    g.Name                                      AS 장르
    , COUNT(DISTINCT ii.InvoiceId)              AS 청구서수
    , SUM(ii.Quantity)                          AS 판매수량
    , ROUND(SUM(ii.InvoiceId * ii.Quantity), 2) AS 총매출
FROM invoice_items ii
INNER JOIN tracks t ON ii.TrackId = t.TrackId
INNER JOIN genres g ON t.GenreId = g.GenreId
GROUP BY g.Name

UNION ALL

SELECT '------전체합계'
    , COUNT(DISTINCT InvoiceId)
    , SUM(Quantity)
    , ROUND(SUM(InvoiceId * Quantity), 2)
FROM invoice_items
;


-- ──────────────────────────────────────────────────────────
-- XXX 4-2. 서브쿼리 + EXCEPT
--      판매 실적이 있는 트랙 중 현재 플레이리스트에 없는 트랙
-- ──────────────────────────────────────────────────────────
-- 확인 1: 판매된 트랙 수

-- 확인 2: 플레이리스트에 있는 트랙 수

-- 확인 3: 판매됐지만 플리에 없는 트랙

-- 확인 4: 플리에 있지만 판매 안 된 트랙 (반대 방향)


-- ──────────────────────────────────────────────────────────
-- 4-3. 집계 + HAVING + EXISTS 조합
--      앨범이 2개 이상이면서 총 트랙이 30개 이상인 아티스트
-- ──────────────────────────────────────────────────────────
-- join, where, exists...




-- ──────────────────────────────────────────────────────────
-- XXX 4-4. 인라인 뷰 + UNION ALL - 월별 매출 + 분기 소계
-- ──────────────────────────────────────────────────────────


-- ============================================================
-- PART 5. 계층형 질의 (Hierarchical Query)
-- ============================================================
-- SQLite 방식: WITH RECURSIVE CTE
-- 대상 테이블: employees
--   EmployeeId : PK
--   ReportsTo  : 상위 관리자 FK (NULL = 최상위 Root)
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 5-1. 기본 계층형 질의 - 보고 체계 전체 조회
-- ──────────────────────────────────────────────────────────
WITH RECURSIVE emp_hierarchy(
    EmployeeId, FirstName, LastName, Title, ReportsTo, lvl
) AS (
    -- Anchor: 최상위 직원 (Root)
    SELECT EmployeeId, FirstName, LastName, Title, ReportsTo,
           0 AS lvl
    FROM employees
    WHERE ReportsTo IS NULL

    UNION ALL

    -- Recursive: 직속 부하 반복 탐색
    SELECT e.EmployeeId, e.FirstName, e.LastName,
           e.Title, e.ReportsTo, h.lvl + 1
    FROM employees e
    JOIN emp_hierarchy h ON e.ReportsTo = h.EmployeeId
)
SELECT lvl                                                AS 계층레벨,
       EmployeeId                                         AS 직원ID,
       SUBSTR('                ', 1, lvl * 4)
           || FirstName || ' ' || LastName                AS 직원명,
       Title                                              AS 직책,
       ReportsTo                                          AS 관리자ID
FROM emp_hierarchy
ORDER BY lvl, EmployeeId;


-- ──────────────────────────────────────────────────────────
-- 5-2. 계층형 + 집계 - 직원별 담당 고객 수 포함 조회
-- ──────────────────────────────────────────────────────────
WITH RECURSIVE emp_hier(
    EmployeeId, FirstName, LastName, Title, ReportsTo, lvl
) AS (
    SELECT EmployeeId, FirstName, LastName, Title, ReportsTo, 0 AS lvl
    FROM employees
    WHERE ReportsTo IS NULL

    UNION ALL

    SELECT e.EmployeeId, e.FirstName, e.LastName,
           e.Title, e.ReportsTo, h.lvl + 1
    FROM employees e
    JOIN emp_hier h ON e.ReportsTo = h.EmployeeId
)
SELECT h.lvl        AS 계층레벨,
       h.EmployeeId AS 직원ID,
       SUBSTR('                ', 1, h.lvl * 4)
           || h.FirstName || ' ' || h.LastName AS 직원명,
       h.Title      AS 직책,
       COUNT(c.CustomerId)                     AS 담당고객수,
       ROUND(SUM(i.Total), 2)                  AS 담당매출합계
FROM emp_hier h
LEFT JOIN customers c ON h.EmployeeId = c.SupportRepId
LEFT JOIN invoices  i ON c.CustomerId  = i.CustomerId
GROUP BY h.EmployeeId, h.lvl, h.FirstName, h.LastName, h.Title
ORDER BY h.lvl, h.EmployeeId;


-- ──────────────────────────────────────────────────────────
-- 5-3. 경로(PATH) + 리프(Leaf) 노드 판별
-- ──────────────────────────────────────────────────────────
WITH RECURSIVE emp_path(
    EmployeeId, FirstName, LastName, Title, ReportsTo, lvl, path
) AS (
    SELECT EmployeeId, FirstName, LastName, Title, ReportsTo,
           0,
           FirstName || ' ' || LastName AS path
    FROM employees
    WHERE ReportsTo IS NULL

    UNION ALL

    SELECT e.EmployeeId, e.FirstName, e.LastName,
           e.Title, e.ReportsTo, p.lvl + 1,
           p.path || ' > ' || e.FirstName || ' ' || e.LastName
    FROM employees e
    JOIN emp_path p ON e.ReportsTo = p.EmployeeId
)
SELECT lvl        AS 계층레벨,
       EmployeeId AS 직원ID,
       path       AS 조직경로,
       Title      AS 직책,
       CASE
           WHEN EmployeeId NOT IN (
               SELECT ReportsTo
               FROM employees
               WHERE ReportsTo IS NOT NULL
           ) THEN 'Leaf'
           ELSE 'Branch'
       END AS 노드유형
FROM emp_path
ORDER BY path;


-- ──────────────────────────────────────────────────────────
-- 5-4. 계층형 + UNION ALL - 레벨별 인원 + 전체 합계
-- ──────────────────────────────────────────────────────────
WITH RECURSIVE emp_cte(
    EmployeeId, FirstName, LastName, Title, ReportsTo, lvl
) AS (
    SELECT EmployeeId, FirstName, LastName, Title, ReportsTo, 0
    FROM employees
    WHERE ReportsTo IS NULL

    UNION ALL

    SELECT e.EmployeeId, e.FirstName, e.LastName,
           e.Title, e.ReportsTo, c.lvl + 1
    FROM employees e
    JOIN emp_cte c ON e.ReportsTo = c.EmployeeId
)
SELECT 'Level ' || CAST(lvl AS TEXT) AS 계층레벨,
       COUNT(*)                      AS 직원수
FROM emp_cte
GROUP BY lvl

UNION ALL

SELECT '── 합계', COUNT(*)
FROM emp_cte

ORDER BY 계층레벨;


-- ============================================================
-- [참고] Oracle 계층형 질의 구문 (SQLite 미지원 - 비교용)
-- ============================================================
/*
SELECT LEVEL,
       LPAD(' ', 4*(LEVEL-1)) || EmployeeId         AS 직원ID,
       FirstName || ' ' || LastName                 AS 직원명,
       Title,
       ReportsTo,
       CONNECT_BY_ROOT  FirstName || ' ' || LastName AS 루트직원,
       CONNECT_BY_ISLEAF                             AS 리프여부,
       SYS_CONNECT_BY_PATH(LastName, '/')            AS 경로
FROM   employees
START  WITH ReportsTo IS NULL
CONNECT BY  PRIOR EmployeeId = ReportsTo
ORDER  SIBLINGS BY LastName;
*/

-- ============================================================
-- End of Day03_students_copy.sql
-- ============================================================
