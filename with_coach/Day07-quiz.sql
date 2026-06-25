/* =====================================================================
   Day 07 마케팅 분석 SQL 퀴즈 20문제 (정답 포함)
   - 사용 DB : classicmodels.db  (datasets/classicmodels.db)
   - 테마    : 마케팅·매출·고객·제품 라인 분석
   ===================================================================== */

/* ================================================================
   PART A. 쉬운 문제 (4)
   ================================================================ */

SELECT sqlite_version();


/* ----------------------------------------------------------------
   Q01. [집계] productLine별 등록 제품 수
   -- 마케팅팀: 카탈로그에 제품 라인별 SKU(품목) 수가 필요합니다.
   -- 출력: productLine, product_count (내림차순)
   -- 테이블명: products
   ---------------------------------------------------------------- */
SELECT 
   productLine
   , COUNT(*) AS product_count
FROM products
GROUP BY productLine
ORDER BY product_count DESC
;

/* ----------------------------------------------------------------
   Q02. [GROUP BY] country별 잠재 고객(고객) 수
   -- 글로벌 마케팅: 국가별 고객 규모를 파악합니다.
   -- 출력: country, customer_count (고객 수 내림차순)
   -- 테이블명: customers
   ---------------------------------------------------------------- */
SELECT 
   country
   , COUNT(*) AS customer_count
FROM customers
GROUP BY country
ORDER BY customer_count DESC
;

/* ----------------------------------------------------------------
   Q03. [집계] productLine별 평균 권장소비자가(MSRP)
   -- 가격 정책 검토: 라인별 평균 MSRP를 소수 둘째 자리까지 구하세요.
   -- 출력: productLine, avg_msrp (내림차순)
   -- 테이블명: products
   ---------------------------------------------------------------- */
SELECT 
   productLine
   , AVG(MSRP) AS avg_msrp
FROM products
GROUP BY productLine
ORDER BY avg_msrp DESC
;

/* ----------------------------------------------------------------
   Q04. [WHERE + COUNT] 2004년 주문 건수
   -- 연도별 마케팅 캠페인 성과: 2004년 주문이 몇 건인지 구하세요.
   -- 힌트: strftime('%Y', orderDate)
   -- 출력: orders_in_2004
   -- 테이블명: orders
   ---------------------------------------------------------------- */
SELECT 
   COUNT(*) AS orders_in_2004
FROM orders
WHERE strftime('%Y', orderDate) = '2004'
;

/* ================================================================
   PART B. JOIN 문제 (5)
   ================================================================ */


/* ----------------------------------------------------------------
   Q05. [INNER JOIN] country별 총 주문 금액
   -- 지역 마케팅 예산: 국가별 매출(quantity × priceEach 합) TOP 10
   -- 테이블: customers, orders, orderdetails
   -- 출력: country, total_revenue (내림차순, LIMIT 10)
   -- 테이블명: customers, orders, orderdetails
   ---------------------------------------------------------------- */
SELECT 
   c.country
   , SUM(d.quantityOrdered * d.priceEach) AS total_revenue
FROM customers c
INNER JOIN orders o ON c.customerNumber = o.customerNumber
INNER JOIN orderdetails d ON o.orderNumber = d.orderNumber
GROUP BY c.country
ORDER BY total_revenue DESC
LIMIT 10
;

/* ----------------------------------------------------------------
   Q06. [JOIN + GROUP BY] productLine별 매출 및 판매 수량
   -- 제품 라인 마케팅: 라인별 매출·판매량 비교
   -- 테이블: products, orderdetails
   -- 출력: productLine, total_revenue, total_qty (매출 내림차순)
   -- 테이블명: products, orderdetails
   ---------------------------------------------------------------- */
SELECT 
   p.productLine
   , SUM(d.quantityOrdered * d.priceEach) AS total_revenue
   , SUM(d.quantityOrdered) AS total_qty
FROM products p
INNER JOIN orderdetails d ON d.productCode = p.productCode
GROUP BY p.productLine
ORDER BY total_revenue DESC
;

/* ----------------------------------------------------------------
   Q07. [JOIN] salesRep(영업 담당)별 담당 고객 수·평균 신용한도
   -- 세일즈 마케팅: 담당자별 포트폴리오 규모
   -- 테이블: customers, employees
   -- 출력: employeeNumber, rep_name, customer_count, avg_creditLimit
   -- 정렬: customer_count 내림차순
   -- 테이블명: employees, customers
   ---------------------------------------------------------------- */
SELECT 
   e.employeeNumber
   , (e.firstName || " " || e.lastName) AS rep_name
   , COUNT(c.customerNumber) AS customer_count
   , AVG(c.creditLimit) AS avg_creditLimit
FROM employees e
INNER JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
GROUP BY e.employeeNumber, rep_name
ORDER BY customer_count DESC
;

/* ----------------------------------------------------------------
   Q08. [JOIN] territory(지역)별 고객·주문·매출 요약
   -- 지역 마케팅 KPI: offices.territory 기준
   -- 테이블: offices, employees, customers, orders, orderdetails
   -- 출력: territory, customer_count, order_count, total_revenue
   -- 테이블명: offices, employees, customers, orders, orderdetails
   ---------------------------------------------------------------- */
SELECT 
   o.territory
   , COUNT(DISTINCT c.customerNumber) AS customer_count
   , COUNT(DISTINCT d.orderNumber) AS order_count
   , SUM(d.quantityOrdered * d.priceEach) AS total_revenue
FROM offices o
INNER JOIN employees e ON o.officeCode = e.officeCode
INNER JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
INNER JOIN orders od ON od.customerNumber = c.customerNumber
INNER JOIN orderdetails d ON d.orderNumber = od.orderNumber
GROUP BY o.territory
ORDER BY total_revenue DESC
;

/* ----------------------------------------------------------------
   Q09. [JOIN + HAVING] 'Classic Cars' 라인 제품을 3회 이상 구매한 고객
   -- 타깃 마케팅: 충성 고객 후보군 추출
   -- 테이블: customers, orders, orderdetails, products
   -- 출력: customerNumber, customerName, purchase_count
   -- HAVING purchase_count >= 3
   -- 테이블명: customers, orders, orderdetails, products
   ---------------------------------------------------------------- */
SELECT 
   c.customerNumber
   , c.customerName
   , COUNT(*) AS purchase_count
FROM customers c
INNER JOIN orders o ON o.customerNumber = c.customerNumber
INNER JOIN orderdetails d ON d.orderNumber = o.orderNumber
INNER JOIN products p ON d.productCode = p.productCode
WHERE p.productLine = "Classic Cars"
GROUP BY c.customerNumber, c.customerName
HAVING purchase_count >= 3
ORDER BY purchase_count DESC
;

/* ================================================================
   PART C. 서브쿼리 문제 (5)
   ================================================================ */


/* ----------------------------------------------------------------
   Q10. [WHERE 서브쿼리] 전체 고객 평균 creditLimit 초과 고객
   -- VIP 마케팅 후보: 평균 신용한도보다 높은 고객
   -- 출력: customerNumber, customerName, creditLimit (내림차순)
   -- 테이블명: customers
   ---------------------------------------------------------------- */
SELECT 
   customerNumber
   , customerName
   , creditLimit
FROM customers
WHERE creditLimit > (SELECT AVG(creditLimit) FROM customers)
ORDER BY creditLimit DESC
;

/* ----------------------------------------------------------------
   Q11. [IN 서브쿼리] 2003년과 2004년 모두 주문한 고객
   -- 리텐션 마케팅: 연속 구매 고객 식별 (INTERSECT 대신 IN 2회)
   -- 출력: customerNumber, customerName
   -- 테이블명: customers, orders
   ---------------------------------------------------------------- */
SELECT customerNumber, customerName
FROM customers 
WHERE customerNumber IN (
   SELECT customerNumber FROM orders WHERE strftime('%Y', orderDate) = '2003'
) AND customerNumber IN (
   SELECT customerNumber FROM orders WHERE strftime('%Y', orderDate) = '2004'
)
ORDER BY customerNumber
;

/* ----------------------------------------------------------------
   Q12. [NOT IN] 한 번도 주문하지 않은 고객 (잠재 이탈·미활성)
   -- 윈백(Win-back) 캠페인 대상
   -- 출력: customerNumber, customerName, country
   -- 테이블명: customers, orders
   ---------------------------------------------------------------- */
SELECT customerNumber, customerName, country
FROM customers
WHERE customerNumber NOT IN (
   SELECT DISTINCT customerNumber FROM orders
)
ORDER BY customerNumber
;

/* ----------------------------------------------------------------
   Q13. [FROM 서브쿼리] productLine별 매출 TOP 3
   -- 카테고리 마케팅: 라인별 매출 상위 3개만
   -- 출력: productLine, line_revenue
   -- 테이블명: products, orderdetails
   ---------------------------------------------------------------- */
SELECT 
   productLine
   , SUM(quantityOrdered * priceEach) AS line_revenue
FROM (
   SELECT * FROM products p INNER JOIN orderdetails d ON p.productCode = d.productCode
) dp
GROUP BY productLine
ORDER BY line_revenue DESC
LIMIT 3
;

/* ----------------------------------------------------------------
   Q14. [EXISTS] 'Shipped' 주문 이력이 있는 국가 목록
   -- 배송 완료 경험 국가 → 재구매 캠페인 지역
   -- 출력: country (중복 없이)
   -- 테이블명: customers, orders
   ---------------------------------------------------------------- */
SELECT DISTINCT c.country
FROM customers c
WHERE EXISTS (
   SELECT 1
   FROM orders o
   WHERE c.customerNumber = o.customerNumber AND o.status = 'Shipped'
)
ORDER BY country
;

/* ================================================================
   PART D. 윈도우 함수 (4)
   ================================================================ */


/* ----------------------------------------------------------------
   Q15. [RANK] 고객별 총 결제액 순위 TOP 10
   -- 마케팅 등급: 결제액 기준 VIP 순위
   -- 테이블: customers, payments
   -- 출력: customerNumber, customerName, total_payment, payment_rank
   -- 테이블명: customers, payments
   ---------------------------------------------------------------- */
SELECT    
   customerNumber
   , customerName
   , total_payment
   , payment_rank
FROM (
   SELECT 
      c.customerNumber
      , c.customerName
      , SUM(p.amount) AS total_payment
      , RANK() OVER(ORDER BY SUM(p.amount) DESC) AS payment_rank
   FROM customers c
   INNER JOIN payments p ON c.customerNumber = p.customerNumber
   GROUP BY c.customerNumber
)
WHERE payment_rank <= 10
ORDER BY payment_rank ASC
;

/* ----------------------------------------------------------------
   Q16. [PARTITION BY] 국가 내 creditLimit 순위
   -- 국가별 프리미엄 고객: 같은 country 안에서 신용한도 순위
   -- 출력: country, customerName, creditLimit, country_rank (상위 5국 × 각 3명은 전체 출력 후 LIMIT 생략)
   -- 정렬: country, country_rank
   -- 테이블명: customers
   ---------------------------------------------------------------- */
SELECT
   country
   , customerName
   , creditLimit
   , country_rank
FROM (
   SELECT 
      country
      , customerName
      , creditLimit
      , RANK() OVER(PARTITION BY country ORDER BY creditLimit DESC) AS country_rank
   FROM customers
)
WHERE country_rank <= 3
ORDER BY country, country_rank
;

/* ----------------------------------------------------------------
   Q17. [LAG] 월별 매출 및 전월 대비 증감
   -- 마케팅 트렌드: 월별 주문 매출 MoM(Month-over-Month)
   -- 출력: year_month, monthly_revenue, prev_month_revenue, mom_diff
   -- 테이블명: orders, orderdetails
   ---------------------------------------------------------------- */
SELECT
   year_month
   , monthly_revenue
   , LAG(monthly_revenue, 1) OVER(ORDER BY year_month) AS prev_month_revenue
   , monthly_revenue - LAG(monthly_revenue, 1) OVER(ORDER BY year_month) AS mom_diff
FROM (
   SELECT 
      strftime('%Y%m', o.orderDate) AS year_month
      , SUM(d.quantityOrdered * d.priceEach) AS monthly_revenue
   FROM orders o
   INNER JOIN orderdetails d ON o.orderNumber = d.orderNumber
   GROUP BY year_month
)
ORDER BY year_month
;

/* ----------------------------------------------------------------
   Q18. [SUM OVER] productLine별 매출 비중 (Running ratio)
   -- 포트폴리오 분석: 라인별 매출 + 전체 대비 비율
   -- 출력: productLine, line_revenue, revenue_ratio
   -- 테이블명: products, orderdetails
   ---------------------------------------------------------------- */
SELECT 
   productLine
   , line_revenue
   , line_revenue / SUM(line_revenue) OVER() AS revenue_ratio
FROM (
   SELECT 
      DISTINCT p.productLine
      , SUM(d.quantityOrdered * d.priceEach) AS line_revenue
   FROM products p
   INNER JOIN orderdetails d ON p.productCode = d.productCode
   GROUP BY p.productLine
)
ORDER BY line_revenue DESC
;

/* ----------------------------------------------------------------
   Q19. [NOT EXISTS] 한 번도 판매되지 않은 제품 (재고·프로모션 검토)
   -- orderdetails에 없는 productCode
   -- 출력: productCode, productName, productLine, quantityInStock
   -- 테이블명: products, orderdetails
   ---------------------------------------------------------------- */
SELECT p.productCode, p.productName, p.productLine, p.quantityInStock
FROM products p
WHERE NOT EXISTS (
   SELECT 1
   FROM orderdetails d WHERE p.productCode = d.productCode
)
ORDER BY p.productLine, p.productCode
;

/* ================================================================
   PART E. 매우 어려운 복합 쿼리 (1)
   ================================================================ */


/* ----------------------------------------------------------------
   Q20. [복합] 국가 × productLine 마케팅 대시보드
   -- JOIN + 서브쿼리 + 윈도우 함수 + CTE
   --
   -- 요구사항:
   --   1) 국가·제품라인별 매출(line_revenue) 집계
   --   2) 해당 국가 내 productLine 매출 순위(country_line_rank)
   --   3) 국가 전체 매출(country_total) 대비 비중(pct_of_country)
   --   4) 국가 평균 라인 매출(country_avg_line_rev) 초과 여부(above_avg_flag)
   --   5) country_total 이 전체 국가 평균 초과인 country 만 (마케팅 집중 국가)
   -- 출력: country, productLine, line_revenue, country_line_rank,
   --        pct_of_country, above_avg_flag
   -- 정렬: country, country_line_rank
   -- 테이블명: customers, orders, orderdetails, products
   ---------------------------------------------------------------- */
SELECT country, productLine, line_revenue, country_line_rank, pct_of_country, above_avg_flag
FROM
(
SELECT
   country
   , productLine
   , line_revenue
   , RANK() OVER(PARTITION BY country ORDER BY line_revenue DESC) AS country_line_rank
   , SUM(line_revenue) OVER(PARTITION BY country) AS country_total
   , line_revenue / SUM(line_revenue) OVER(PARTITION BY country) AS pct_of_country
   , AVG(line_revenue) OVER(PARTITION BY country) AS country_avg_line_rev
   , CASE
         WHEN line_revenue > (AVG(line_revenue) OVER(PARTITION BY country)) THEN 'Y'
         ELSE 'N'
      END AS above_avg_flag
FROM (
   SELECT 
      c.country
      , p.productLine
      , SUM(d.quantityOrdered * d.priceEach) AS line_revenue
   FROM customers c
   INNER JOIN orders o ON o.customerNumber = c.customerNumber
   INNER JOIN orderdetails d ON d.orderNumber = o.orderNumber
   INNER JOIN products p ON p.productCode = d.productCode
   GROUP BY c.country, p.productLine
   ORDER BY line_revenue
)
GROUP BY country, line_revenue
)
WHERE country IN (
   SELECT country
    FROM (
        SELECT country,
               SUM(line_revenue) AS country_total
        FROM (
            SELECT 
               c.country
               , p.productLine
               , SUM(d.quantityOrdered * d.priceEach) AS line_revenue
            FROM customers c
            INNER JOIN orders o ON o.customerNumber = c.customerNumber
            INNER JOIN orderdetails d ON d.orderNumber = o.orderNumber
            INNER JOIN products p ON p.productCode = d.productCode
            GROUP BY c.country, p.productLine
            ORDER BY line_revenue
        )
        GROUP BY country
    )
    WHERE country_total > (
        SELECT AVG(cntry_total)
        FROM (
            SELECT SUM(line_revenue) AS cntry_total
            FROM (
               SELECT 
                  c.country
                  , p.productLine
                  , SUM(d.quantityOrdered * d.priceEach) AS line_revenue
               FROM customers c
               INNER JOIN orders o ON o.customerNumber = c.customerNumber
               INNER JOIN orderdetails d ON d.orderNumber = o.orderNumber
               INNER JOIN products p ON p.productCode = d.productCode
               GROUP BY c.country, p.productLine
               ORDER BY line_revenue
            )
            GROUP BY country
        )
    )
)
;

-- ============================================================
-- End of Day07-answers.sql
-- ============================================================


/* ----------------------------------------------------------------
   Q20. [복합] 국가 × productLine 마케팅 대시보드 수정본
   ---------------------------------------------------------------- */
WITH BaseRev AS (
   -- 1단계: 국가(country) 및 제품라인(productLine)별 매출 집계
   SELECT 
      c.country,
      p.productLine,
      SUM(d.quantityOrdered * d.priceEach) AS line_revenue
   FROM customers c
   INNER JOIN orders o ON o.customerNumber = c.customerNumber
   INNER JOIN orderdetails d ON d.orderNumber = o.orderNumber
   INNER JOIN products p ON p.productCode = d.productCode
   GROUP BY c.country, p.productLine
),
CountryAgg AS (
   -- 2단계: 국가별 총매출 (전체 국가의 평균 매출을 구하기 위한 용도)
   SELECT 
      country,
      SUM(line_revenue) AS country_total
   FROM BaseRev
   GROUP BY country
),
WindowedRev AS (
   -- 3단계: 윈도우 함수를 사용해 순위, 비중, 평균 등을 한 번에 계산
   SELECT
      country,
      productLine,
      line_revenue,
      RANK() OVER(PARTITION BY country ORDER BY line_revenue DESC) AS country_line_rank,
      SUM(line_revenue) OVER(PARTITION BY country) AS country_total_window,
      line_revenue / SUM(line_revenue) OVER(PARTITION BY country) AS pct_of_country,
      AVG(line_revenue) OVER(PARTITION BY country) AS country_avg_line_rev
   FROM BaseRev
)
-- 4단계: 최종 출력 및 필터링 (above_avg_flag 생성 및 집중 국가 필터링)
SELECT 
   w.country,
   w.productLine,
   w.line_revenue,
   w.country_line_rank,
   w.pct_of_country,
   CASE 
      WHEN w.line_revenue > w.country_avg_line_rev THEN 'Y'
      ELSE 'N' 
   END AS above_avg_flag
FROM WindowedRev w
-- 국가의 총매출이 '전체 국가의 평균 총매출'보다 큰 곳만 필터링
WHERE w.country_total_window > (SELECT AVG(country_total) FROM CountryAgg)
ORDER BY w.country, w.country_line_rank;

